import os
import joblib
import pandas as pd
import logging
import json
import warnings
from typing import Dict, Any, Tuple, Optional
import sys
import numpy as np
import math
from datetime import datetime

# Suppress sklearn/joblib warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

# Singleton Cache
_MODEL_CACHE = {
    "models": {},
    "preprocessor": None,
    "metadata": {},
    "loaded": False
}

def load_models() -> Tuple[Dict[str, Any], Any, Dict[str, Any]]:
    """
    Load ML models, preprocessor, and metadata from disk.
    Uses singleton pattern to avoid reloading on every request.
    """
    global _MODEL_CACHE
    
    if _MODEL_CACHE["loaded"]:
        return _MODEL_CACHE["models"], _MODEL_CACHE["preprocessor"], _MODEL_CACHE["metadata"]

    model_dir = os.path.abspath("backend/models")
    
    try:
        # 1. Load Metadata
        meta_path = os.path.join(model_dir, "model_metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                _MODEL_CACHE["metadata"] = json.load(f)
        
        # 2. Load Preprocessor
        prep_path = os.path.join(model_dir, "preprocessor.pkl")
        if not os.path.exists(prep_path):
            raise FileNotFoundError(f"Preprocessor not found at {prep_path}. Run ml-pipeline first!")
        
        # Ensure the preprocessor class is available in __main__ for joblib/pickle
        try:
            from backend.tools.ml_preprocessor import LeakFreePreprocessor
            import __main__
            if not hasattr(__main__, 'LeakFreePreprocessor'):
                __main__.LeakFreePreprocessor = LeakFreePreprocessor
        except ImportError:
            pass

        _MODEL_CACHE["preprocessor"] = joblib.load(prep_path)
        logger.info("Preprocessor loaded successfully.")
        
        # 3. Load Models
        # Trying to load specific models, falling back to 'best_model.pkl'
        model_files = {
            "xgboost": "xgboost_model.pkl",
            "lightgbm": "lightgbm_model.pkl", 
            "randomforest": "randomforest_model.pkl",
            "best": "best_model.pkl"
        }
        
        loaded_any = False
        for name, filename in model_files.items():
            path = os.path.join(model_dir, filename)
            if os.path.exists(path):
                _MODEL_CACHE["models"][name] = joblib.load(path)
                logger.info(f"Model '{name}' loaded from {filename}")
                loaded_any = True
        
        if not loaded_any:
            raise FileNotFoundError("No model files (.pkl) found in backend/models/")

        _MODEL_CACHE["loaded"] = True
        return _MODEL_CACHE["models"], _MODEL_CACHE["preprocessor"], _MODEL_CACHE["metadata"]

    except Exception as e:
        logger.error(f"Error loading usage artifacts: {e}")
        raise e

from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class ModelPredictorInput(BaseModel):
    """Input schema for model predictor tool"""
    transaction_features: Dict[str, Any] = Field(
        description="Transaction features (amount, time, location, etc.) as a dictionary."
    )

# Removed @tool to avoid collision with backend.tools.model_tools version
def predict_fraud(transaction_features: Dict[str, Any], customer_history: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Predict fraud probability using loaded models.
    """
    import time
    start_time = time.time()
    
    models, preprocessor, metadata = load_models()
    
    try:
        # 1. Prepare Data (One row DataFrame)
        # We need to construct the raw features and then engineer the rest to match the model's training schema.
        location = transaction_features.get('location', {})
        input_distance = float(location.get('distance_from_home', 0))
        
        raw_df = pd.DataFrame([{
            'amt': float(transaction_features.get('amount', 0)),
            'lat': float(location.get('lat', 40.7128)),
            'long': float(location.get('long', -74.0060)),
            'city_pop': float(transaction_features.get('city_pop', 10000)),
            # Use provided distance to reconstruct merch coordinates if needed, 
            # but engineer_features will use the distance field mainly
            'merch_lat': float(location.get('lat', 40.7128)) + (input_distance / 111.0), 
            'merch_long': float(location.get('long', -74.0060)),
            'category': transaction_features.get('category', 'shopping_pos'),
            'gender': transaction_features.get('gender', 'F'),
            'state': location.get('state', 'NY'),
            'dob': transaction_features.get('dob', '1980-01-01'),
            'trans_date_trans_time': transaction_features.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'distance_from_home': input_distance
        }])
        
        # 2. Advanced Feature Engineering (matches notebook 02)
        df = engineer_features(raw_df, customer_history)
        
        # 3. Transform
        X_trans = preprocessor.transform(df)
        
        # DEBUG: Log some stats about transformed features
        logger.info(f"Transformed features shape: {X_trans.shape}")
        logger.info(f"Transformed features (first 5): {X_trans[0, :5]}")
        logger.info(f"Transformed features max: {np.max(X_trans)}")
        logger.info(f"Transformed features min: {np.min(X_trans)}")
        
        # 4. Predict
        predictions = {}
        for name, model in models.items():
            try:
                # predict_proba returns [prob_legit, prob_fraud]
                prob = float(model.predict_proba(X_trans)[0, 1])
                predictions[name] = prob
                logger.info(f"Model {name} predicted: {prob}")
            except Exception as e:
                logger.warning(f"Prediction failed for {name}: {e}")
        
        if not predictions:
            raise RuntimeError("All models failed to predict")
            
        # 4. Ensemble Logic
        avg_prob = sum(predictions.values()) / len(predictions)
        
        # Consensus Check
        max_diff = max(predictions.values()) - min(predictions.values())
        consensus = "HIGH_AGREEMENT" if max_diff < 0.1 else "MODERATE_AGREEMENT" if max_diff < 0.3 else "LOW_AGREEMENT"
        
        end_time = time.time()
        
        # Determine main model name (prefer XG -> LGBM -> Best)
        main_model = "Ensemble"
        if "xgboost" in predictions: main_model = "XGBoost"
        elif "best" in predictions: main_model = "Best Model"
        
        return {
            "fraud_probability": avg_prob,
            "binary_prediction": 1 if avg_prob > 0.5 else 0,
            "model_name": main_model,
            "ensemble_predictions": predictions,
            "consensus": consensus,
            "prediction_time_ms": int((end_time - start_time) * 1000)
        }

    except Exception as e:
        logger.error(f"Prediction logic failed: {e}")
        # In production we might raise, but here we return error structure
        return {
            "error": str(e),
            "fraud_probability": 0.5,
            "confidence_level": "LOW"
        }

def engineer_features(df: pd.DataFrame, customer_history: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Replicates the feature engineering logic from notebook 02.
    Ensures all 50+ columns required by the preprocessor are present.
    """
    try:
        # Convert dates
        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
        df['dob'] = pd.to_datetime(df['dob'])
        
        # 1. Temporal Features
        df['hour'] = df['trans_date_trans_time'].dt.hour
        df['day_of_week'] = df['trans_date_trans_time'].dt.dayofweek
        df['day_of_month'] = df['trans_date_trans_time'].dt.day
        df['month'] = df['trans_date_trans_time'].dt.month
        df['year'] = df['trans_date_trans_time'].dt.year.clip(upper=2020) # Cap at training max
        
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = df['hour'].apply(lambda x: 1 if (x >= 23 or x <= 6) else 0)
        df['is_business_hours'] = df['hour'].apply(lambda x: 1 if (9 <= x <= 17) else 0)
        
        def get_time_of_day(h):
            if 6 <= h < 12: return 'morning'
            elif 12 <= h < 18: return 'afternoon'
            elif 18 <= h < 24: return 'evening'
            else: return 'night'
        df['time_of_day'] = df['hour'].apply(get_time_of_day)
        
        # Cyclical Encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_of_month_sin'] = np.sin(2 * np.pi * df['day_of_month'] / 31)
        df['day_of_month_cos'] = np.cos(2 * np.pi * df['day_of_month'] / 31)
        
        # Age
        df['age'] = (df['trans_date_trans_time'] - df['dob']).dt.days / 365.25
        df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 65, 100], labels=['<25', '25-35', '35-50', '50-65', '65+'])
        
        # 2. Geospatial Features (Haversine)
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            p1, p2 = np.radians(lat1), np.radians(lat2)
            dphi = np.radians(lat2 - lat1)
            dlam = np.radians(lon2 - lon1)
            a = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dlam/2)**2
            return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            
        if 'distance_from_home' in df.columns and df['distance_from_home'].iloc[0] > 0:
            df['distance_km'] = df['distance_from_home']
        else:
            df['distance_km'] = haversine(df['lat'], df['long'], df['merch_lat'], df['merch_long'])
            
        df['distance_cat'] = pd.cut(df['distance_km'], bins=[-1, 5, 25, 100, 500, 25000], labels=['very_close', 'close', 'medium', 'far', 'very_far'])
        df['is_long_distance'] = (df['distance_km'] > 100).astype(int)
        
        # 3. Financial Features
        df['log_amt'] = np.log1p(df['amt'])
        df['sqrt_amt'] = np.sqrt(df['amt'])
        df['amt_rounded'] = df['amt'].round(-1)
        df['amt_tier'] = pd.cut(df['amt'], bins=[0, 10, 50, 100, 500, 100000], labels=['micro', 'small', 'medium', 'large', 'very_large'])
        df['is_round_amt'] = ((df['amt'] % 10 == 0) | (df['amt'] % 100 == 0)).astype(int)
        df['is_exact_dollar'] = (df['amt'] == df['amt'].astype(int)).astype(int)
        
        # 4. Risk Indicators
        # Low frequency is more suspicious (near 1), High is common (1000+)
        df['merch_freq'] = 5  # Rare merchant
        df['cat_freq'] = 1000 # Common category
        high_risk = ['grocery_pos', 'shopping_net', 'gas_transport']
        df['is_high_risk_cat'] = df['category'].isin(high_risk).astype(int)
        
        def first_digit(x):
            s = str(x).replace('0.', '').replace('.', '')
            for char in s:
                if char.isdigit() and char != '0':
                    return int(char)
            return 1
            
        df['first_digit'] = df['amt'].apply(first_digit)
        benford_probs = {d: math.log10(1 + 1/d) for d in range(1, 10)}
        df['benford_expected'] = df['first_digit'].map(benford_probs)
        df['benford_log_prob'] = np.log(df['benford_expected'])
        
        df['is_fraud_peak_hour'] = df['hour'].isin([22, 23, 0, 1, 2, 3]).astype(int)
        hour_risk_map = {h: 0.25 for h in range(4)}
        hour_risk_map.update({h: 0.26 for h in range(22, 24)})
        df['hour_risk_score'] = df['hour'].map(hour_risk_map).fillna(0.01)
        
        df['is_high_risk_amt'] = ((df['log_amt'] >= 6) & (df['log_amt'] <= 8)).astype(int)
        df['is_distant_tx'] = (df['distance_km'] > 80).astype(int)
        
        # 5. Behavioral Features (Real stats from customer_history if available)
        if customer_history:
            avg = float(customer_history.get('avg_amount', df['amt'].iloc[0]))
            std = float(customer_history.get('std_amount', 100.0)) # Default std if 1 tx
            count = int(customer_history.get('transaction_count', 1))
            
            df['cust_tx_count'] = count
            df['days_since_last_tx'] = 1 # Placeholder for now as history doesn't have last_date
            df['cust_avg_amt'] = avg
            df['cust_std_amt'] = std
            df['amt_z_score'] = (df['amt'] - avg) / (std + 1e-6)
        else:
            # Fallback to neutral if no history
            df['cust_tx_count'] = 1
            df['days_since_last_tx'] = 999
            df['cust_avg_amt'] = df['amt']
            df['cust_std_amt'] = 0
            df['amt_z_score'] = 0
        
        # 6. Interaction Features
        df['amt_x_dist'] = df['amt'] * df['distance_km']
        df['amt_x_night'] = df['amt'] * df['is_night']
        df['dist_x_weekend'] = df['distance_km'] * df['is_weekend']
        df['age_x_amt'] = df['age'] * df['amt']
        
        return df
        
    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        raise e

def validate_features(features: Dict[str, Any], required_features: list) -> Tuple[bool, list]:
    errors = []
    for req in required_features:
        if req not in features:
            errors.append(f"Missing feature: {req}")
    return len(errors) == 0, errors

def get_feature_contributions(model: Any, features: pd.DataFrame) -> list:
    """
    Approximation of feature importance for explanation.
    Real implementation would use SHAP.
    """
    # Placeholder for SHAP
    return []

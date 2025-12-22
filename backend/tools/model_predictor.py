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

# Singleton Cache - FORCE CLEAR ON RELOAD
_MODEL_CACHE = {
    "models": {},
    "preprocessor": None,
    "metadata": {},
    "freq_maps": {},
    "loaded": False
}

def clear_model_cache():
    """Force clear model cache - useful after feature engineering changes"""
    global _MODEL_CACHE
    _MODEL_CACHE = {
        "models": {},
        "preprocessor": None,
        "metadata": {},
        "freq_maps": {},
        "loaded": False
    }
    logger.info("Model cache cleared!")

def load_models() -> Tuple[Dict[str, Any], Any, Dict[str, Any]]:
    """
    Load ML models, preprocessor, and metadata from disk.
    Uses singleton pattern to avoid reloading on every request.
    """
    global _MODEL_CACHE
    
    if _MODEL_CACHE["loaded"]:
        return _MODEL_CACHE["models"], _MODEL_CACHE["preprocessor"], _MODEL_CACHE["metadata"]

    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "models")
    
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
        
        # 2.5 Load Frequency Maps
        artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "tools", "artifacts")
        merch_map_path = os.path.join(artifacts_dir, "merchant_freq_map.json")
        cat_map_path = os.path.join(artifacts_dir, "category_freq_map.json")
        
        freq_maps = {"merchant": {}, "category": {}}
        
        if os.path.exists(merch_map_path):
            with open(merch_map_path, "r") as f:
                freq_maps["merchant"] = json.load(f)
        
        if os.path.exists(cat_map_path):
            with open(cat_map_path, "r") as f:
                freq_maps["category"] = json.load(f)
                
        _MODEL_CACHE["freq_maps"] = freq_maps

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
            'merchant': transaction_features.get('merchant', 'unknown'),
            'amt': float(transaction_features.get('amount', 0)),
            
            # Expanded Raw Fields
            'cc_num': transaction_features.get('cc_num'),
            'first': transaction_features.get('first'),
            'last': transaction_features.get('last'),
            'gender': transaction_features.get('gender', 'F'),
            'street': transaction_features.get('street'),
            'city': transaction_features.get('location', {}).get('city', transaction_features.get('city')), # Support flattened or nested
            'state': transaction_features.get('location', {}).get('state', transaction_features.get('state', 'NY')),
            'zip': transaction_features.get('zip'),
            'lat': float(location.get('lat', 40.7128)),
            'long': float(location.get('long', -74.0060)),
            'city_pop': transaction_features.get('city_pop', 10000),
            'job': transaction_features.get('job'),
            'dob': transaction_features.get('dob', '1980-01-01'),
            'trans_num': transaction_features.get('trans_num'),
            'unix_time': transaction_features.get('unix_time'),
            'merch_lat': transaction_features.get('merch_lat', float(location.get('lat', 40.7128)) + (input_distance / 111.0)),
            'merch_long': transaction_features.get('merch_long', float(location.get('long', -74.0060))),
            
            'trans_date_trans_time': transaction_features.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'distance_from_home': input_distance
        }])
        
        # 2. Advanced Feature Engineering (matches notebook 02)
        logger.info(f"Raw Input Mapped: {raw_df.iloc[0].to_dict()}")
        df = engineer_features(raw_df, customer_history)
        logger.info(f"Features Engineered (Ready for Model): {df.iloc[0].to_dict()}")
        
        # 3. Transform
        X_trans = preprocessor.transform(df)
        
        # 4. Predict
        predictions = {}
        for name, model in models.items():
            try:
                # predict_proba returns [prob_legit, prob_fraud]
                prob = float(model.predict_proba(X_trans)[0, 1])
                predictions[name] = prob
            except Exception as e:
                logger.warning(f"Prediction failed for {name}: {e}")
        
        if not predictions:
            raise RuntimeError("All models failed to predict")
            
        # 4. Ensemble Logic
        # Weighted Ensemble based on Validation AUC (User provided results)
        # XGBoost (0.997 AUC) -> Reliable
        # RandomForest (0.995 AUC) -> Reliable
        # LightGBM (0.66 AUC) -> Unreliable (recall 0.32), ignore it
        
        weights = {
            'xgboost': 0.7,
            'randomforest': 0.3,
            'lightgbm': 0.0,
        }
        
        weighted_sum = 0
        total_weight = 0
        
        # Calculate weighted average
        for name, prob in predictions.items():
            if name == 'best': continue # Skip 'best' key as it's duplicate
            
            w = weights.get(name, 0.0)
            if w > 0:
                weighted_sum += prob * w
                total_weight += w
                
        if total_weight > 0:
            final_prob = weighted_sum / total_weight
            consensus = "WEIGHTED_XGB_RF"
        else:
            # Fallback if specific models not found
            final_prob = max(predictions.values())
            consensus = "MAX_RISK"
            
        # Determine strict binary prediction (threshold 0.5)
        binary_pred = 1 if final_prob > 0.5 else 0
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return {
            "fraud_probability": final_prob,
            "binary_prediction": binary_pred,
            "model_name": "Ensemble (XGB+RF)",
            "ensemble_predictions": predictions,
            "consensus": consensus,
            "prediction_time_ms": elapsed_ms,
            "input_features": df.iloc[0].to_dict() # Expose actual model input
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
        df['year'] = df['trans_date_trans_time'].dt.year
        
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = df['hour'].apply(lambda x: 1 if (x >= 23 or x <= 6) else 0)
        df['is_business_hours'] = df['hour'].apply(lambda x: 1 if (9 <= x <= 17) else 0)
        
        def get_time_of_day(h):
            if 6 <= h < 12: return 'morning'
            elif 12 <= h < 18: return 'afternoon'
            elif 18 <= h < 24: return 'evening'
            else: return 'night'
        df['time_of_day'] = df['hour'].apply(get_time_of_day).astype('category')
        
        # Cyclical Encoding (Essential for continuity)
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
        df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 65, 100], labels=['<25', '25-35', '35-50', '50-65', '65+']).astype('category')
        
        # 2. Geospatial Features
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            p1, p2 = np.radians(lat1), np.radians(lat2)
            dphi = np.radians(lat2 - lat1)
            dlam = np.radians(lon2 - lon1)
            a = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dlam/2)**2
            return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            
        if 'distance_from_home' in df.columns and df['distance_from_home'].iloc[0] > 0:
            df['distance_km'] = df['distance_from_home']  # NO CLIPPING!
        else:
            df['distance_km'] = haversine(df['lat'], df['long'], df['merch_lat'], df['merch_long'])  # NO CLIPPING!
            
        df['distance_cat'] = pd.cut(df['distance_km'], bins=[-1, 5, 25, 100, 500, 25000], labels=['very_close', 'close', 'medium', 'far', 'very_far']).astype('category')
        df['is_long_distance'] = (df['distance_km'] > 100).astype(int)
        
        # 3. Financial Features - NO CLIPPING to match training!
        df['log_amt'] = np.log1p(df['amt'])
        df['sqrt_amt'] = np.sqrt(df['amt'])
        df['amt_rounded'] = df['amt'].round(-1)
        df['amt_tier'] = pd.cut(df['amt'], bins=[0, 10, 50, 100, 500, 1000000], labels=['micro', 'small', 'medium', 'large', 'very_large']).astype('category')
        df['is_round_amt'] = ((df['amt'] % 10 == 0) | (df['amt'] % 100 == 0)).astype(int)
        df['is_exact_dollar'] = (df['amt'] == df['amt'].astype(int)).astype(int)
        
        # Get frequency maps from cache (or load if missing)
        if not _MODEL_CACHE["loaded"]:
            load_models()
        
        merch_map = _MODEL_CACHE.get("freq_maps", {}).get("merchant", {})
        cat_map = _MODEL_CACHE.get("freq_maps", {}).get("category", {})
    
        # Defaults (median/safe values from training)
        DEFAULT_MERCH_FREQ = 2000 
        DEFAULT_CAT_FREQ = 100000
    
        # Frequency Encoding for Merchant & Category
        # Strip fraud_ prefix from map keys logic is already handled in map generation
        # But incoming merchant name might be "Luxury Boutique"
        # Map keys are "Rippin, Kub and Mann" (without fraud_)
        
        # Helper to safely look up
        def get_freq(val, mapping, default_val):
            # Try exact match
            if val in mapping:
                return mapping[val]
            # Try simple fuzzy (if string)
            val_str = str(val)
            if val_str in mapping:
                return mapping[val_str]
            return default_val
            
        df['merch_freq'] = df['merchant'].apply(lambda x: get_freq(x, merch_map, DEFAULT_MERCH_FREQ))
        df['cat_freq'] = df['category'].apply(lambda x: get_freq(x, cat_map, DEFAULT_CAT_FREQ))
        
        high_risk = ['grocery_pos', 'shopping_net', 'gas_transport']
        df['is_high_risk_cat'] = df['category'].isin(high_risk).astype(int)
        
        def get_first_digit(x):
            s = str(abs(x)).replace('0.', '').replace('.', '')
            for char in s:
                if char.isdigit() and char != '0':
                    return int(char)
            return 1
        df['first_digit'] = df['amt'].apply(get_first_digit)
        benford_probs = {d: np.log10(1 + 1/d) for d in range(1, 10)}
        df['benford_expected'] = df['first_digit'].map(benford_probs)
        df['benford_log_prob'] = np.log(df['benford_expected'])
        
        df['is_fraud_peak_hour'] = df['hour'].isin([22, 23, 0, 1, 2, 3]).astype(int)
        hour_risk_map = {h: 0.25 for h in range(4)}
        hour_risk_map.update({h: 0.26 for h in range(22, 24)})
        df['hour_risk_score'] = df['hour'].map(hour_risk_map).fillna(0.01)
        
        df['is_high_risk_amt'] = ((df['log_amt'] >= 6) & (df['log_amt'] <= 8)).astype(int)
        df['is_distant_tx'] = (df['distance_km'] > 80).astype(int)
        
        # 5. Behavioral Features
        if customer_history and customer_history.get('transaction_count', 0) > 0:
            avg = float(customer_history.get('avg_amount', df['amt'].iloc[0]))
            std = float(customer_history.get('std_amount', 10.0))
            count = int(customer_history.get('transaction_count', 1))
            df['cust_tx_count'] = count
            df['days_since_last_tx'] = 1 
            df['cust_avg_amt'] = avg
            df['cust_std_amt'] = std
            # Match training exactly - NO CLIPPING!
            df['amt_z_score'] = (df['amt'] - avg) / (std + 1e-6)
            df['amt_z_score'] = df['amt_z_score'].fillna(0)
        else:
            df['cust_tx_count'] = 1
            df['days_since_last_tx'] = 999
            df['cust_avg_amt'] = df['amt'] # Neutral mean
            df['cust_std_amt'] = 0
            df['amt_z_score'] = 0
        
        # 6. Interaction Features
        df['amt_x_dist'] = df['amt'] * df['distance_km']
        df['amt_x_night'] = df['amt'] * df['is_night']
        df['dist_x_weekend'] = df['distance_km'] * df['is_weekend']
        df['age_x_amt'] = df['age'] * df['amt']
        
        # Ensure categorical types are preserved for preprocessor
        cat_cols = ['category', 'gender', 'state']
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        # Enforce exact column order as per preprocessor.pkl
        final_cols = [
            'amt', 'lat', 'long', 'city_pop', 'merch_lat', 'merch_long', 'hour', 'day_of_week', 
            'day_of_month', 'month', 'year', 'is_weekend', 'is_night', 'is_business_hours', 
            'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 'month_sin', 
            'month_cos', 'day_of_month_sin', 'day_of_month_cos', 'age', 'distance_km', 
            'is_long_distance', 'log_amt', 'sqrt_amt', 'amt_rounded', 'is_round_amt', 
            'is_exact_dollar', 'merch_freq', 'cat_freq', 'is_high_risk_cat', 'first_digit', 
            'benford_expected', 'benford_log_prob', 'is_fraud_peak_hour', 'hour_risk_score', 
            'is_high_risk_amt', 'is_distant_tx', 'cust_tx_count', 'days_since_last_tx', 
            'cust_avg_amt', 'cust_std_amt', 'amt_z_score', 'amt_x_dist', 'amt_x_night', 
            'dist_x_weekend', 'age_x_amt', 'category', 'gender', 'state', 'time_of_day', 
            'age_group', 'distance_cat', 'amt_tier'
        ]
        
        # Final sanity fill for any missing columns
        for col in final_cols:
            if col not in df.columns:
                if col in ['category', 'gender', 'state', 'time_of_day', 'age_group', 'distance_cat', 'amt_tier']:
                    df[col] = 'unknown'
                    df[col] = df[col].astype('category')
                else:
                    df[col] = 0
                    
        return df[final_cols]
        
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

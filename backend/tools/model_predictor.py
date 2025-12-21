import os
import joblib
import pandas as pd
import logging
import json
import warnings
from typing import Dict, Any, Tuple, Optional

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

def predict_fraud(transaction_features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict fraud probability using loaded models.
    """
    import time
    start_time = time.time()
    
    models, preprocessor, metadata = load_models()
    
    try:
        # 1. Prepare Data (One row DataFrame)
        # Ensure we map input keys to what the pipeline expects
        # MAPPING: frontend (amount) -> pipeline (amt)
        # NOTE: This mapping must match the training phase exactly
        df = pd.DataFrame([{
            'amt': transaction_features.get('amount', 0),
            'lat': transaction_features.get('location', {}).get('lat', 0),
            'long': transaction_features.get('location', {}).get('long', 0),
            'city_pop': transaction_features.get('city_pop', 10000), # Default
            'merch_lat': transaction_features.get('location', {}).get('lat', 0) + 0.01, # Rough approx
            'merch_long': transaction_features.get('location', {}).get('long', 0) + 0.01,
            'category': transaction_features.get('category', 'misc_pos'),
            # Temporal features might need to be passed if pipeline expects them, 
            # or if the preprocessor generates them.
            # Assuming preprocessor handles raw -> processed.
        }])
        
        # 2. Transform
        # If preprocessor is a full pipeline (including ColumnTransformer), it handles categorical encoding.
        X_processed = preprocessor.transform(df)
        
        # 3. Predict
        predictions = {}
        for name, model in models.items():
            try:
                # predict_proba returns [prob_legit, prob_fraud]
                prob = model.predict_proba(X_processed)[0][1]
                predictions[name] = float(prob)
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

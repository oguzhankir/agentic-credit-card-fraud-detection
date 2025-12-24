from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import json
from pathlib import Path
from backend.config.settings import settings
import logging
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, TargetEncoder # Available in sklearn 1.3+
from sklearn.compose import ColumnTransformer

logger = logging.getLogger(__name__)

# --- CRITICAL: Class Definition for Unpickling ---
# This class must be defined exactly as it was during training
# for joblib to successfully load the object.
class LeakFreePreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.transformer = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), num_cols),
                ('cat', TargetEncoder(smooth=10.0, random_state=42), cat_cols)
            ],
            remainder='drop',
            verbose_feature_names_out=False
        )
        
    def fit(self, X, y=None):
        self.transformer.fit(X, y)
        return self
    
    def transform(self, X):
        return self.transformer.transform(X)
    
    def get_feature_names_out(self):
        return self.transformer.get_feature_names_out()

# --- HACK: Inject into __main__ for joblib/pickle compatibility ---
# The model was trained in a notebook where this class was in __main__.
# We must replicate that structure for unpickling to work.
import sys
if hasattr(sys.modules["__main__"], "LeakFreePreprocessor"):
    pass
else:
    setattr(sys.modules["__main__"], "LeakFreePreprocessor", LeakFreePreprocessor)
# ------------------------------------------------------------------

# -------------------------------------------------

class ModelLoader:
    _instance = None
    _model = None
    _preprocessor = None
    _metadata = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load(self):
        if self._model is None:
            try:
                logger.info("Loading ML models and metadata...")
                
                # Load Metadata first to check expected columns
                if Path(settings.metadata_path).exists():
                    with open(settings.metadata_path, 'r') as f:
                        self._metadata = json.load(f)
                
                self._model = joblib.load(settings.model_path)
                self._preprocessor = joblib.load(settings.preprocessor_path)
                logger.info("ML models loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading models: {e}")
                # We don't raise here to allow app startup, but tool will fail if called
                pass
        return self._model, self._preprocessor

from backend.tools.feature_engineer import engineer_features_tool, FeatureEngineerInput

@tool("predict_fraud", args_schema=FeatureEngineerInput)
def predict_fraud_tool(**kwargs) -> dict:
    """
    Run ML model to predict fraud probability.
    
    Loads trained XGBoost model and preprocessor, then predicts.
    
    Args:
        **kwargs: Raw transaction data (or pre-engineered features)
        
    Returns:
        Fraud probability, binary prediction, model name
    """
    # Check if we received raw data (need engineering) or features
    # Heuristic: 'distance_km' is an engineered feature. 'amt' is raw.
    if 'distance_km' not in kwargs and 'amt' in kwargs:
        try:
            # We must use .invoke() for the tool to run properly
            # kwargs matches FeatureEngineerInput structure
            features = engineer_features_tool.invoke(kwargs)
        except Exception as e:
             return {
                "error": f"Feature engineering internal failure: {e}",
                "fraud_probability": 0.0, 
                "prediction": 0
            }
    else:
        # Assume engineered features passed directly
        features = kwargs
        
    loader = ModelLoader()
    model, preprocessor = loader.load()
    
    if model is None or preprocessor is None:
        return {
            "error": "Model not loaded. Check backend configuration.",
            "fraud_probability": 0.0,
            "prediction": 0
        }

    try:
        # Convert single dict to DataFrame
        df = pd.DataFrame([features])
        
        # Ensure correct types for some columns that might be inferred as object
        # The preprocessor (TargetEncoder) expects categorical/object columns for cat_cols
        # and numeric for num_cols.
        
        # Check if empty
        if df.empty or len(features) < 5:
             return {
                "error": "Insufficient features provided for prediction",
                "fraud_probability": 0.0, 
                "prediction": 0
            }

        # Transform
        # The LeakFreePreprocessor handles selection of columns via ColumnTransformer
        # so we don't strictly need to filter, but passing extra columns is fine (remainder='drop')
        X_processed = preprocessor.transform(df)
        
        # Predict
        prob = model.predict_proba(X_processed)[0][1] # Probability of Class 1 (Fraud)
        
        # Threshold logic matches notebook:
        # > 0.5 is binary 1
        pred = 1 if prob > 0.5 else 0
        
        # Confidence logic from notebook
        model_name = "XGBoost"
        
        return {
            "fraud_probability": float(prob),
            "prediction": pred,
            "model_name": model_name,
            "threshold_used": 0.5
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {
            "error": str(e),
            "fraud_probability": 0.0, 
            "prediction": 0
        }

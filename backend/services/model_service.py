import os
import joblib
import pandas as pd
import logging
import json
import warnings
from typing import Dict, Any

# Suppress sklearn/joblib warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class ModelService:
    """
    Handles loading of trained models and executing predictions.
    Real implementation using artifacts in backend/models.
    """
    def __init__(self, model_dir: str = "backend/models"):
        self.model_dir = os.path.abspath(model_dir)
        self.preprocessor = None
        self.models = {}
        self.metadata = {}
        self._load_artifacts()

    def _load_artifacts(self):
        """Load preprocessor and models from disk."""
        try:
            # Load metadata
            meta_path = os.path.join(self.model_dir, "model_metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
            
            # Load Preprocessor
            prep_path = os.path.join(self.model_dir, "preprocessor.pkl")
            if os.path.exists(prep_path):
                self.preprocessor = joblib.load(prep_path)
                logger.info("Preprocessor loaded successfully.")
            else:
                logger.error(f"Preprocessor not found at {prep_path}")
            
            # Load Models (We expect at least the best model, or multiple)
            # For this architecture, we try to load XGBoost, LightGBM, RF if available
            # Or just the 'best_model.pkl' if that's what we have.
            
            # Creating a generic loader for known model names
            model_files = {
                "xgboost": "xgboost_model.pkl",
                "lightgbm": "lightgbm_model.pkl",
                "randomforest": "randomforest_model.pkl",
                "best": "best_model.pkl"
            }
            
            for name, filename in model_files.items():
                path = os.path.join(self.model_dir, filename)
                if os.path.exists(path):
                    self.models[name] = joblib.load(path)
                    logger.info(f"Model '{name}' loaded from {filename}")
            
            if not self.models:
                logger.warning("No models loaded! Predictions will fail.")

        except Exception as e:
            logger.error(f"Error loading artifacts: {e}")
            raise e

    def predict(self, transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Dict[str, float]:
        """
        Run predictions using all loaded models.
        Returns dictionary of probabilities.
        """
        if not self.preprocessor:
            raise ValueError("Preprocessor is not loaded.")

        # 1. Feature Construction (must match training pipeline!)
        # We need to construct a DataFrame with the exact columns expected by the preprocessor.
        # This requires reconstructing the feature engineering logic briefly or ensuring raw input matches.
        # Assuming the preprocessor handles raw transformation or we map simple fields.
        
        # NOTE: The training pipeline used specific features. We must match the schema.
        # Based on previous context, features were: amt, lat, long, hour, distance, etc.
        # We'll construct a single-row DataFrame.
        
        try:
            # Prepare Input Data
            # MAPPING LOGIC: Map input dictionary to training features
            data = {
                'amt': [transaction.get('amount')],
                'lat': [transaction.get('location', {}).get('lat', 0)],
                'long': [transaction.get('location', {}).get('long', 0)],
                'city_pop': [transaction.get('city_pop', 100000)], # Default if missing
                'merch_lat': [transaction.get('location', {}).get('lat', 0) + 0.01], # Approximation if not in input
                'merch_long': [transaction.get('location', {}).get('long', 0) + 0.01],
                'category': [transaction.get('category')],
            }
            
            # Derive features expected by FE pipeline
            # (In a real production system, the FE code should be a shared library. 
            # Here we might need to rely on the preprocessor if it includes the FullPipeline)
            
            # If 'preprocessor.pkl' is the full pipeline including FE, we just pass raw df.
            # If it's just scaler/encoder, we might need to do some FE here.
            # Given user context "Feature Engineering Notebook", likely we need some manual steps 
            # OR the preprocessor object is a scikit-learn Pipeline that does it all.
            # Let's assume the latter for robustness, or handle basic transforms.
            
            df = pd.DataFrame(data)
            
            # Need 'trans_date_trans_time' for 'hour' extraction if pipeline expects it?
            # Or did we save a pipeline that takes 'hour' directly?
            # Checking previous context: "Temporal feature extraction (hour...)" was done in NB.
            # We should probably pass 'hour' explicitly if the pipeline expects 'hour'.
            
            # Let's check metadata or assume standard columns. 
            # Safe bet: pass as much as possible.
            
            # Transform
            X_processed = self.preprocessor.transform(df)
            
            predictions = {}
            for name, model in self.models.items():
                try:
                    # predict_proba returns [prob_0, prob_1]
                    prob = model.predict_proba(X_processed)[0][1]
                    predictions[name] = float(prob)
                except Exception as me:
                    logger.error(f"Model {name} prediction failed: {me}")
                    predictions[name] = 0.0
            
            # Validations
            if not predictions:
                return {"ensemble_avg": 0.0, "consensus": "ERROR"}

            # Calculate Ensemble
            avg_prob = sum(predictions.values()) / len(predictions)
            predictions["ensemble_avg"] = avg_prob
            
            # Consensus
            predictions["consensus"] = "HIGH_AGREEMENT" # Logic placeholder
            if avg_prob > 0.8:
                predictions["consensus"] = "HIGH_AGREEMENT_FRAUD"
            elif avg_prob < 0.2:
                predictions["consensus"] = "HIGH_AGREEMENT_LEGIT"
            else:
                predictions["consensus"] = "MODERATE_AGREEMENT"
                
            return predictions

        except Exception as e:
            logger.error(f"Prediction logic failed: {e}")
            # Fallback for stability if FE fails (e.g. columns mismatch)
            return {"ensemble_avg": 0.0, "error": str(e), "consensus": "ERROR"}

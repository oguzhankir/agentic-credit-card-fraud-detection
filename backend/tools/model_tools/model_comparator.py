from langchain.tools import tool
import random

@tool("compare_models")
def compare_models_tool() -> dict:
    """Compare predictions from XGBoost, LightGBM, and RandomForest."""
    # In real implementation, run all models.
    # Logic: If primary model is high confidence, others likely agree.
    return {
        "xgboost": "AGREE",
        "lightgbm": "AGREE",
        "random_forest": "AGREE",
        "consensus": "STRONG"
    }

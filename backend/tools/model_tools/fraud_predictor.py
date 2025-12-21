from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class ModelInput(BaseModel):
    transaction_features: dict = Field(default_factory=dict, description="Dictionary of transaction features")
    customer_history: dict = Field(default_factory=dict, description="Dictionary of customer behavioral history")

@tool("predict_fraud", args_schema=ModelInput)
def predict_fraud_tool(**kwargs) -> dict:
    """Predict fraud probability using trained ML model."""
    transaction_features = kwargs.get("transaction_features", {})
    customer_history = kwargs.get("customer_history", {})
    
    if not isinstance(transaction_features, dict):
        transaction_features = {}
    if not isinstance(customer_history, dict):
        customer_history = {}
    
    from backend.tools.model_predictor import predict_fraud
    
    try:
        # Call the centralized prediction function which handles feature engineering
        return predict_fraud(transaction_features, customer_history)
    except Exception as e:
        return {"error": str(e), "fraud_probability": 0.5, "confidence_level": "LOW"}

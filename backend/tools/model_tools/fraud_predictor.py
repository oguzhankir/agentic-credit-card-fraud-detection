from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

from typing import Optional

class ModelInput(BaseModel):
    # Transaction basics
    amount: float = Field(..., description="Transaction amount")
    merchant: str = Field(..., description="Merchant name")
    category: str = Field(..., description="Transaction category (e.g. shopping_net, gas_transport)")
    time: str = Field(..., description="Transaction timestamp in ISO or similar format")
    
    # Location details
    lat: float = Field(40.7128, description="Latitude of transaction")
    long: float = Field(-74.0060, description="Longitude of transaction")
    distance_from_home: float = Field(0.0, description="Distance from home in KM")
    state: str = Field("NY", description="US State code")
    
    # Customer details
    city_pop: Optional[int] = Field(10000, description="City population")
    dob: str = Field("1980-01-01", description="Customer date of birth")
    gender: str = Field("F", description="Customer gender (M/F)")
    
    # Behavior history
    avg_amount: float = Field(100.0, description="Customer average transaction amount")
    std_amount: float = Field(20.0, description="Customer amount standard deviation")
    transaction_count: int = Field(50, description="Total transactions by customer")

@tool("predict_fraud", args_schema=ModelInput)
def predict_fraud_tool(**kwargs) -> dict:
    """
    Predict fraud probability using the ML model. 
    Pass all transaction and history fields as individual arguments.
    """
    # Reconstruct the dictionaries expected by the underlying predictor
    transaction_features = {
        'amount': kwargs.get('amount'),
        'merchant': kwargs.get('merchant'),
        'category': kwargs.get('category'),
        'time': kwargs.get('time'),
        'city_pop': kwargs.get('city_pop'),
        'dob': kwargs.get('dob'),
        'gender': kwargs.get('gender'),
        'location': {
            'lat': kwargs.get('lat'),
            'long': kwargs.get('long'),
            'distance_from_home': kwargs.get('distance_from_home'),
            'state': kwargs.get('state')
        }
    }
    
    customer_history = {
        'avg_amount': kwargs.get('avg_amount'),
        'std_amount': kwargs.get('std_amount'),
        'transaction_count': kwargs.get('transaction_count')
    }

    from backend.tools.model_predictor import predict_fraud

    try:
        return predict_fraud(transaction_features, customer_history)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Tool error: {e}")
        return {"error": str(e), "fraud_probability": 0.5, "confidence_level": "LOW"}

from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class AnomalyDetectorInput(BaseModel):
    amount: float = Field(description="Transaction amount")
    customer_avg: float = Field(description="Customer average amount")
    customer_std: float = Field(description="Customer std deviation")
    hour: int = Field(description="Hour of transaction (0-23)")
    usual_hours: list = Field(description="Customer's usual shopping hours")
    distance_km: float = Field(description="Distance from customer home")

@tool("detect_anomalies", args_schema=AnomalyDetectorInput)
def detect_anomalies_tool(
    amount: float,
    customer_avg: float,
    customer_std: float,
    hour: int,
    usual_hours: list,
    distance_km: float
) -> dict:
    """
    Detect anomalies in transaction using statistical methods.
    
    Calculates z-scores, checks time patterns, and distance anomalies.
    This is a Python calculation tool - NO LLM involved.
    
    Returns:
        Dictionary with anomaly flags and scores
    """
    # Amount anomaly
    z_score = (amount - customer_avg) / (customer_std + 1e-5)
    amount_anomaly = abs(z_score) > 3
    
    # Time anomaly
    is_night = (hour >= 22) or (hour <= 6)
    is_unusual_hour = hour not in usual_hours
    time_anomaly = is_night or is_unusual_hour
    
    # Location anomaly
    location_anomaly = distance_km > 80
    
    return {
        "amount_anomaly": {
            "z_score": float(z_score),
            "is_anomaly": amount_anomaly,
            "severity": "high" if abs(z_score) > 5 else "medium" if abs(z_score) > 3 else "low"
        },
        "time_anomaly": {
            "hour": hour,
            "is_night": is_night,
            "is_unusual": is_unusual_hour,
            "is_anomaly": time_anomaly
        },
        "location_anomaly": {
            "distance_km": distance_km,
            "is_far": location_anomaly,
            "is_anomaly": location_anomaly
        },
        "total_anomalies": sum([amount_anomaly, time_anomaly, location_anomaly])
    }

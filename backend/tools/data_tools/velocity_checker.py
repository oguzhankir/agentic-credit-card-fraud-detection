from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class VelocityInput(BaseModel):
    transaction_count_1h: int = Field(description="Number of transactions in last hour")
    transaction_count_24h: int = Field(description="Number of transactions in last 24 hours")

@tool("check_velocity", args_schema=VelocityInput)
def check_velocity_tool(transaction_count_1h: int, transaction_count_24h: int) -> dict:
    """Check for high frequency transaction velocity."""
    velocity_risk = "LOW"
    if transaction_count_1h > 5:
        velocity_risk = "CRITICAL"
    elif transaction_count_1h > 3:
        velocity_risk = "HIGH"
    elif transaction_count_24h > 15:
        velocity_risk = "MEDIUM"
        
    return {
        "velocity_risk": velocity_risk, 
        "details": f"{transaction_count_1h} tx/hr, {transaction_count_24h} tx/day"
    }

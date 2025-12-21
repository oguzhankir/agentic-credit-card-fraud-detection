from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Dict, Any

class AlertInput(BaseModel):
    decision: Dict[str, Any] = Field(description="Final decision from coordinator")
    transaction: Dict[str, Any] = Field(description="Transaction details")
    risk_score: int = Field(description="Risk score 0-100")

@tool("generate_alert", args_schema=AlertInput)
def generate_alert_tool(decision: Dict[str, Any], transaction: Dict[str, Any], risk_score: int) -> Dict[str, Any]:
    """Generate structured alert object."""
    
    # 1. Determine Level
    level = "INFO"
    action = decision.get('action', 'MANUAL_REVIEW')
    
    if action == 'BLOCK':
        level = "CRITICAL"
    elif action == 'MANUAL_REVIEW':
        level = "WARNING"
    elif risk_score > 70:
        level = "HIGH"
        
    # 2. Construct Message
    message = f"Transaction {transaction.get('transaction_id')} flagged. Decision: {action}. Risk Score: {risk_score}."
    
    return {
        "alert_id": "ALT-" + str(int(transaction.get('amount', 0) * 100)), # Mock ID
        "level": level,
        "message": message,
        "timestamp": "now",
        "recommended_action": decision.get("recommended_actions", ["Review details"])
    }

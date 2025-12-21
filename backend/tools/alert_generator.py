from langchain.tools import tool
from pydantic import BaseModel, Field

class AlertInput(BaseModel):
    decision: Dict[str, Any] = Field(description="Final decision from coordinator")
    transaction: Dict[str, Any] = Field(description="Transaction details")
    risk_score: int = Field(description="Risk score 0-100")

@tool("generate_alert", args_schema=AlertInput)
def generate_alert(decision: Dict[str, Any], transaction: Dict[str, Any], risk_score: int) -> Dict[str, Any]:
    """Generate structured alert object."""
    
    # 1. Determine Level
    if risk_score >= 86: level = 'CRITICAL'
    elif risk_score >= 61: level = 'HIGH'
    elif risk_score >= 31: level = 'MEDIUM'
    else: level = 'LOW'
    
    # 2. Generate Message
    amt = transaction.get('amount')
    date = transaction.get('time')
    message = f"Risk Level {level}: ${amt} transaction at {date}. Action: {decision.get('action')}"
    
    # 3. Recommended Actions
    actions = []
    action_type = decision.get('action', 'REVIEW')
    
    if action_type == 'BLOCK':
        actions.extend([
            'Block transaction immediately',
            'Send SMS verification to customer', 
            'Alert fraud investigation team',
            'Freeze card temporarily'
        ])
    elif action_type == 'MANUAL_REVIEW':
        actions.extend([
            'Queue for manual review',
            'Contact customer via App',
            'Flag in fraud dashboard'
        ])
    else:
        actions.extend([
            'Approve transaction',
            'Log for later review'
        ])
        
    return {
        'alert_id': f"alert_{uuid4().hex[:12]}",
        'level': level,
        'timestamp': datetime.now().isoformat(),
        'transaction_id': transaction.get('transaction_id'),
        'message': message,
        'recommended_actions': actions,
        'metadata': {
            'risk_score': risk_score,
            'fraud_probability': decision.get('fraud_probability'),
            'key_factors': decision.get('key_factors', [])
        }
    }

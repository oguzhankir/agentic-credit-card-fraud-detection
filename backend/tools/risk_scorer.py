from langchain.tools import tool
from pydantic import BaseModel, Field

class RiskScorerInput(BaseModel):
    model_prediction: Dict[str, Any] = Field(description="Prediction output from model_predictor")
    anomalies: Dict[str, Any] = Field(description="Anomaly detection results")
    business_rules: Dict[str, bool] = Field(default={}, description="Applied business rules")

@tool("calculate_risk_score", args_schema=RiskScorerInput)
def calculate_risk_score(model_prediction: Dict[str, Any], anomalies: Dict[str, Any], business_rules: Dict[str, bool] = None) -> Dict[str, Any]:
    """
    Calculate 0-100 risk score based on weighted factors.
    """
    if business_rules is None:
        business_rules = {}

    # 1. Base Score from Model (Max 50)
    # fraud_probability is 0.0 to 1.0
    prob = model_prediction.get('fraud_probability', 0.0)
    base_score = prob * 50
    
    # 2. Anomaly Penalties (Max 40)
    anomaly_score = 0
    
    # Amount
    amt = anomalies.get('amount', {})
    if amt.get('is_anomaly'):
        sev = amt.get('severity', 'low')
        anomaly_score += 15 if sev == 'high' else 10 if sev == 'medium' else 5
        
    # Time
    time = anomalies.get('time', {})
    if time.get('is_anomaly'):
        anomaly_score += 10
        
    # Location
    loc = anomalies.get('location', {})
    if loc.get('is_anomaly'):
        sev = loc.get('severity', 'low')
        anomaly_score += 15 if sev == 'high' else 10
        
    # Cap anomaly score
    anomaly_score = min(40, anomaly_score)
    
    # 3. Business Rules (Max 10)
    rule_score = 0
    # Example rules passed in
    if business_rules.get('high_amount'): rule_score += 10
    if business_rules.get('new_customer'): rule_score += 5
    
    rule_score = min(10, rule_score)
    
    # Total
    total_score = int(min(100, base_score + anomaly_score + rule_score))
    
    return {
        'risk_score': total_score,
        'category': categorize_risk(total_score),
        'breakdown': {
            'model_score': round(base_score, 1),
            'anomaly_score': anomaly_score,
            'business_score': rule_score
        },
        'calculation_method': 'weighted_sum'
    }

def categorize_risk(score: int) -> str:
    if score <= 30: return 'LOW'
    elif score <= 60: return 'MEDIUM'
    elif score <= 85: return 'HIGH'
    else: return 'CRITICAL'

def apply_business_rules(transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Dict[str, bool]:
    """Check explicit business rules."""
    rules = {}
    
    # Rule 1: High Amount > 5000
    if transaction.get('amount', 0) > 5000:
        rules['high_amount'] = True
        
    # Rule 2: High Risk Category
    if transaction.get('category') in ['shopping_net', 'misc_net', 'entertainment']:
        rules['video_game_or_net'] = True
        
    # Rule 3: New Customer (if history suggests)
    if customer_history.get('transaction_count', 100) < 5:
        rules['new_customer'] = True
        
    return rules

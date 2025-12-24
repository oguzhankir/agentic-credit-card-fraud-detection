from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class RiskScorerInput(BaseModel):
    """Input schema for risk scorer"""
    # Flattened inputs for easier LLM usage
    fraud_probability: float = Field(None, description="Probability from model (0-1)")
    anomalies: dict = Field(None, description="Anomalies dictionary from detection step")
    
    class Config:
        extra = "allow"

@tool("calculate_risk_score", args_schema=RiskScorerInput)
def calculate_risk_score_tool(
    fraud_probability: float = None,
    anomalies: dict = None,
    **kwargs
) -> dict:
    """
    Calculate final risk score (0-100) from model and anomalies.
    
    Args:
        fraud_probability: Model probability
        anomalies: Anomalies dict
        **kwargs: Fallback for loose args
        
    Returns:
        Risk score and category
    """
    # Handle inputs
    if fraud_probability is None:
        # Check if passed as model_prediction dict
        model_pred = kwargs.get('model_prediction', {})
        fraud_probability = model_pred.get('fraud_probability', 0.0)
    
    if anomalies is None:
         anomalies = kwargs.get('anomalies', {})
         
    # 1. Base Score from Model (0-50)
    base_score = fraud_probability * 50
    
    # 2. Anomaly Penalties (0-40)
    anomaly_score = 0
    # anomalies output has 'anomalies' key wrapping the content
    anomaly_details = anomalies.get('anomalies', {})
    
    severities = []
    
    for anomaly_type, data in anomaly_details.items():
        if isinstance(data, dict) and data.get('is_anomaly'):
            sev = data.get('severity', 'low')
            severities.append(sev)
            
            if sev == 'high':
                anomaly_score += 20
            elif sev == 'medium':
                anomaly_score += 10
            else:
                anomaly_score += 5
                
    # Cap anomaly score at 40
    anomaly_score = min(40, anomaly_score)
    
    # 3. Business Rules / Heuristics (0-10)
    business_score = 0
    if 'high' in severities and len([s for s in severities if s in ['high', 'medium']]) >= 2:
        business_score += 10
    
    # Total Calculation
    total_score = base_score + anomaly_score + business_score
    total_score = min(100, total_score) # Cap at 100
    
    # Categorize
    if total_score >= 85:
        category = 'CRITICAL'
    elif total_score >= 60:
        category = 'HIGH'
    elif total_score >= 30:
        category = 'MEDIUM'
    else:
        category = 'LOW'
    
    return {
        'risk_score': int(total_score),
        'category': category,
        'breakdown': {
            'model_contribution': int(base_score),
            'anomaly_contribution': int(anomaly_score),
            'business_rules_contribution': int(business_score)
        }
    }

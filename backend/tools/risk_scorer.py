from typing import Any, Dict, List
from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class RiskScorerInput(BaseModel):
    """Input schema for risk scorer"""
    # Flattened inputs for easier LLM usage
    fraud_probability: float = Field(None, description="Probability from model (0-1)")
    anomalies: Any = Field(None, description="Anomalies dictionary OR a list of severity strings (e.g. ['high', 'medium'])")
    
    class Config:
        extra = "allow"

@tool("calculate_risk_score", args_schema=RiskScorerInput)
def calculate_risk_score_tool(
    fraud_probability: float = None,
    anomalies: Any = None,
    **kwargs
) -> dict:
    """
    Calculate final risk score (0-100) from model and anomalies.
    
    Args:
        fraud_probability: Model probability (0.0 to 1.0)
        anomalies: Anomalies dict OR list of severities detected (e.g., ['high', 'medium'])
        **kwargs: Fallback for loose args
        
    Returns:
        Risk score and category
    """
    # 1. Handle Inputs
    if fraud_probability is None:
        model_pred = kwargs.get('model_prediction', {})
        fraud_probability = model_pred.get('fraud_probability', 0.0)
    
    # Ensure fraud_probability is a float
    try:
        fraud_probability = float(fraud_probability)
    except:
        fraud_probability = 0.0

    # 2. Extract Severities
    severities = []
    
    if isinstance(anomalies, list):
        # LLM passed a list of strings like ['high', 'medium']
        severities = [str(s).lower() for s in anomalies]
    elif isinstance(anomalies, dict):
        # Traditional way: passed the result of detect_anomalies
        anomaly_details = anomalies.get('anomalies', anomalies)
        for data in anomaly_details.values():
            if isinstance(data, dict) and data.get('is_anomaly'):
                severities.append(data.get('severity', 'low').lower())
    elif isinstance(anomalies, str):
        # LLM passed a comma-separated string?
        severities = [s.strip().lower() for s in anomalies.split(',') if s.strip()]

    # 3. Base Score from Model (0-50)
    base_score = fraud_probability * 50
    
    # 4. Anomaly Penalties (0-40)
    anomaly_score = 0
    for sev in severities:
        if sev == 'high':
            anomaly_score += 20
        elif sev == 'medium':
            anomaly_score += 10
        elif sev in ['low', 'benford']: # Include low level anomalies
            anomaly_score += 5
                
    # Cap anomaly score at 40
    anomaly_score = min(40, anomaly_score)
    
    # 5. Business Rules / Heuristics (0-10)
    business_score = 0
    # Rule: If we have multiple significant anomalies
    sig_anomalies = [s for s in severities if s in ['high', 'medium']]
    if len(sig_anomalies) >= 2:
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

from datetime import datetime
from typing import Dict, Any, List

from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class RiskScorerInput(BaseModel):
    model_prediction: Dict[str, Any] = Field(description="The complete prediction dictionary from the model agent, containing fraud_probability, binary_prediction, model_name, etc.")
    anomalies: Dict[str, Any] = Field(description="The complete anomalies dictionary from the data agent, containing amount_anomaly, time_anomaly, location_anomaly, etc.")
    business_rules: Dict[str, bool] = Field(default={}, description="Optional business rules to apply")

@tool("calculate_risk_score", args_schema=RiskScorerInput)
def calculate_risk_score_tool(model_prediction: Dict[str, Any], anomalies: Dict[str, Any], business_rules: Dict[str, bool] = None) -> Dict[str, Any]:
    """
    Calculate a 0-100 risk score by combining model predictions and anomaly detections.
    
    REQUIRED PARAMETERS:
    - model_prediction: The prediction dict from model agent (must include 'fraud_probability')
    - anomalies: The anomalies dict from data agent (must include anomaly details)
    
    Returns a dict with 'risk_score' (0-100), 'risk_level', and 'breakdown' of how score was calculated.
    """
    if business_rules is None:
        business_rules = {}

    # 1. Base Score from Model (Max 50)
    fraud_prob = model_prediction.get('fraud_probability', 0)
    model_score = fraud_prob * 50

    # 2. Anomaly Score (Max 40)
    anomaly_score = 0
    
    # Amount anomaly
    amount_anom = anomalies.get('amount', {})
    # Handle both new 'amount' dict structure and legacy key access if needed
    if 'amount_anomaly' in anomalies: # From new structure
        if anomalies['amount_anomaly'].get('is_anomaly'):
            anomaly_score += 15
    elif amount_anom.get('is_anomaly'): # From legacy structure
        anomaly_score += 15
        
    # Time anomaly
    time_anom = anomalies.get('time', {})
    if 'time_anomaly' in anomalies:
         if anomalies['time_anomaly'].get('is_anomaly'):
            anomaly_score += 10
    elif time_anom.get('is_anomaly'):
        anomaly_score += 10
        
    # Location anomaly
    loc_anom = anomalies.get('location', {})
    if 'location_anomaly' in anomalies:
        if anomalies['location_anomaly'].get('is_anomaly'):
            anomaly_score += 15
    elif loc_anom.get('is_anomaly'):
        anomaly_score += 15

    # 3. Business Rules (Max 10)
    rule_score = 0
    if business_rules.get('velocity_check_failed'):
        rule_score += 10
    
    total_score = min(100, model_score + anomaly_score + rule_score)
    
    return {
        "risk_score": int(total_score),
        "breakdown": {
            "model_contribution": int(model_score),
            "anomaly_contribution": int(anomaly_score),
            "rule_contribution": int(rule_score)
        }
    }

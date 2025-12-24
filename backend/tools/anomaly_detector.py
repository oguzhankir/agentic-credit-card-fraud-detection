from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class AnomalyDetectorInput(BaseModel):
    """Input schema for anomaly detector"""
    # Key features needed for detection (flattened)
    amt_z_score: float = Field(None, description="Z-score of transaction amount")
    is_night: int = Field(None, description="1 if transaction is at night")
    is_fraud_peak_hour: int = Field(None, description="1 if transaction is in peak fraud hour")
    distance_km: float = Field(None, description="Distance from home in km")
    is_distant_tx: int = Field(None, description="1 if transaction is distant")
    benford_expected: float = Field(None, description="Benford's Law expected probability")
    
    class Config:
        extra = "allow"

@tool("detect_anomalies", args_schema=AnomalyDetectorInput)
def detect_anomalies_tool(**kwargs) -> dict:
    """
    Detect anomalies in transaction features using statistical methods.
    
    Detects:
    1. Amount anomaly (Z-score > 3)
    2. Time anomaly (night hours, unusual for customer)
    3. Location anomaly (distance > 80km)
    
    This is PURE PYTHON - no LLM involved.
    
    Args:
        **kwargs: Engineered features (must include amt_z_score, distance_km, etc.)
        
    Returns:
        Dictionary with anomaly flags and severity levels
    """
    features = kwargs
    anomalies = {}
    
    # 1. Amount anomaly
    if 'amt_z_score' in features:
        z_score = features['amt_z_score']
        is_anomaly = abs(z_score) > 3
        # Determine severity
        if abs(z_score) > 5:
            severity = 'high'
        elif abs(z_score) > 3:
            severity = 'medium'
        else:
            severity = 'low'
            
        anomalies['amount'] = {
            'is_anomaly': is_anomaly,
            'z_score': z_score,
            'severity': severity if is_anomaly else 'none',
            'explanation': f'{z_score:.2f} standard deviations from customer baseline'
        }
    
    # 2. Time anomaly
    is_night = features.get('is_night', 0)
    is_peak_fraud = features.get('is_fraud_peak_hour', 0)
    
    if is_night or is_peak_fraud:
        severity = 'medium' if is_peak_fraud else 'low'
        anomalies['time'] = {
            'is_anomaly': True,
            'severity': severity,
            'explanation': 'Transaction during high-risk hours (Late night/Early morning)'
        }
    else:
        anomalies['time'] = {
            'is_anomaly': False,
            'severity': 'none',
            'explanation': 'Transaction during normal hours'
        }
    
    # 3. Location anomaly
    dist_km = features.get('distance_km', 0)
    is_distant = features.get('is_distant_tx', 0)
    
    if is_distant or dist_km > 80:
        severity = 'high' if dist_km > 500 else 'medium'
        anomalies['location'] = {
            'is_anomaly': True,
            'distance_km': dist_km,
            'severity': severity,
            'explanation': f'Transaction location is {dist_km:.1f}km from home'
        }
    else:
        anomalies['location'] = {
            'is_anomaly': False,
            'distance_km': dist_km,
            'severity': 'none',
            'explanation': 'Location consistent with home address'
        }
        
    # Benford's Law Check (experimental)
    benford_prob = features.get('benford_expected', 1.0)
    if benford_prob < 0.05: # e.g. starting with 9 is rare (~4.6%)
        anomalies['benford'] = {
            'is_anomaly': True,
            'severity': 'low',
            'explanation': f'Leading digit has low probability ({benford_prob:.1%}) according to Benford\'s Law'
        }

    # 4. Summary
    total_anomalies = sum(1 for a in anomalies.values() if a.get('is_anomaly'))
    
    # Simple risk mapping
    if total_anomalies >= 2:
        overall_risk = 'HIGH'
    elif total_anomalies == 1:
        # If the one anomaly is HIGH severity, then overall is HIGH
        severities = [a.get('severity') for a in anomalies.values() if a.get('is_anomaly')]
        if 'high' in severities:
            overall_risk = 'HIGH'
        elif 'medium' in severities:
            overall_risk = 'MEDIUM'
        else:
            overall_risk = 'LOW'
    else:
        overall_risk = 'LOW'
    
    return {
        'anomalies': anomalies,
        'total_anomalies': total_anomalies,
        'overall_risk': overall_risk
    }

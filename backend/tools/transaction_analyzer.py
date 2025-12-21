from datetime import datetime
import math
from typing import Dict, Any, List

def analyze_amount(amount: float, customer_avg: float, customer_std: float) -> Dict[str, Any]:
    """Calculate Z-Score and determine amount anomaly."""
    if customer_std == 0:
        z_score = 0 if amount == customer_avg else 10 # Sentinel
    else:
        z_score = (amount - customer_avg) / customer_std
    
    abs_z = abs(z_score)
    is_anomaly = abs_z > 3
    
    if abs_z > 5: severity = 'high'
    elif abs_z > 3: severity = 'medium'
    else: severity = 'low'
    
    return {
        'z_score': round(z_score, 2),
        'is_anomaly': is_anomaly,
        'severity': severity,
        'value': amount,
        'baseline': customer_avg,
        'explanation': f"{z_score:.1f} standard deviations from normal"
    }

def analyze_time_pattern(time_str: str, usual_hours: List[int]) -> Dict[str, Any]:
    """Check for night hours and unusual timing."""
    try:
        dt = datetime.fromisoformat(time_str)
    except ValueError:
        # Fallback if format is not ISO
        return {'error': 'Invalid time format'}
        
    hour = dt.hour
    is_night = (hour >= 22) or (hour <= 6)
    is_unusual = hour not in usual_hours if usual_hours else False
    
    is_anomaly = is_night or is_unusual
    severity = 'high' if (is_night and is_unusual) else 'medium' if is_anomaly else 'low'
    
    return {
        'hour': hour,
        'is_night': is_night,
        'is_unusual': is_unusual,
        'is_anomaly': is_anomaly,
        'severity': severity,
        'explanation': f"Transaction at {hour}:00 ({'Night' if is_night else 'Day'}). {'Unusual for customer.' if is_unusual else 'Normal timing.'}"
    }

def analyze_geospatial(location: Dict[str, float], customer_history: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyze distance from home."""
    distance = location.get('distance_from_home', 0)
    
    # Thresholds based on typical behavior (or EDA inputs)
    is_far = distance > 80
    
    if distance > 200: severity = 'high'
    elif distance > 80: severity = 'medium'
    else: severity = 'low'
    
    return {
        'distance_km': distance,
        'is_far': is_far,
        'is_anomaly': is_far,
        'severity': severity,
        'explanation': f"{distance}km from home. {'Suspiciously far.' if is_far else 'Within normal range.'}"
    }

def calculate_all_anomalies(transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate all anomaly checks."""
    
    # 1. Amount
    amount_res = analyze_amount(
        transaction.get('amount', 0), 
        customer_history.get('avg_amount', 0), 
        customer_history.get('std_amount', 1)
    )
    
    # 2. Time
    time_res = analyze_time_pattern(
        transaction.get('time', datetime.now().isoformat()),
        customer_history.get('usual_hours', [])
    )
    
    # 3. Location
    loc_res = analyze_geospatial(transaction.get('location', {}))
    
    # Overall Risk Assessment
    anomaly_count = sum([
        1 if amount_res['is_anomaly'] else 0,
        1 if time_res.get('is_anomaly') else 0,
        1 if loc_res['is_anomaly'] else 0
    ])
    
    overall_risk = 'LOW'
    if anomaly_count >= 2 or amount_res.get('severity') == 'high':
        overall_risk = 'CRITICAL' if anomaly_count == 3 else 'HIGH'
    elif anomaly_count == 1:
        overall_risk = 'MEDIUM'
        
    return {
        'amount': amount_res,
        'time': time_res,
        'location': loc_res,
        'total_anomaly_count': anomaly_count,
        'overall_risk': overall_risk,
        'red_flags': [
            k for k, v in {'Amount': amount_res, 'Time': time_res, 'Location': loc_res}.items()
            if v.get('is_anomaly')
        ]
    }

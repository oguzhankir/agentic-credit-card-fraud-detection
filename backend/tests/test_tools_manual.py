import sys
import os
from datetime import datetime

# Add project root to path (parent of backend)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.tools.feature_engineer import engineer_features_tool
from backend.tools.anomaly_detector import detect_anomalies_tool
from backend.tools.risk_scorer import calculate_risk_score_tool

def test_tools():
    print("Testing Backend Tools...")
    
    # 1. Test Feature Engineering
    raw_tx = {
        "trans_date_trans_time": "2024-01-01T23:30:00", # Late night
        "amt": 5000.00,
        "merchant": "fraud_shop",
        "category": "grocery_pos",
        "dob": "1990-01-01T00:00:00",
        "lat": 40.0,
        "long": -74.0,
        "merch_lat": 42.0, # Far away (~200km+)
        "merch_long": -72.0
    }
    
    try:
        # Use .invoke implementation for LangChain tool
        # Input schema is now flattened, so we pass the whole dict as kwargs
        features = engineer_features_tool.invoke(raw_tx)
        print("✅ Feature Engineer: Success")
        print(f"   - Distance: {features.get('distance_km'):.2f}km")
        print(f"   - Is Night: {features.get('is_night')}")
    except Exception as e:
        print(f"❌ Feature Engineer Failed: {e}")
        return

    # 2. Test Anomaly Detection
    try:
        # Inject high Z-score for test
        features['amt_z_score'] = 4.5
        features['is_fraud_peak_hour'] = 1
        
        # Input is now flattened
        anomalies = detect_anomalies_tool.invoke(features)
        print("✅ Anomaly Detector: Success")
        print(f"   - Input Z-Score: {features['amt_z_score']}")
        print(f"   - Amount Anomaly: {anomalies['anomalies']['amount']['is_anomaly']}")
        print(f"   - Location Anomaly: {anomalies['anomalies']['location']['is_anomaly']}")
    except Exception as e:
        print(f"❌ Anomaly Detector Failed: {e}")
        return

    # 3. Test Risk Scorer
    try:
        # Mock model prediction
        model_pred = {"fraud_probability": 0.8, "prediction": 1}
        
        score = calculate_risk_score_tool.invoke({"model_prediction": model_pred, "anomalies": anomalies})
        print("✅ Risk Scorer: Success")
        print(f"   - Risk Score: {score['risk_score']}")
        print(f"   - Category: {score['category']}")
    except Exception as e:
        print(f"❌ Risk Scorer Failed: {e}")
        return

    print("\nAll Tool Tests Passed!")

if __name__ == "__main__":
    test_tools()

import pandas as pd
import numpy as np
import joblib
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

from backend.tools.model_predictor import predict_fraud

# User's exact input from the trace
transaction_features = {
    'amount': 1850.0,
    'merchant': 'Luxury Boutique',
    'category': 'shopping_pos',
    'time': '2020-03-12T23:13',
    'location': {
        'lat': 34.0522,
        'long': -118.2437,
        'distance_from_home': 2500.0,
        'state': 'CA'
    },
    'city_pop': 10000,
    'dob': '1980-01-01',
    'gender': 'F'
}

customer_history = {
    'avg_amount': 100.0,
    'std_amount': 20.0,
    'transaction_count': 1
}

print("Testing user's suspicious transaction...")
result = predict_fraud(transaction_features, customer_history)
print(f"Result: {json.dumps(result, indent=2)}")

# Test with my "Perfect Fraud" category
transaction_features['category'] = 'shopping_net'
print("\nTesting with 'shopping_net' category...")
result_net = predict_fraud(transaction_features, customer_history)
print(f"Result (Net): {json.dumps(result_net, indent=2)}")

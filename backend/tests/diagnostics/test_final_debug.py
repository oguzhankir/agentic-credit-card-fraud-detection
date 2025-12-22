import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Add backend to path
sys.path.append(os.path.abspath("."))

from tools.model_predictor import predict_fraud

def test():
    tx = {
        'amount': 2500.0,
        'merchant': 'fraud_Kirlin and Sons',
        'category': 'shopping_pos',
        'time': '2025-12-22T21:40:00',
        'location': {
            'lat': 40.7128,
            'long': -74.0060,
            'distance_from_home': 500.0
        },
        'customer_id': 'cust_123',
        'dob': '1980-01-01'
    }
    history = {
        'avg_amount': 50.0,
        'std_amount': 10.0,
        'transaction_count': 100
    }
    
    print("Testing suspicious transaction...")
    result = predict_fraud(tx, history)
    print(f"\nFinal Result: {result}")

if __name__ == "__main__":
    test()

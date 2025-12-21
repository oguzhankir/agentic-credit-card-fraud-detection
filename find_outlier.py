import joblib
import os
import sys
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath("."))

from backend.tools.ml_preprocessor import LeakFreePreprocessor

def find_outlier():
    prep_path = "backend/models/preprocessor.pkl"
    import __main__
    __main__.LeakFreePreprocessor = LeakFreePreprocessor
    prep = joblib.load(prep_path)
    
    from backend.tools.model_predictor import engineer_features
    # Mock suspicious tx
    raw_df = pd.DataFrame([{
        'amt': 2500.0,
        'lat': 40.7128, 'long': -74.0060,
        'city_pop': 333497,
        'merch_lat': 40.8128, 'merch_long': -74.1060,
        'category': 'shopping_pos', 'gender': 'M', 'state': 'NY',
        'dob': '1980-01-01',
        'trans_date_trans_time': '2025-12-22 00:00:00'
    }])
    history = {'avg_amount': 50.0, 'std_amount': 10.0, 'transaction_count': 100}
    eng_df = engineer_features(raw_df, history)
    
    X_trans = prep.transform(eng_df)
    
    # Get column names after transform
    # The ColumnTransformer order is num then cat.
    num_cols = prep.transformer.transformers_[0][2]
    cat_cols = prep.transformer.transformers_[1][2]
    all_names = num_cols + cat_cols
    
    print(f"Transformed features len: {X_trans.shape[1]}")
    print(f"Names len: {len(all_names)}")
    
    for i, val in enumerate(X_trans[0]):
        if abs(val) > 10: # Look for > 10 std dev
            print(f"Feature '{all_names[i]}' has OUTLIER value: {val}")

if __name__ == "__main__":
    find_outlier()

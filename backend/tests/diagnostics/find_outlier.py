import joblib
import os
import sys
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath("."))
from tools.ml_preprocessor import LeakFreePreprocessor

def find_outlier():
    prep_path = "backend/models/preprocessor.pkl"
    import __main__
    __main__.LeakFreePreprocessor = LeakFreePreprocessor
    prep = joblib.load(prep_path)
    
    from tools.model_predictor import engineer_features
    raw_df = pd.DataFrame([{
        'amt': 2500.0,
        'lat': 40.7128, 'long': -74.0060,
        'city_pop': 333497,
        'merch_lat': 40.8128, 'merch_long': -74.1060,
        'category': 'shopping_pos', 'gender': 'M', 'state': 'NY',
        'dob': '1980-01-01',
        'trans_date_trans_time': '2025-12-22T21:40:00',
        'distance_from_home': 500.0
    }])
    history = {'avg_amount': 50.0, 'std_amount': 10.0, 'transaction_count': 100}
    eng_df = engineer_features(raw_df, history)
    X_trans = prep.transform(eng_df)
    
    num_cols = prep.transformer.transformers_[0][2]
    cat_cols = prep.transformer.transformers_[1][2]
    all_names = num_cols + cat_cols
    
    # Sort features by value
    indexed_vals = sorted(enumerate(X_trans[0]), key=lambda x: abs(x[1]), reverse=True)
    
    print("Top 20 Features by Outlier Score:")
    for i, val in indexed_vals[:20]:
        print(f"  {all_names[i]}: {val}")

if __name__ == "__main__":
    find_outlier()

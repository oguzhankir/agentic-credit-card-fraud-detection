import joblib
import os
import sys
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath("."))

from backend.tools.ml_preprocessor import LeakFreePreprocessor

def inspect():
    prep_path = "backend/models/preprocessor.pkl"
    if not os.path.exists(prep_path): return

    import __main__
    __main__.LeakFreePreprocessor = LeakFreePreprocessor

    prep = joblib.load(prep_path)
    if hasattr(prep, 'transformer'):
        ct = prep.transformer
        all_cols = []
        for name, transformer, columns in ct.transformers_:
            if name != 'remainder':
                print(f"Transformer '{name}' columns ({len(columns)}): {columns}")
                all_cols.extend(columns)
        
        print(f"\nTotal expected columns: {len(all_cols)}")
        
        # Now mock a transaction and see what our engineer_features produces
        from backend.tools.model_predictor import engineer_features
        raw_df = pd.DataFrame([{
            'amt': 2500.0,
            'lat': 33.96, 'long': -80.93,
            'city_pop': 333497,
            'merch_lat': 33.98, 'merch_long': -81.20,
            'category': 'shopping_pos', 'gender': 'M', 'state': 'SC',
            'dob': '1968-03-19',
            'trans_date_trans_time': '2025-12-22 00:00:00'
        }])
        history = {'avg_amount': 100.0, 'std_amount': 20.0, 'transaction_count': 50}
        eng_df = engineer_features(raw_df, history)
        eng_cols = eng_df.columns.tolist()
        
        print(f"\nBackend engineered columns ({len(eng_cols)}): {eng_cols}")
        
        missing = set(all_cols) - set(eng_cols)
        extra = set(eng_cols) - set(all_cols)
        
        print(f"\nMissing in backend: {missing}")
        print(f"Extra in backend (will be dropped): {extra}")

if __name__ == "__main__":
    inspect()

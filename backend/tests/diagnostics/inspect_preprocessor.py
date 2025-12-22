import joblib
import os
import sys
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath("."))
from tools.ml_preprocessor import LeakFreePreprocessor

def inspect():
    prep_path = "backend/models/preprocessor.pkl"
    import __main__
    __main__.LeakFreePreprocessor = LeakFreePreprocessor
    prep = joblib.load(prep_path)
    if hasattr(prep, 'transformer'):
        ct = prep.transformer
        for name, transformer, columns in ct.transformers_:
            if name == 'cat' and 'category' in columns:
                idx = columns.index('category')
                # TargetEncoder stores the encodings in its 'encodings_' or similar internal attribute
                # Since it's scikit-learn TargetEncoder, we might need to use its transform on dummy test cases
                # or check its attributes if it's the one from category_encoders (it is likely sklearn 1.3+)
                
                test_categories = ['shopping_pos', 'shopping_net', 'gas_transport', 'misc_pos', 'entertainment']
                test_df = pd.DataFrame({'category': test_categories})
                # We need to fill other cat columns to avoid errors
                for col in columns:
                    if col != 'category':
                        test_df[col] = transformer.categories_[columns.index(col)][0]
                
                # Transform just the categorical part
                transformed = transformer.transform(test_df)
                for i, cat in enumerate(test_categories):
                    print(f"Category '{cat}' encoded as: {transformed[i, idx]}")

if __name__ == "__main__":
    inspect()

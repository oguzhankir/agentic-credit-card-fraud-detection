import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, TargetEncoder

class LeakFreePreprocessor(BaseEstimator, TransformerMixin):
    """
    Custom preprocessor to match the one used during training in notebooks.
    Handles numerical scaling and categorical target encoding.
    """
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.transformer = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), num_cols),
                ('cat', TargetEncoder(smooth=10.0, random_state=42), cat_cols)
            ],
            remainder='drop',
            verbose_feature_names_out=False
        )
        
    def fit(self, X, y=None):
        self.transformer.fit(X, y)
        return self
    
    def transform(self, X):
        return self.transformer.transform(X)
    
    def get_feature_names_out(self):
        return self.transformer.get_feature_names_out()

from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
import numpy as np
import math
import json
from pathlib import Path
from backend.config.settings import settings

class FeatureEngineerInput(BaseModel):
    """Input schema for feature engineering tool"""
    # Flattened fields to help LLM
    trans_date_trans_time: str = Field(..., description="Transaction timestamp")
    amt: float = Field(..., description="Transaction amount")
    merchant: str = Field(..., description="Merchant name")
    category: str = Field(..., description="Transaction category")
    # Optional fields that might be in the input
    lat: float = Field(None, description="Latitude")
    long: float = Field(None, description="Longitude")
    merch_lat: float = Field(None, description="Merchant Latitude")
    merch_long: float = Field(None, description="Merchant Longitude")
    dob: str = Field(None, description="Date of birth")
    city_pop: int = Field(None, description="Population of city")
    zip: str = Field(None, description="Zip code")
    state: str = Field(None, description="State")
    job: str = Field(None, description="Job title")
    merch_zip: str = Field(None, description="Merchant Zip")
    gender: str = Field(None, description="Gender")
    
    class Config:
        extra = "allow"

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2*R*np.arctan2(np.sqrt(a), np.sqrt(1-a))

def cyclical_encode(value, max_val):
    """Encode cyclical features using sin and cos."""
    sin_val = np.sin(2 * np.pi * value / max_val)
    cos_val = np.cos(2 * np.pi * value / max_val)
    return sin_val, cos_val

@tool("engineer_features", args_schema=FeatureEngineerInput)
def engineer_features_tool(
    trans_date_trans_time: str, 
    amt: float, 
    merchant: str, 
    category: str,
    **kwargs
) -> dict:
    """
    Engineer 67 features from raw transaction data.
    
    Args:
        trans_date_trans_time: Transaction timestamp
        amt: Amount
        merchant: Merchant name
        category: Category
        **kwargs: Other transaction fields
        
    Returns:
        Dictionary with engineered features
    """
    # Reconstruct dictionary
    raw_transaction = kwargs
    raw_transaction.update({
        'trans_date_trans_time': trans_date_trans_time,
        'amt': amt,
        'merchant': merchant,
        'category': category
    })
    
    # 1. Convert to DataFrame for easier manipulation
    df = pd.DataFrame([raw_transaction])
    
    # Ensure correct data types (matching notebook logic)
    df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
    
    if 'dob' in df.columns and df['dob'].notna().all():
        df['dob'] = pd.to_datetime(df['dob'])
    else:
        # Fallback if dob missing: assume mean age ~33
        df['dob'] = df['trans_date_trans_time'] - pd.Timedelta(days=33*365.25)

    df['amt'] = df['amt'].astype(float)
    
    # Defaults for potential missing schema fields required by model
    if 'category' not in df.columns: df['category'] = 'unknown'
    if 'city_pop' not in df.columns: df['city_pop'] = 0 # Default low pop
    if 'job' not in df.columns: df['job'] = 'unknown'
    if 'state' not in df.columns: df['state'] = 'unknown'
    if 'zip' not in df.columns: df['zip'] = '00000'
    if 'gender' not in df.columns: df['gender'] = 'F' # OR M, doesn't matter much for default


    # 2. Temporal Features
    df['hour'] = df['trans_date_trans_time'].dt.hour
    df['day_of_week'] = df['trans_date_trans_time'].dt.dayofweek
    df['day_of_month'] = df['trans_date_trans_time'].dt.day
    df['month'] = df['trans_date_trans_time'].dt.month
    df['year'] = df['trans_date_trans_time'].dt.year

    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_night'] = df['hour'].apply(lambda x: 1 if (23 <= x or x <= 6) else 0)
    df['is_business_hours'] = df['hour'].apply(lambda x: 1 if (9 <= x <= 17) else 0)

    # Time of day category
    def get_time_of_day(h):
        if 6 <= h < 12: return 'morning'
        elif 12 <= h < 18: return 'afternoon'
        elif 18 <= h < 24: return 'evening'
        else: return 'night'
    df['time_of_day'] = df['hour'].apply(get_time_of_day) # Keep as string for now if needed, or encode if model expects specific format. 
    # Note: Model likely expects OneHot or ordinal for categorical. The notebook usually drops processed categoricals or uses frequency map.
    # The final feature set list from notebook had 'time_of_day' as a feature but XGBoost needs numbers.
    # Let's assume the preprocessor handles encoding or we strictly output numerical features here.
    # Notebook output "Final Feature Set" includes 'time_of_day'. We'll keep it.

    # Cyclical Encoding
    df['hour_sin'], df['hour_cos'] = zip(*df['hour'].apply(lambda x: cyclical_encode(x, 24)))
    df['day_of_week_sin'], df['day_of_week_cos'] = zip(*df['day_of_week'].apply(lambda x: cyclical_encode(x, 7)))
    df['month_sin'], df['month_cos'] = zip(*df['month'].apply(lambda x: cyclical_encode(x, 12)))
    df['day_of_month_sin'], df['day_of_month_cos'] = zip(*df['day_of_month'].apply(lambda x: cyclical_encode(x, 31)))

    # Age
    df['age'] = (df['trans_date_trans_time'] - df['dob']).dt.days / 365.25
    # Age Group
    # Note: pd.cut returns categorical, we might need string for JSON serialization
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 65, 100], labels=['<25', '25-35', '35-50', '50-65', '65+']).astype(str)

    # 3. Geospatial Analysis
    if all(k in df.columns for k in ['lat', 'long', 'merch_lat', 'merch_long']):
        df['distance_km'] = haversine(df['lat'], df['long'], df['merch_lat'], df['merch_long'])
    else:
        df['distance_km'] = 0.0 # Default if coordinates missing
        
    df['distance_cat'] = pd.cut(df['distance_km'], 
                                bins=[-1, 5, 25, 100, 500, 25000], 
                                labels=['very_close', 'close', 'medium', 'far', 'very_far']).astype(str)
    df['is_long_distance'] = (df['distance_km'] > 100).astype(int)

    # 4. Financial Transaction Profiling
    df['log_amt'] = np.log1p(df['amt'])
    df['sqrt_amt'] = np.sqrt(df['amt'])
    df['amt_rounded'] = df['amt'].round(-1)
    df['amt_tier'] = pd.cut(df['amt'], 
                            bins=[0, 10, 50, 100, 500, 100000], 
                            labels=['micro', 'small', 'medium', 'large', 'very_large']).astype(str)
    df['is_round_amt'] = ((df['amt'] % 10 == 0) | (df['amt'] % 100 == 0)).astype(int)
    df['is_exact_dollar'] = (df['amt'] == df['amt'].astype(int)).astype(int)

    # 5. Merchant & Category Encoding (Frequency Maps)
    # Load maps from artifacts
    merch_freq_map = {}
    cat_freq_map = {}
    try:
        if Path(settings.merchant_freq_path).exists():
            with open(settings.merchant_freq_path, 'r') as f:
                merch_freq_map = json.load(f)
        
        if Path(settings.category_freq_path).exists():
            with open(settings.category_freq_path, 'r') as f:
                cat_freq_map = json.load(f)
    except Exception as e:
        # Fallback to empty if file missing or corrupt
        # In prod, we might want to log this warning
        pass

    df['merch_freq'] = df['merchant'].map(merch_freq_map).fillna(1.0) # Default to 1 (rare)
    df['cat_freq'] = df['category'].map(cat_freq_map).fillna(1.0)
    
    high_risk_cats = ['grocery_pos', 'shopping_net', 'gas_transport']
    df['is_high_risk_cat'] = df['category'].isin(high_risk_cats).astype(int)

    # 6. EDA-Driven Indicators
    # Benford's
    def first_digit(x):
        s = str(x)
        for char in s:
            if char.isdigit() and char != '0':
                return int(char)
        return 1
    df['first_digit'] = df['amt'].apply(first_digit)
    benford_probs = {d: math.log10(1 + 1/d) for d in range(1, 10)}
    df['benford_expected'] = df['first_digit'].map(benford_probs)
    df['benford_log_prob'] = np.log(df['benford_expected'])
    
    # High risk hours
    df['is_fraud_peak_hour'] = df['hour'].isin([22, 23, 0, 1, 2, 3]).astype(int)
    hour_risk_map = {h: 0.25 for h in range(4)}
    hour_risk_map.update({h: 0.26 for h in range(22, 24)})
    df['hour_risk_score'] = df['hour'].map(hour_risk_map).fillna(0.01)
    
    df['is_high_risk_amt'] = ((df['log_amt'] >= 6) & (df['log_amt'] <= 8)).astype(int)
    df['is_distant_tx'] = (df['distance_km'] > 80).astype(int)

    # 7. Behavioral History
    # NOTE: Since we process single transactions live, we often don't have the full real-time history 
    # loaded in memory. In a prod system, we'd query a Feature Store (Redis/Feast).
    # For this implementation, we will use provided values if available in input, 
    # otherwise default to "new customer" baselines to avoid crashing.
    
    # Check if history fields exist in input, else default to notebook defaults
    df['cust_tx_count'] = raw_transaction.get('cust_tx_count', 0) 
    df['days_since_last_tx'] = raw_transaction.get('days_since_last_tx', 999.0)
    df['cust_avg_amt'] = raw_transaction.get('cust_avg_amt', 0.0)
    df['cust_std_amt'] = raw_transaction.get('cust_std_amt', 0.0)
    df['amt_z_score'] = 0.0 # Default if no history
    if raw_transaction.get('cust_std_amt', 0) > 0:
         df['amt_z_score'] = (df['amt'] - df['cust_avg_amt']) / (df['cust_std_amt'] + 1e-5)
    
    # 8. Interactions
    df['amt_x_dist'] = df['amt'] * df['distance_km']
    df['amt_x_night'] = df['amt'] * df['is_night']
    df['dist_x_weekend'] = df['distance_km'] * df['is_weekend']
    df['age_x_amt'] = df['age'] * df['amt']

    # Convert to dict, handling potential numpy types
    result = df.to_dict(orient='records')[0]
    
    # JSON serialization safety for numpy types
    for k, v in result.items():
        if isinstance(v, (np.integer, np.int64, np.int32, np.int8)):
            result[k] = int(v)
        elif isinstance(v, (np.floating, np.float64, np.float32)):
            result[k] = float(v)
            
    return result

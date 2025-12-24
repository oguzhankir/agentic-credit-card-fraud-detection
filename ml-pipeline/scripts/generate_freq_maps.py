import pandas as pd
import json
import os

# Path to data
DATA_PATH = "/Users/oguz/Desktop/agentic-credit-card-fraud-detection/ml-pipeline/data/raw/fraudTrain.csv"
OUTPUT_DIR = "/Users/oguz/Desktop/agentic-credit-card-fraud-detection/backend/tools/artifacts"

# Ensure output dir exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Reading {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

print("Generating Merchant Frequency Map...")
# Strip 'fraud_' prefix from merchant names if present
raw_counts = df['merchant'].value_counts().to_dict()
merch_freq = {k.replace('fraud_', ''): v for k, v in raw_counts.items()}

print("Generating Category Frequency Map...")
# Categories might also have prefix? Let's check or just use as is.
# Usually categories are like 'grocery_pos', 'misc_net' etc.
cat_freq = df['category'].value_counts().to_dict()

# Save as JSON
merch_path = os.path.join(OUTPUT_DIR, "merchant_freq_map.json")
cat_path = os.path.join(OUTPUT_DIR, "category_freq_map.json")

with open(merch_path, 'w') as f:
    json.dump(merch_freq, f)

with open(cat_path, 'w') as f:
    json.dump(cat_freq, f)

print(f"Saved maps to {OUTPUT_DIR}")
print(f"Merchant map size: {len(merch_freq)}")
print(f"Category map size: {len(cat_freq)}")

# Test check
print("Test check:")
print(f"fraud_Rippin, Kub and Mann: {merch_freq.get('fraud_Rippin, Kub and Mann', 'Not Found')}")
print(f"grocery_pos: {cat_freq.get('grocery_pos', 'Not Found')}")

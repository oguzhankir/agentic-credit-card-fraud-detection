import json
import os

meta_path = "ml-pipeline/data/metadata/feature_metadata.json"
if os.path.exists(meta_path):
    with open(meta_path, 'r') as f:
        data = f.read()
        print(data)
else:
    print(f"Error: {meta_path} not found")

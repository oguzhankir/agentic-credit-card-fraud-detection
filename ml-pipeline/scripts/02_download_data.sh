#!/bin/bash

# Get the absolute path to the script directory
# This script is located in ml-pipeline/scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Calculate Project Root.
# SCRIPT_DIR is .../agentic-credit-card-fraud-detection/ml-pipeline/scripts
# Parent is .../agentic-credit-card-fraud-detection/ml-pipeline
# Grandparent is .../agentic-credit-card-fraud-detection (Project Root)
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Define the target directory using absolute path
TARGET_DIR="$PROJECT_ROOT/ml-pipeline/data/raw"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

echo "Downloading dataset to $TARGET_DIR..."
# Download the dataset using curl
curl -L -o "$TARGET_DIR/fraud-detection.zip" \
  https://www.kaggle.com/api/v1/datasets/download/kartik2112/fraud-detection

echo "Unzipping dataset..."
# Unzip the file
unzip -o "$TARGET_DIR/fraud-detection.zip" -d "$TARGET_DIR"

echo "Cleaning up zip file..."
# Remove the zip file
rm "$TARGET_DIR/fraud-detection.zip"

echo "Download and extraction complete!"

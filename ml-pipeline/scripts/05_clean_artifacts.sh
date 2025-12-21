#!/bin/bash

# clean_artifacts.sh
# Cleans up generated artifacts for a fresh run
# PROTECTS raw data

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "WARNING: This will delete all ML artifacts (models, metrics, processed data)!"
echo "Raw data will NOT be deleted."
echo ""
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" == "yes" ]; then
    echo "Cleaning up..."
    
    rm -rf "$PROJECT_ROOT/data/processed/"*
    echo "Removed data/processed contents"
    
    rm -rf "$PROJECT_ROOT/data/metadata/"*
    echo "Removed data/metadata contents"
    
    rm -rf "$PROJECT_ROOT/artifacts/models/"*
    echo "Removed artifacts/models contents"
    
    rm -rf "$PROJECT_ROOT/artifacts/metrics/"*
    echo "Removed artifacts/metrics contents"
    
    rm -rf "$PROJECT_ROOT/artifacts/reports/"*
    echo "Removed artifacts/reports contents"
    
    rm -rf "$PROJECT_ROOT/artifacts/logs/"*
    echo "Removed artifacts/logs contents"
    
    # Clean backend
    rm -f "$PROJECT_ROOT/../backend/models/"*
    echo "Removed backend/models contents"

    echo "Cleanup Complete!"
else
    echo "Cleanup Cancelled."
fi

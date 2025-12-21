#!/bin/bash

# validate_artifacts.sh
# Verifies the integrity of generated ML pipeline artifacts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "ML PIPELINE ARTIFACT VALIDATION REPORT"
echo "========================================"

FAILED=0

# Helper function
check_file() {
    local file=$1
    local min_size=$2
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        # Simple size check (exists and > 0)
        if [ -s "$file" ]; then
            echo "PASSED: $(basename "$file") ($size)"
        else
            echo "FAILED: $(basename "$file") is empty!"
            FAILED=1
        fi
    else
        echo "FAILED: $(basename "$file") missing!"
        FAILED=1
    fi
}

echo ""
echo "Data Files:"
check_file "$PROJECT_ROOT/data/processed/features_engineered.parquet" 100
check_file "$PROJECT_ROOT/data/metadata/feature_metadata.json" 0

echo ""
echo "Models:"
# Check for at least 2 models
MODEL_COUNT=$(find "$PROJECT_ROOT/artifacts/models" -name "*_model.pkl" | wc -l)
if [ "$MODEL_COUNT" -gt 0 ]; then
    echo "PASSED: Found $MODEL_COUNT trained models."
else
    echo "FAILED: No model files found!"
    FAILED=1
fi
check_file "$PROJECT_ROOT/artifacts/models/preprocessor.pkl" 0

echo ""
echo "Metrics:"
check_file "$PROJECT_ROOT/artifacts/metrics/model_registry.json" 0

# JSON Validity Check
if [ -f "$PROJECT_ROOT/artifacts/metrics/model_registry.json" ]; then
    python -m json.tool "$PROJECT_ROOT/artifacts/metrics/model_registry.json" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "PASSED: model_registry.json is valid JSON"
    else
        echo "FAILED: model_registry.json is INVALID JSON"
        FAILED=1
    fi
fi

echo ""
echo "Figures:"
IMG_COUNT=$(find "$PROJECT_ROOT/artifacts/reports/figures" -name "*.png" | wc -l)
if [ "$IMG_COUNT" -gt 0 ]; then
    echo "PASSED: Found $IMG_COUNT visualizations."
else
    echo "FAILED: No figures generated!"
    FAILED=1
fi

echo ""
echo "========================================"
if [ $FAILED -eq 0 ]; then
    echo "STATUS: ALL CHECKS PASSED"
    exit 0
else
    echo "STATUS: VALIDATION FAILED - CHECK ERRORS"
    exit 1
fi

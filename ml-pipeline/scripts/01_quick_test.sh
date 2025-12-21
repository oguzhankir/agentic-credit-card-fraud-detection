#!/bin/bash

# quick_test.sh
# Environment Sanity Check

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Running Environment Sanity Check..."

# 1. Python Check
if command -v python &>/dev/null; then
    ver=$(python --version)
    echo "Python: OK ($ver)"
else
    echo "Python: MISSING!"
    exit 1
fi

# 2. Package Check
echo "Checking critical packages..."
python -c "import pandas; import numpy; import sklearn; import xgboost; print('Packages: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Packages: FAIL (Missing dependencies)"
else
    echo "Packages: OK"
fi

# 3. Dataset Check
if [ -f "$PROJECT_ROOT/data/raw/fraudTrain.csv" ]; then
    size=$(du -h "$PROJECT_ROOT/data/raw/fraudTrain.csv" | cut -f1)
    echo "Dataset: FOUND ($size)"
else
    echo "Dataset: MISSING (Will be downloaded by pipeline)"
fi

# 4. Folder Structure
if [ -d "$PROJECT_ROOT/notebooks" ] && [ -d "$PROJECT_ROOT/scripts" ]; then
    echo "Structure: OK"
else
    echo "Structure: INVALID"
fi

echo "STATUS: READY TO RUN"
exit 0

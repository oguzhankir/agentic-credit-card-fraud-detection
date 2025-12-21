#!/bin/bash

# run_full_pipeline.sh
# Orchestrates the complete ML pipeline: Data -> Notebooks -> Artifacts -> Production

# Setup directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/artifacts/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/pipeline_$TIMESTAMP.log"

# Logging function
log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log "Starting ML Pipeline..."

# Step 1: Data Check
log "Step 1: Checking Data..."
if [ -f "$PROJECT_ROOT/data/raw/fraudTrain.csv" ]; then
    log "Dataset already exists, skipping download."
else
    log "Dataset missing. Running download script..."
    bash "$SCRIPT_DIR/02_download_data.sh" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "ERROR: Data download failed! Check log for details."
        exit 1
    fi
fi

# Step 2: Execute Notebooks
log "Step 2: Executing Jupyter Notebooks..."
NOTEBOOKS=("01_eda.ipynb" "02_feature_engineering.ipynb" "03_model_training.ipynb")

for nb in "${NOTEBOOKS[@]}"; do
    log "Running $nb..."
    jupyter nbconvert --to notebook --execute --inplace "$PROJECT_ROOT/notebooks/$nb" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "ERROR: Notebook $nb failed! Check log: $LOG_FILE"
        exit 1
    fi
    log "Successfully executed $nb."
done

# Step 3: Artifact Verification
log "Step 3: Verifying Artifacts..."
MODEL_COUNT=$(find "$PROJECT_ROOT/artifacts/models" -name "*.pkl" | wc -l)
if [ "$MODEL_COUNT" -lt 2 ]; then
    log "ERROR: Insufficient models found in artifacts/models/"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/artifacts/metrics/model_registry.json" ]; then
    log "ERROR: model_registry.json not found!"
    exit 1
fi

# Step 4: Export to Production
log "Step 4: Exporting to Production..."
python "$SCRIPT_DIR/export_to_production.py" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Production export failed!"
    exit 1
fi

# Success
log "FULL PIPELINE COMPLETED SUCCESSFULLY!"
log "Artifacts Created:"
log "- Models: $(ls $PROJECT_ROOT/artifacts/models/*.pkl | xargs -n 1 basename | tr '\n' ' ')"
log "- Metrics: $(ls $PROJECT_ROOT/artifacts/metrics/*.json | xargs -n 1 basename | tr '\n' ' ')"

END_TIME=$(date +%s)
START_TIME=$(date -j -f "%Y%m%d_%H%M%S" "$TIMESTAMP" +%s)
DURATION=$((END_TIME - START_TIME))
log "Total Time: $(($DURATION / 60)) minutes $(($DURATION % 60)) seconds"
log "Ready to start backend!"

exit 0

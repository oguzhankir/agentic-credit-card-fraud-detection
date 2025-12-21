import os
import shutil
import json
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def export_artifacts():
    # Resolve Paths
    SCRIPT_DIR = Path(__file__).resolve().parent
    ML_PIPELINE_ROOT = SCRIPT_DIR.parent
    PROJECT_ROOT = ML_PIPELINE_ROOT.parent
    
    ARTIFACTS_DIR = ML_PIPELINE_ROOT / "artifacts"
    METRICS_FILE = ARTIFACTS_DIR / "metrics" / "model_registry.json"
    MODELS_DIR = ARTIFACTS_DIR / "models"
    
    BACKEND_MODELS_DIR = PROJECT_ROOT / "backend" / "models"
    
    logger.info("Exporting Best Model to Production...")
    
    # 1. Validate Metrics Existence
    if not METRICS_FILE.exists():
        logger.error(f"Metrics file not found at {METRICS_FILE}. Run training first!")
        sys.exit(1)
        
    # 2. Identify Best Model
    with open(METRICS_FILE, "r") as f:
        registry = json.load(f)
        
    best_model_name = registry.get("best_model", "").lower()
    if not best_model_name:
        logger.error("Could not verify best model name from registry.")
        sys.exit(1)
        
    logger.info(f"Best Model Identified: {best_model_name.upper()}")
    
    # 3. Define Source Files
    source_model = MODELS_DIR / f"{best_model_name}_model.pkl"
    source_preprocessor = MODELS_DIR / "preprocessor.pkl"
    
    if not source_model.exists():
        logger.error(f"Model file missing: {source_model}")
        sys.exit(1)
        
    if not source_preprocessor.exists():
        logger.error(f"Preprocessor file missing: {source_preprocessor}")
        sys.exit(1)
        
    # 4. Prepare Destination
    BACKEND_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    dest_model = BACKEND_MODELS_DIR / "best_model.pkl"
    dest_preprocessor = BACKEND_MODELS_DIR / "preprocessor.pkl"
    dest_metadata = BACKEND_MODELS_DIR / "model_metadata.json"
    
    # 5. Copy Files
    try:
        shutil.copy2(source_model, dest_model)
        shutil.copy2(source_preprocessor, dest_preprocessor)
        shutil.copy2(METRICS_FILE, dest_metadata)
        
        # Verify Copy
        if dest_model.stat().st_size > 0 and dest_preprocessor.stat().st_size > 0:
            logger.info("Files Copied Successfully:")
            logger.info(f" - best_model.pkl ({dest_model.stat().st_size / 1024 / 1024:.2f} MB)")
            logger.info(f" - preprocessor.pkl ({dest_preprocessor.stat().st_size / 1024 / 1024:.2f} MB)")
            logger.info(f"Destination: {BACKEND_MODELS_DIR}")
            logger.info("Production export complete!")
        else:
            logger.error("File copy verification failed (size 0).")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Failed to copy artifacts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    export_artifacts()

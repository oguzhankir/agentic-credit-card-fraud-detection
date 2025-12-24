from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.api.routes import transactions, health, websocket
import logging
import time
import json
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backend/logs/app.log")
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models
    logger.info("Starting up Backend...")
    # Trigger model loading via singleton to warm up
    from backend.tools.model_predictor import ModelLoader
    try:
        ModelLoader().load()
    except Exception as e:
        logger.warning(f"Could not load models on startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Backend...")

app = FastAPI(
    title="Agentic Fraud Detection API",
    description="Backend for Fraud Detection System using LangChain Agents",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(transactions.router, prefix="/api", tags=["Transactions"])
app.include_router(websocket.router, tags=["WebSocket"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "duration_seconds": round(duration, 4)
    }
    
    # Write to API Usage Log
    try:
        log_path = Path(settings.api_usage_log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to file (JSON Lines format for appendability)
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
            
    except Exception as e:
        logger.error(f"Failed to write api log: {e}")
        
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host=settings.api_host, port=settings.api_port, reload=True)

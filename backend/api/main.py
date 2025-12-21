from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

# Import Routes
from backend.api.routes import transactions, health, websocket
from backend.services.websocket_manager import WebSocketManager

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fraud Detection Agentic AI",
    version="1.0.0",
    description="Real-time fraud detection with LLM agents"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for demo resilience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State Initialization
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Backend Services...")
    # Initialize WebSocket manager
    app.state.ws_manager = WebSocketManager()
    
    # Models are loaded lazily in tools/model_predictor.py via singleton
    # but we could force load here if needed:
    # from backend.tools.model_predictor import load_models
    # load_models()
    
    logger.info("Backend startup complete")

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

# Include Routers
app.include_router(transactions.router)
app.include_router(health.router)
app.include_router(websocket.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

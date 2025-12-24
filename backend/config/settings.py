from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from .env file."""
    
    # OpenAI
    openai_api_key: str
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 800
    
    # Model Paths
    model_path: str
    preprocessor_path: str
    metadata_path: str = "backend/models/model_metadata.json"
    
    # Artifact Paths
    merchant_freq_path: str
    category_freq_path: str
    
    # Logging
    log_level: str = "INFO"
    save_react_logs: bool = True
    react_log_dir: str = "backend/logs/react_logs"
    api_usage_log: str = "backend/logs/api_usage.json"
    
    # API Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = "backend/.env" 
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "ignore"
        protected_namespaces = ('settings_',)

settings = Settings()

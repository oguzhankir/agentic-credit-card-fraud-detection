from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

class Decision(BaseModel):
    action: Literal['APPROVE', 'BLOCK', 'MANUAL_REVIEW']
    reasoning: str
    confidence: int = Field(..., ge=0, le=100)
    key_factors: List[str]

class ModelPrediction(BaseModel):
    model_config = {"protected_namespaces": ()}
    fraud_probability: float = Field(..., ge=0, le=1)
    binary_prediction: Literal[0, 1]
    model_name: str
    ensemble_predictions: Optional[Dict[str, float]] = None
    consensus: str
    top_features: Optional[List[Dict[str, Any]]] = None

class AnomalyDetail(BaseModel):
    score: Optional[float] = 0
    is_anomaly: bool
    explanation: Optional[str] = ""
    severity: Optional[str] = None
    z_score: Optional[float] = None # Added based on usage
    value: Optional[float] = None

class Anomalies(BaseModel):
    amount: AnomalyDetail
    time: AnomalyDetail
    location: AnomalyDetail
    overall_risk: str
    total_anomaly_count: Optional[int] = 0
    red_flags: List[str]

class AnalysisResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    transaction_id: str
    analysis_timestamp: str
    decision: Decision
    risk_score: int = Field(..., ge=0, le=100)
    model_prediction: ModelPrediction
    anomalies: Anomalies
    react_steps: List[Dict[str, Any]]
    recommended_actions: List[str]
    processing_time_ms: int
    llm_calls_made: int
    total_tokens_used: int

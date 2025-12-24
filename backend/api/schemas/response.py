from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Decision(BaseModel):
    """Final decision schema"""
    action: str # APPROVE, BLOCK, MANUAL_REVIEW
    reasoning: str
    confidence: Optional[float] = 0.0
    key_factors: List[str] = []

class ReActStep(BaseModel):
    """Individual step in the ReAct process"""
    step: int
    type: str # THOUGHT, ACTION, OBSERVATION, DECISION
    agent: str
    content: Any
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    """Full response structure"""
    transaction_id: str
    timestamp: str
    decision: Decision
    react_steps: List[ReActStep]
    metrics: Dict[str, Any]

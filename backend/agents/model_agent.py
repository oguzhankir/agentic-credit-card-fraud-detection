from typing import Dict, Any
import json
from .base_agent import BaseAgent
from backend.config.langchain_config import MODEL_AGENT_SYSTEM_PROMPT
from backend.tools.model_predictor import predict_fraud_tool

class ModelAgent(BaseAgent):
    """
    Model Agent: Responsible for Fraud Prediction and Risk Scoring.
    """
    
    def __init__(self):
        tools = [predict_fraud_tool]
        super().__init__(name="model_expert", tools=tools, system_prompt=MODEL_AGENT_SYSTEM_PROMPT)
    
    def analyze(self, data: Dict) -> Dict:
        """
        Orchestrate model inference.
        """
        input_text = f"""
        Analyze the fraud risk for this transaction data:
        {json.dumps(data, default=str)}
        
        Tasks:
        1. Predict fraud probability (use valid transaction fields).
        """
        return self.execute(input_text)

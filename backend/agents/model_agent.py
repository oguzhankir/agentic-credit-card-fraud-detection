from backend.agents.base_agent import BaseAgent
from backend.config.langchain_config import MODEL_AGENT_PROMPT
from backend.tools.model_tools import (
    predict_fraud_tool,
    explain_features_tool,
    compare_models_tool
)
from typing import Dict, Any

class ModelAgent(BaseAgent):
    """Agent specialized in ML model predictions"""
    
    def __init__(self):
        tools = [
            predict_fraud_tool,
            explain_features_tool,
            compare_models_tool
        ]
        
        super().__init__(
            name="model_agent",
            tools=tools,
            prompt_template=MODEL_AGENT_PROMPT
        )
    
    def analyze(self, transaction_features: Dict[str, Any], customer_history: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run ML model and interpret predictions
        
        Args:
            transaction_features: Engineered features
            
        Returns:
            Dict with predictions and interpretation
        """
        input_text = f"""
        Analyze this transaction for fraud.
        
        TRANSACTION DATA:
        {transaction_features}
        
        CUSTOMER HISTORY:
        {customer_history}
        
        INSTRUCTIONS:
        1. Run 'predict_fraud' by passing TRANSACTION DATA to 'transaction_features' AND CUSTOMER HISTORY to 'customer_history'.
        2. Explain if the model probability indicates risk.
        """
        
        result = self.execute(input_text)
        
        return {
            "agent": "model_agent",
            "prediction": self._extract_prediction(result),
            "interpretation": result["output"],
            "react_steps": result["steps"],
            "confidence": self._extract_confidence(result["output"])
        }
    
    def _extract_prediction(self, result: Dict) -> Dict:
        """Extract prediction from agent result"""
        prediction = {
            "fraud_probability": 0.5,
            "model_name": "Unknown"
        }
        
        for step in result.get("steps", []):
            if step["type"] == "OBSERVATION":
                 try:
                    import json
                    content_str = step["content"].replace("'", '"').replace("True", "true").replace("False", "false")
                    obs = json.loads(content_str)
                    
                    if "fraud_probability" in obs: # From predict_fraud tool
                         return obs
                 except:
                    pass
        
        return prediction
    
    def _extract_confidence(self, output: str) -> str:
        """Extract confidence level from LLM output"""
        output_upper = output.upper()
        if "HIGH CONFIDENCE" in output_upper or "VERY CONFIDENT" in output_upper:
            return "HIGH"
        elif "LOW CONFIDENCE" in output_upper or "UNCERTAIN" in output_upper:
            return "LOW"
        else:
            return "MEDIUM"
    async def analyze_async(self, transaction_features: Dict[str, Any], customer_history: Dict[str, Any] = None, callbacks: list = None) -> Dict[str, Any]:
        """
        Async run ML model and interpret predictions
        """
        input_text = f"""
        Analyze this transaction for fraud with high precision.
        
        OFFICIAL TRANSACTION DATA:
        {transaction_features}
        
        CUSTOMER BEHAVIORAL HISTORY:
        {customer_history}
        
        REQUIRED ACTION:
        You MUST call the 'predict_fraud' tool. 
        - Pass 'OFFICIAL TRANSACTION DATA' as 'transaction_features'.
        - Pass 'CUSTOMER BEHAVIORAL HISTORY' as 'customer_history'.
        
        Interpret the resulting fraud_probability and decide if it is risky.
        """
        
        result = await self.aexecute(input_text, callbacks=callbacks)
        
        return {
            "agent": "model_agent",
            "prediction": self._extract_prediction(result),
            "interpretation": result["output"],
            "react_steps": result["steps"],
            "confidence": self._extract_confidence(result["output"])
        }

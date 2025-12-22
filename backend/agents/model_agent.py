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
        loc = transaction_features.get('location', {})
        hist = customer_history or {}
        
        # Ensure state is never None for strict validation
        state_val = loc.get('state') or 'NY'
        
        input_text = f"""
        Analyze this transaction for fraud with the 'predict_fraud' tool.
        
        FIELDS TO PASS:
        - amount: {transaction_features.get('amount')}
        - merchant: {transaction_features.get('merchant')}
        - category: {transaction_features.get('category')}
        - time: {transaction_features.get('time')}
        - lat: {loc.get('lat', 40.7128)}
        - long: {loc.get('long', -74.006)}
        - distance_from_home: {loc.get('distance_from_home', 0.0)}
        - state: {state_val}
        - city_pop: {transaction_features.get('city_pop', 10000)}
        - dob: {transaction_features.get('dob', '1980-01-01')}
        - gender: {transaction_features.get('gender', 'F')}
        - avg_amount: {hist.get('avg_amount', 100.0)}
        - std_amount: {hist.get('std_amount', 20.0)}
        - transaction_count: {hist.get('transaction_count', 50)}

        MANDATORY: Call 'predict_fraud' using EXACTLY the fields above.
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
                    import ast
                    # Observations are often string representations of dicts
                    content = step["content"]
                    if isinstance(content, str):
                        # Try ast.literal_eval first as it handles Python dicts/bools/none better
                        try:
                            obs = ast.literal_eval(content)
                        except:
                            import json
                            content_str = content.replace("'", '"').replace("True", "true").replace("False", "false")
                            obs = json.loads(content_str)
                    else:
                        obs = content
                        
                    if isinstance(obs, dict) and "fraud_probability" in obs:
                         return obs
                 except Exception as e:
                    logger.warning(f"Failed to extract prediction from observation: {e}")
        
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
        loc = transaction_features.get('location', {})
        hist = customer_history or {}
        
        # Ensure state is never None for strict validation
        state_val = loc.get('state') or 'NY'
        
        input_text = f"""
        Analyze this transaction for fraud with the 'predict_fraud' tool.
        
        FIELDS TO PASS:
        - amount: {transaction_features.get('amount')}
        - merchant: {transaction_features.get('merchant')}
        - category: {transaction_features.get('category')}
        - time: {transaction_features.get('time')}
        - lat: {loc.get('lat', 40.7128)}
        - long: {loc.get('long', -74.006)}
        - distance_from_home: {loc.get('distance_from_home', 0.0)}
        - state: {state_val}
        - city_pop: {transaction_features.get('city_pop', 10000)}
        - dob: {transaction_features.get('dob', '1980-01-01')}
        - gender: {transaction_features.get('gender', 'F')}
        - avg_amount: {hist.get('avg_amount', 100.0)}
        - std_amount: {hist.get('std_amount', 20.0)}
        - transaction_count: {hist.get('transaction_count', 50)}

        MANDATORY: Call 'predict_fraud' using EXACTLY the fields above.
        """
        
        result = await self.aexecute(input_text, callbacks=callbacks)
        
        return {
            "agent": "model_agent",
            "prediction": self._extract_prediction(result),
            "interpretation": result["output"],
            "react_steps": result["steps"],
            "confidence": self._extract_confidence(result["output"])
        }

from datetime import datetime
import json
import re
import logging
from typing import Dict, Any, List

from backend.agents.base_agent import BaseAgent
from backend.agents.data_agent import DataAgent
from backend.agents.model_agent import ModelAgent
from backend.config.langchain_config import COORDINATOR_PROMPT
from backend.tools.shared_tools import (
    calculate_risk_score_tool,
    generate_alert_tool
)

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """Main coordinator that orchestrates other agents"""
    
    def __init__(self):
        tools = [
            calculate_risk_score_tool,
            generate_alert_tool
        ]
        
        super().__init__(
            name="coordinator",
            tools=tools,
            prompt_template=COORDINATOR_PROMPT
        )
        
        # Initialize sub-agents
        self.data_agent = DataAgent()
        self.model_agent = ModelAgent()
    
    def analyze(self, transaction: Dict[str, Any], customer_history: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Full transaction analysis workflow
        
        Args:
            transaction: Complete transaction data
            customer_history: Customer history (optional)
            
        Returns:
            Complete analysis with decision
        """
        if customer_history is None:
            customer_history = {}
            
        all_steps = []
        
        # PHASE 1: Data Analysis
        logger.info("Phase 1: Data pattern analysis")
        data_result = self.data_agent.analyze(
            transaction=transaction,
            customer_history=customer_history
        )
        all_steps.extend(data_result['react_steps'])
        
        # PHASE 2: Model Prediction
        logger.info("Phase 2: ML model prediction")
        # Ensure transaction has features needed for model
        # For simplicity, pass the whole transaction dict as features
        model_result = self.model_agent.analyze(
            transaction_features=transaction,
            customer_history=customer_history
        )
        all_steps.extend(model_result['react_steps'])
        
        # PHASE 3: Coordinator Decision
        logger.info("Phase 3: Final decision making")
        
        # Safely get anomaly data
        anomalies = data_result.get('anomalies', {})
        amount_anom = anomalies.get('amount', {})
        # If amount_anom is just {'is_anomaly': False}, convert to string properly or handle it
        
        # Prepare data for prompt
        model_pred = model_result.get('prediction', {})
        data_anomalies = data_result.get('anomalies', {})
        
        input_text = f"""
        Based on analysis from specialized agents, make the final decision.
        
        CRITICAL INSTRUCTIONS:
        1. You MUST call the 'calculate_risk_score' tool with these EXACT parameters:
           - model_prediction: {json.dumps(model_pred)}
           - anomalies: {json.dumps(data_anomalies)}
        
        2. After getting the risk score, make your decision:
           - If risk_score > 90: BLOCK
           - If risk_score < 30: APPROVE
           - Otherwise: MANUAL_REVIEW
        
        DATA AGENT FINDINGS:
        {data_result.get('interpretation', 'No interpretation')}
        
        Anomalies detected:
        - Amount: {amount_anom}
        - Time: {anomalies.get('time', {})}
        - Location: {anomalies.get('location', {})}
        - Overall Risk: {data_result.get('overall_risk', 'UNKNOWN')}
        
        MODEL AGENT FINDINGS:
        {model_result.get('interpretation', 'No interpretation')}
        
        Prediction:
        - Fraud Probability: {model_pred.get('fraud_probability', 0):.2%}
        - Model: {model_pred.get('model_name', 'Unknown')}
        - Confidence: {model_result.get('confidence', 'UNKNOWN')}
        
        Provide final decision in this EXACT JSON format:
        {{
            "action": "APPROVE",
            "reasoning": "Clear explanation here",
            "confidence": 85,
            "key_factors": ["factor1", "factor2"],
            "recommended_actions": ["action1"]
        }}
        
        IMPORTANT: "confidence" MUST be an integer number (0-100), NOT a string.
        """
        
        coordinator_result = self.execute(input_text)
        all_steps.extend(coordinator_result['steps'])
        
        # Parse final decision
        decision = self._parse_decision(coordinator_result['output'])
        
        # Add DECISION step manually for visualization if not in steps
        all_steps.append({
            "step": len(all_steps) + 1,
            "type": "DECISION",
            "agent": "coordinator",
            "content": f"Decision: {decision['action']}. {decision['reasoning']}",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "llm_used": True,
                "llm_purpose": "DECISION",
                "action": decision['action'],
                "confidence": decision['confidence']
            }
        })
        
        return {
            "transaction_id": transaction.get('transaction_id', 'unknown'),
            "analysis_timestamp": datetime.now().isoformat(),
            "decision": decision,
            "risk_score": decision.get('confidence', 0),
            "model_prediction": {
                "fraud_probability": model_result.get('prediction', {}).get('fraud_probability', 0.0),
                "binary_prediction": model_result.get('prediction', {}).get('binary_prediction', 0),
                "model_name": model_result.get('prediction', {}).get('model_name', "Unknown"),
                "consensus": model_result.get('prediction', {}).get('consensus', "Single Model"),
                "ensemble_predictions": model_result.get('prediction', {}).get('ensemble_predictions', {})
            },
            "anomalies": {
                "amount": anomalies.get('amount', {"is_anomaly": False, "score": 0.0}),
                "time": anomalies.get('time', {"is_anomaly": False, "score": 0.0}),
                "location": anomalies.get('location', {"is_anomaly": False, "score": 0.0}),
                "overall_risk": data_result.get("overall_risk", "UNKNOWN"),
                "red_flags": data_result.get("anomalies", {}).get("red_flags", []),
                "total_anomaly_count": data_result.get("anomalies", {}).get("total_anomalies", 0)
            },
            "react_steps": all_steps,
            "recommended_actions": decision.get('recommended_actions', []),
            "processing_time_ms": 0, # Will be calculated by ReActEngine
            "llm_calls_made": 1, # Placeholder
            "total_tokens_used": 100 # Placeholder
        }
    
    def _parse_decision(self, output: str) -> Dict[str, Any]:
        """Parse final decision from LLM output"""
        try:
            # Extract JSON
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
                
                # Validate required fields
                required = ['action', 'reasoning', 'confidence']
                if all(k in decision for k in required):
                    return decision
            
            # Fallback
            return {
                "action": "MANUAL_REVIEW",
                "reasoning": output[:200] + "...",
                "confidence": 50,
                "key_factors": [],
                "recommended_actions": ["Review transaction manually"]
            }
            
        except Exception as e:
            logger.error(f"Failed to parse decision: {e}")
            return {
                "action": "MANUAL_REVIEW",
                "reasoning": "Error in decision parsing via LLM.",
                "confidence": 0,
                "key_factors": [],
                "recommended_actions": []
            }

from datetime import datetime
import json
import re
import logging
from typing import Dict, Any, List

from backend.agents.base_agent import BaseAgent
from backend.agents.data_agent import DataAgent
from backend.agents.model_agent import ModelAgent
from backend.config.langchain_config import COORDINATOR_PROMPT

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """Main coordinator that orchestrates other agents"""
    
    def __init__(self):
        # NO TOOLS! Direct decision making
        super().__init__(
            name="coordinator",
            tools=[],  # EMPTY!
            prompt_template=COORDINATOR_PROMPT
        )
        
        # Initialize sub-agents
        self.data_agent = DataAgent()
        self.model_agent = ModelAgent()
    
    def _calculate_risk_score(self, model_pred: Dict, anomalies: Dict) -> int:
        """Calculate risk score directly without LLM"""
        fraud_prob = model_pred.get('fraud_probability', 0)
        amount_z = anomalies.get('amount_anomaly', {}).get('z_score', 0)
        total_anomalies = anomalies.get('total_anomalies', 0)
        
        # If Z-score is EXTREME (>1000), model prediction is unreliable
        # because model never saw such values in training
        if abs(amount_z) > 1000:
            # Ignore model, use pure anomaly-based risk
            risk_score = 99
            logger.warning(f"EXTREME Z-score detected: {amount_z:.2f}. Model unreliable, using anomaly-only risk=99")
        elif abs(amount_z) > 100:
            # Very high Z-score: Model less reliable, weight anomalies more
            model_risk = fraud_prob * 100 * 0.2  # Reduce model weight
            anomaly_risk = min(amount_z / 50, 1) * 60  # Increase anomaly weight
            count_risk = total_anomalies * 10
            risk_score = int(min(99, model_risk + anomaly_risk + count_risk))
            logger.info(f"High Z-score {amount_z:.2f}: Reduced model weight, risk={risk_score}")
        else:
            # Normal case: Balanced weighting
            model_risk = fraud_prob * 100 * 0.4
            anomaly_risk = min(amount_z / 100, 1) * 40
            count_risk = total_anomalies * 10
            risk_score = int(min(99, model_risk + anomaly_risk + count_risk))
        
        return risk_score
    
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
        
        # Prepare data for prompt - serialize to JSON for clarity
        model_pred = model_result.get('prediction', {})
        data_anomalies = data_result.get('anomalies', {})
        
        input_text = f"""
        Based on analysis from specialized agents, make the final decision.
        
        CRITICAL INSTRUCTIONS:
        1. You MUST call 'calculate_risk_score' tool with these parameters:
           model_prediction={json.dumps(model_pred)}
           anomalies={json.dumps(data_anomalies)}
        
        2. After getting the risk score, make your decision based on the score.
        
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
        
        Provide final decision in JSON format (confidence MUST be integer 0-100):
        {{
            "action": "APPROVE/BLOCK/MANUAL_REVIEW",
            "reasoning": "Clear explanation",
            "confidence": 85,
            "key_factors": ["factor1", "factor2"],
            "recommended_actions": ["action1"]
        }}
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
    async def analyze_async(self, transaction: Dict[str, Any], customer_history: Dict[str, Any] = None, callbacks: list = None) -> Dict[str, Any]:
        """
        Async Full transaction analysis workflow
        """
        if customer_history is None:
            customer_history = {}
            
        all_steps = []
        
        # PHASE 1: Data Analysis
        logger.info("Phase 1: Data pattern analysis")
        
        # Set agent context for callbacks
        if callbacks:
            for cb in callbacks:
                if hasattr(cb, 'set_agent'):
                    cb.set_agent("data_agent")
        
        data_result = await self.data_agent.analyze_async(
            transaction=transaction,
            customer_history=customer_history,
            callbacks=callbacks
        )
        all_steps.extend(data_result['react_steps'])
        
        # PHASE 2: Model Prediction
        logger.info("Phase 2: ML model prediction")
        
        # Set agent context for callbacks
        if callbacks:
            for cb in callbacks:
                if hasattr(cb, 'set_agent'):
                    cb.set_agent("model_agent")
        
        # Ensure transaction has features needed for model
        model_result = await self.model_agent.analyze_async(
            transaction_features=transaction,
            customer_history=customer_history,
            callbacks=callbacks
        )
        all_steps.extend(model_result['react_steps'])
        
        # PHASE 3: Coordinator Decision
        logger.info("Phase 3: Final decision making")
        
        # Set agent context for callbacks
        if callbacks:
            for cb in callbacks:
                if hasattr(cb, 'set_agent'):
                    cb.set_agent("coordinator")
        
        # Safely get anomaly data
        anomalies = data_result.get('anomalies', {})
        model_pred = model_result.get('prediction', {})
        
        # CALCULATE RISK DIRECTLY (NO TOOL!)
        risk_score = self._calculate_risk_score(model_pred, anomalies)
        logger.info(f"Calculated risk score: {risk_score}/100")
        
        # Determine action based on risk
        if risk_score > 90:
            action = "BLOCK"
            reasoning = f"CRITICAL FRAUD RISK (score: {risk_score}/100). Extreme anomalies detected."
        elif risk_score > 50:
            action = "MANUAL_REVIEW"
            reasoning = f"SUSPICIOUS ACTIVITY (score: {risk_score}/100). Manual verification required."
        else:
            action = "APPROVE"
            reasoning = f"LOW RISK (score: {risk_score}/100). Transaction appears legitimate."
        
        amount_z = anomalies.get('amount_anomaly', {}).get('z_score', 0)
        
        # Build key factors
        key_factors = []
        if amount_z > 1000:
            key_factors.append(f"NUCLEAR RISK: Amount Z-score {amount_z:.0f}")
        elif amount_z > 3:
            key_factors.append(f"Amount Z-score: {amount_z:.2f}")
        
        distance = anomalies.get('location_anomaly', {}).get('distance_km', 0)
        if distance > 1000:
            key_factors.append(f"Distance: {distance:.0f} km")
        
        fraud_prob = model_pred.get('fraud_probability', 0)
        key_factors.append(f"Model fraud probability: {fraud_prob:.2%}")
        
        # Create decision directly (NO AGENT!)
        decision = {
            "action": action,
            "reasoning": reasoning + " " + ". ".join(key_factors),
            "confidence": risk_score,
            "key_factors": key_factors,
            "recommended_actions": [
                "Block transaction immediately" if action == "BLOCK" else
                "Manual review required" if action == "MANUAL_REVIEW" else
                "Approve transaction"
            ]
        }
        
        logger.info(f"Decision: {action} (confidence: {risk_score})")
        
        # Add DECISION step for visualization
        decision_step = {
            "step": len(all_steps) + 1,
            "type": "DECISION",
            "agent": "coordinator",
            "content": f"Decision: {decision['action']}. {decision['reasoning']}",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "llm_used": False,  # NO LLM! Direct Python decision
                "llm_purpose": "NONE",
                "action": decision['action'],
                "confidence": decision['confidence'],
                "risk_score": risk_score
            }
        }
        all_steps.append(decision_step)
        
        # Emit decision step via callback
        if callbacks:
             for cb in callbacks:
                 if hasattr(cb, 'ws_manager'):
                     import asyncio
                     await cb.ws_manager.send_to_connection(cb.connection_id, {
                        "type": "react_step",
                        "data": decision_step
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

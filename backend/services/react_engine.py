from datetime import datetime
import logging
from typing import Dict, Any, List, Generator

# Import custom modules
from backend.services.llm_service import LLMService
from backend.tools.transaction_analyzer import calculate_all_anomalies
from backend.tools.model_predictor import predict_fraud
from backend.tools.risk_scorer import calculate_risk_score, apply_business_rules
from backend.tools.alert_generator import generate_alert
from backend.tools.report_generator import generate_analysis_report

logger = logging.getLogger(__name__)

class ReActEngine:
    def __init__(self):
        self.llm = LLMService()
        self.history = []
        
    def run(self, transaction: Dict[str, Any], customer_history: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Execute full analysis synchronously.
        """
        self.history = [] # Clear previous steps
        start_time = datetime.now()
        
        # Generator aggregation
        for step in self.stream_analysis(transaction, customer_history):
            if step['type'] == 'react_step':
                self.history.append(step['data'])
            elif step['type'] == 'decision':
                return step['data']
        
        return {} # Should not reach here

    def stream_analysis(self, transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Execute analysis yielding steps for real-time visualization.
        """
        start_ts = datetime.now()
        
        # --- PHASE 1: PLANNING (LLM) ---
        planning_prompt = f"""
        Analyze this transaction:
        - Amount: ${transaction.get('amount')}
        - Merchant: {transaction.get('merchant')}
        - Location Diff: {transaction.get('location', {}).get('distance_from_home')} km
        
        Plan the investigation steps to detect fraud.
        """
        
        plan_text = self.llm.call(planning_prompt, purpose="PLANNING", agent="coordinator")
        
        step1 = self._make_step(1, "THOUGHT", "coordinator", plan_text, {"llm_used": True})
        yield {"type": "react_step", "data": step1}
        
        # --- PHASE 2: DATA ANALYSIS (PYTHON + LLM) ---
        # Action: Python Calc
        anomalies = calculate_all_anomalies(transaction, customer_history)
        
        step2 = self._make_step(2, "ACTION", "data", "Calculated statistical anomalies (Pure Python)", {"llm_used": False, "results": anomalies})
        yield {"type": "react_step", "data": step2}
        
        # Observation: LLM Interpret
        interp_prompt = f"Interpret these anomalies: {anomalies}"
        interp_text = self.llm.call(interp_prompt, purpose="INTERPRETATION", agent="data")
        
        step3 = self._make_step(3, "OBSERVATION", "data", interp_text, {"llm_used": True})
        yield {"type": "react_step", "data": step3}
        
        # --- PHASE 3: MODEL PREDICTION (PYTHON + LLM) ---
        # Action: Run Models
        try:
            prediction = predict_fraud(transaction)
        except Exception as e:
            prediction = {"fraud_probability": 0, "error": str(e)}
            
        step4 = self._make_step(4, "ACTION", "model", "Executed ML Model Ensemble", {"llm_used": False, "prediction": prediction})
        yield {"type": "react_step", "data": step4}
        
        # Observation: LLM Interpret
        model_prompt = f"Interpret these ML predictions: {prediction}"
        model_text = self.llm.call(model_prompt, purpose="INTERPRETATION", agent="model")
        
        step5 = self._make_step(5, "OBSERVATION", "model", model_text, {"llm_used": True})
        yield {"type": "react_step", "data": step5}
        
        # --- PHASE 4: RISK SCORING (PYTHON) ---
        business_rules = apply_business_rules(transaction, customer_history)
        risk_result = calculate_risk_score(prediction, anomalies, business_rules)
        
        step6 = self._make_step(6, "ACTION", "coordinator", "Calculated Final Risk Score", {"llm_used": False, "risk": risk_result})
        yield {"type": "react_step", "data": step6}
        
        # --- PHASE 5: DECISION (LLM) ---
        decision_prompt = f"""
        Final Decision Required.
        Risk Score: {risk_result['risk_score']}
        Anomalies: {anomalies}
        Model: {prediction}
        
        Decide: APPROVE, BLOCK, or MANUAL_REVIEW. 
        Format: JSON {{ "action": "...", "reasoning": "...", "confidence": 95, "key_factors": [] }}
        """
        
        decision_json_str = self.llm.call(decision_prompt, purpose="DECISION", agent="coordinator")
        
        # Parse JSON safely
        import json
        try:
            decision_data = json.loads(decision_json_str)
        except:
            # Fallback simple parsing
            decision_data = {
                "action": "MANUAL_REVIEW", 
                "reasoning": decision_json_str, 
                "confidence": 50,
                "key_factors": ["Parsing Error"]
            }
            
        step7 = self._make_step(7, "DECISION", "coordinator", f"{decision_data.get('action')}: {decision_data.get('reasoning')}", {"llm_used": True, "confidence": decision_data.get('confidence')})
        yield {"type": "react_step", "data": step7}
        
        # --- FINAL OUTPUT ---
        processing_time = int((datetime.now() - start_ts).total_seconds() * 1000)
        
        full_result = {
            'transaction_id': transaction.get('transaction_id', 'unknown'),
            'analysis_timestamp': datetime.now().isoformat(),
            'decision': decision_data,
            'risk_score': risk_result['risk_score'],
            'model_prediction': prediction,
            'anomalies': anomalies,
            'react_steps': [step1, step2, step3, step4, step5, step6, step7],
            'recommended_actions': generate_alert(decision_data, transaction, risk_result['risk_score'])['recommended_actions'],
            'processing_time_ms': processing_time,
            'llm_calls_made': 4,
            'total_tokens_used': 0 # TODO: Aggregated from steps
        }
        
        yield {"type": "decision", "data": full_result}

    def _make_step(self, step_num: int, type_: str, agent: str, content: str, metadata: Dict) -> Dict:
        return {
            "step": step_num,
            "type": type_,
            "agent": agent,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }

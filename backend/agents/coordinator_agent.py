import json
import logging
import textwrap
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """
    Orchestrates the Fraud Detection process using a Hybrid approach:
    - LLM: Planning, Interpretation, Decision
    - Python: Calculations, Data Processing, Model Inference
    """
    def __init__(self):
        super().__init__(name="coordinator")
        # Load Real Models
        try:
            from ..services.model_service import ModelService
            self.model_service = ModelService()
        except Exception as e:
            logger.error(f"Failed to initialize ModelService: {e}")
            self.model_service = None

    def analyze_transaction(self, transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for analyzing a single transaction.
        Executes the 5-Phase ReAct Loop.
        """
        self.clear_history()
        start_time = datetime.now()
        
        # --- PHASE 1: INITIAL THOUGHT (LLM - PLANNING) ---
        planning_prompt = f"""
        Analyze this new transaction and plan the investigation strategy:

        Transaction Details:
        - Amount: ${transaction.get('amount')}
        - Time: {transaction.get('time')}
        - Merchant: {transaction.get('merchant')}
        - Distance from home: {transaction.get('location', {}).get('distance_from_home')} km

        Customer History:
        - Average amount: ${customer_history.get('avg_amount')}
        - Usual shopping hours: {customer_history.get('usual_hours')}

        Question: What aspects should we investigate first to determine if this is fraud?
        Think step by step and prioritize.
        """
        
        plan_response = self.call_llm(planning_prompt, purpose='PLANNING')
        
        self.log_step(
            step_type='THOUGHT',
            content=plan_response,
            metadata={
                'llm_used': True,
                'llm_purpose': 'PLANNING',
                'phase': 'initial_assessment'
            }
        )

        # --- PHASE 2: DATA ANALYSIS (HYBRID) ---
        # 2a. Python Calculations (NO LLM)
        anomalies = self._calculate_anomalies(transaction, customer_history)
        
        self.log_step(
            step_type='ACTION',
            content='Calculated transaction anomalies using statistical methods',
            metadata={
                'llm_used': False,
                'calculations': ['z-score', 'time_check', 'distance_check'],
                'results': anomalies
            }
        )
        
        # 2b. LLM Interpretation
        interpretation_prompt = f"""
        I have analyzed this transaction and found the following anomalies:

        1. Amount Anomaly:
           - Transaction: ${transaction.get('amount')}
           - Customer's average: ${customer_history.get('avg_amount')}
           - Z-score: {anomalies['amount']['z_score']:.2f} standard deviations above normal
           - Is Anomaly: {anomalies['amount']['is_anomaly']}
           
        2. Time Anomaly:
           - Transaction hour: {datetime.fromisoformat(transaction['time']).hour}
           - Is Night: {anomalies['time']['is_night']}
           - Usual hours: {customer_history.get('usual_hours')}
           
        3. Location Anomaly:
           - Distance from home: {transaction.get('location', {}).get('distance_from_home')} km
           - Is Far: {anomalies['location']['is_far']}

        Question: Interpret these anomalies. What do they indicate about fraud risk?
        Consider each factor and their combination.
        """
        
        interpretation_response = self.call_llm(interpretation_prompt, purpose='INTERPRETATION')
        
        self.log_step(
            step_type='OBSERVATION',
            content=interpretation_response,
            metadata={
                'llm_used': True,
                'llm_purpose': 'INTERPRETATION',
                'phase': 'data_analysis',
                'anomalies_found': sum(1 for k, v in anomalies.items() if v.get('is_anomaly') or v.get('is_far') or v.get('is_night'))
            }
        )

        # --- PHASE 3: MODEL PREDICTION (HYBRID) ---
        # 3a. Real Prediction using ModelService
        if self.model_service:
            predictions = self.model_service.predict(transaction, customer_history)
        else:
            predictions = {"ensemble_avg": 0, "error": "ModelService unavailable"}
        
        self.log_step(
            step_type='ACTION',
            content='Executed ML models to predict fraud probability',
            metadata={
                'llm_used': False,
                'models_used': list(predictions.keys()),
                'predictions': predictions
            }
        )
        
        # 3b. LLM Interpretation of Models
        model_prompt = f"""
        The ML models have made the following predictions:

        Predictions: {json.dumps(predictions)}

        Question: Interpret these model predictions. Should we trust this high probability?
        What does the strong consensus between models tell us?
        """
        
        model_interpretation = self.call_llm(model_prompt, purpose='INTERPRETATION')
        
        self.log_step(
            step_type='OBSERVATION',
            content=model_interpretation,
            metadata={
                'llm_used': True,
                'llm_purpose': 'INTERPRETATION',
                'phase': 'model_prediction',
                'avg_probability': predictions.get('ensemble_avg', 0)
            }
        )

        # --- PHASE 4: RISK SCORING (PYTHON ONLY) ---
        risk_score_data = self._calculate_risk_score(predictions, anomalies, transaction)
        
        self.log_step(
            step_type='ACTION',
            content=f"Calculated risk score: {risk_score_data['total']}/100",
            metadata={
                'llm_used': False,
                'breakdown': risk_score_data
            }
        )

        # --- PHASE 5: FINAL DECISION (LLM - DECISION) ---
        decision_prompt = f"""
        Based on all analysis, make a final fraud detection decision:

        Data Analysis Summary:
        - Amount Z-Score: {anomalies['amount']['z_score']:.2f}
        - Anomaly Interpretation: {interpretation_response[:200]}...

        Model Predictions:
        - Average Fraud Probability: {predictions['ensemble_avg']:.2f}
        - Consensus: {predictions['consensus']}

        Risk Score: {risk_score_data['total']}/100

        Your Task:
        Make a decision: APPROVE, BLOCK, or MANUAL_REVIEW

        Provide your response in this EXACT JSON format:
        {{
          "action": "BLOCK",
          "reasoning": "Explain why in 2-3 sentences",
          "confidence": 95,
          "key_factors": ["factor1", "factor2", "factor3"],
          "next_steps": ["step1", "step2"]
        }}
        """
        
        decision_json_text = self.call_llm(decision_prompt, purpose='DECISION')
        
        # Robust JSON parsing
        try:
            decision_json_text = decision_json_text.strip()
            if "```json" in decision_json_text:
                decision_json_text = decision_json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in decision_json_text:
                decision_json_text = decision_json_text.split("```")[1].split("```")[0].strip()
                
            decision = json.loads(decision_json_text)
        except Exception as e:
            logger.error(f"Failed to parse decision JSON: {e}")
            decision = {
                "action": "MANUAL_REVIEW",
                "reasoning": "Failed to parse LLM decision, defaulting to manual review.",
                "confidence": 0,
                "key_factors": ["System Error"],
                "next_steps": ["Review Logs"]
            }

        self.log_step(
            step_type='DECISION',
            content=decision['reasoning'],
            metadata={
                'llm_used': True,
                'llm_purpose': 'DECISION',
                'action': decision['action'],
                'confidence': decision['confidence'],
                'phase': 'final_decision'
            }
        )

        # --- FINAL PACKAGING ---
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'transaction_id': transaction.get('transaction_id', 'unknown'),
            'decision': decision,
            'risk_score': risk_score_data['total'],
            'model_prediction': {
                'fraud_probability': predictions['ensemble_avg'],
                'consensus': predictions['consensus']
            },
            'anomalies': anomalies,
            'react_steps': self.get_history(),
            'recommended_actions': decision.get('next_steps', []),
            'processing_time_ms': processing_time_ms,
            'llm_calls_made': 4, # approximated
            # 'total_tokens_used': ... (would need to aggregate from history/logs)
        }

    # --- HELPER METHODS (PURE PYTHON) ---
    def _calculate_anomalies(self, tx: Dict, hist: Dict) -> Dict:
        """Pure Python calculation of statistical anomalies."""
        amt = tx.get('amount', 0)
        avg = hist.get('avg_amount', 1)
        # Simple z-score approximation (assuming std dev is related to avg if not provided)
        std_dev = hist.get('std_amount', avg * 0.5) 
        z_score = (amt - avg) / std_dev if std_dev > 0 else 0
        
        tx_time = datetime.fromisoformat(tx['time'])
        hour = tx_time.hour
        is_night = 0 <= hour < 6
        
        dist = tx.get('location', {}).get('distance_from_home', 0)
        
        return {
            'amount': {
                'z_score': z_score,
                'is_anomaly': z_score > 3,
                'value': amt,
                'baseline': avg
            },
            'time': {
                'hour': hour,
                'is_night': is_night,
                'is_unusual': is_night # Simple rule
            },
            'location': {
                'distance': dist,
                'is_far': dist > 80
            }
        }

    def _mock_model_prediction(self, tx: Dict, anomalies: Dict) -> Dict:
        """
        Simulate ML model output. 
        In production, this would load .pkl files and run predict_proba().
        """
        # Logic to simulate realistic probability based on anomalies for demo purposes
        base_prob = 0.05
        
        if anomalies['amount']['is_anomaly']: base_prob += 0.4
        if anomalies['location']['is_far']: base_prob += 0.3
        if anomalies['time']['is_night']: base_prob += 0.15
        
        prob = min(0.99, base_prob)
        
        # Add some variance for different models
        return {
            'xgboost': min(0.99, prob + 0.02),
            'lightgbm': max(0.01, prob - 0.03),
            'randomforest': prob,
            'ensemble_avg': prob,
            'consensus': 'HIGH_AGREEMENT' if prob > 0.8 or prob < 0.2 else 'MODERATE_AGREEMENT'
        }

    def _calculate_risk_score(self, predictions: Dict, anomalies: Dict, tx: Dict) -> Dict:
        """Pure Python Risk Scoring Engine."""
        base_score = predictions['ensemble_avg'] * 50
        
        anomaly_score = 0
        if anomalies['amount']['is_anomaly']: anomaly_score += 15
        if anomalies['time']['is_night']: anomaly_score += 10
        if anomalies['location']['is_far']: anomaly_score += 15
        
        business_score = 0
        if tx.get('amount', 0) > 5000: business_score += 10
        
        total = min(100, int(base_score + anomaly_score + business_score))
        
        return {
            'base_score': base_score,
            'anomaly_score': anomaly_score,
            'business_score': business_score,
            'total': total
        }

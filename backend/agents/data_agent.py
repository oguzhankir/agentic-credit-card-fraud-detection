from backend.agents.base_agent import BaseAgent
from backend.config.langchain_config import DATA_AGENT_PROMPT
from backend.tools.data_tools import (
    detect_anomalies_tool,
    check_velocity_tool
    # analyze_patterns is effectively covered by detect_anomalies for MVP
)
from typing import Dict, Any

class DataAgent(BaseAgent):
    """Agent specialized in transaction pattern analysis"""
    
    def __init__(self):
        tools = [
            detect_anomalies_tool,
            check_velocity_tool
        ]
        
        super().__init__(
            name="data_agent",
            tools=tools,
            prompt_template=DATA_AGENT_PROMPT
        )
    
    def analyze(self, transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transaction patterns and detect anomalies
        
        Args:
            transaction: Transaction data
            customer_history: Customer baseline data
            
        Returns:
            Dict with anomalies and explanations
        """
        # Prepare input for LLM
        # Ensure 'hour' exists
        if 'hour' not in transaction:
            try:
                # Mock extracting hour if time string 'HH:MM:SS'
                time_str = transaction.get('time', '12:00:00')
                transaction['hour'] = int(time_str.split(':')[0])
            except:
                transaction['hour'] = 12

        location = transaction.get('location', {})
        distance = transaction.get('distance_km') or (location.get('distance_from_home', 0) if isinstance(location, dict) else 0)

        input_text = f"""
        Analyze this transaction for suspicious patterns. Use COMMON SENSE:
        For example, a high-distance transaction for a low-cost category like 'food_dining'
        with a massive amount is almost certainly fraud.

        Transaction:
        - Amount: ${transaction.get('amount')}
        - Time: {transaction.get('time')} (hour: {transaction.get('hour')})
        - Merchant: {transaction.get('merchant')}
        - Category: {transaction.get('category')}
        - Distance from home: {distance} km
        
        Customer Baseline:
        - Average amount: ${customer_history.get('avg_amount', 120)}
        - Std deviation: ${customer_history.get('std_amount', 50)}
        - Usual shopping hours: {customer_history.get('usual_hours', [])}
        - Transaction count: {customer_history.get('transaction_count', 0)}
        
        Tasks:
        1. Use 'detect_anomalies' tool to calculate z-scores and anomaly flags.
        2. Use 'check_velocity' tool to detect unusual transaction frequency.
        
        After using tools, provide interpretation:
        - Which anomalies are most concerning?
        - What do these patterns suggest about fraud risk?
        - Rate overall suspicion level: LOW/MEDIUM/HIGH/CRITICAL
        
        Respond with your analysis and final assessment.
        """
        
        # Execute agent
        result = self.execute(input_text)
        
        # Parse result
        return {
            "agent": "data_agent",
            "anomalies": self._extract_anomalies(result),
            "interpretation": result["output"],
            "react_steps": result["steps"],
            "overall_risk": self._extract_risk_level(result["output"])
        }
    
    def _extract_anomalies(self, result: Dict) -> Dict:
        """Extract anomaly data from agent result"""
        # Parse intermediate steps to find tool outputs
        anomalies = {
            "amount": {"is_anomaly": False},
            "time": {"is_anomaly": False},
            "location": {"is_anomaly": False}
        }
        
        for step in result.get("steps", []):
            if step["type"] == "OBSERVATION":
                # Parse tool output
                try:
                    import json
                    # Observations might be string representations of dicts or actual dicts depending on BaseAgent logic
                    content_str = step["content"].replace("'", '"').replace("True", "true").replace("False", "false")
                    obs = json.loads(content_str)
                    
                    if "amount_anomaly" in obs: # It's from detect_anomalies
                        return obs # Return the full structured anomaly object
                except:
                    pass
        
        return anomalies
    
    def _extract_risk_level(self, output: str) -> str:
        """Extract risk level from LLM output"""
        output_upper = output.upper()
        if "CRITICAL" in output_upper:
            return "CRITICAL"
        elif "HIGH" in output_upper:
            return "HIGH"
        elif "MEDIUM" in output_upper:
            return "MEDIUM"
        else:
            return "LOW"
    async def analyze_async(self, transaction: Dict[str, Any], customer_history: Dict[str, Any], callbacks: list = None) -> Dict[str, Any]:
        """
        Async analyze transaction patterns and detect anomalies
        """
        # Prepare input for LLM
        # Ensure 'hour' exists
        if 'hour' not in transaction:
            try:
                # Mock extracting hour if time string 'HH:MM:SS'
                time_str = transaction.get('time', '12:00:00')
                transaction['hour'] = int(time_str.split(':')[0])
            except:
                transaction['hour'] = 12

        location = transaction.get('location', {})
        distance = transaction.get('distance_km') or (location.get('distance_from_home', 0) if isinstance(location, dict) else 0)

        input_text = f"""
        Analyze this transaction for suspicious patterns. Use COMMON SENSE:
        For example, a high-distance transaction for a low-cost category like 'food_dining'
        with a massive amount is almost certainly fraud.

        Transaction:
        - Amount: ${transaction.get('amount')}
        - Time: {transaction.get('time')} (hour: {transaction.get('hour')})
        - Merchant: {transaction.get('merchant')}
        - Category: {transaction.get('category')}
        - Distance from home: {distance} km
        
        Customer Baseline:
        - Average amount: ${customer_history.get('avg_amount', 120)}
        - Std deviation: ${customer_history.get('std_amount', 50)}
        - Usual shopping hours: {customer_history.get('usual_hours', [])}
        - Transaction count: {customer_history.get('transaction_count', 0)}
        
        Tasks:
        1. Use 'detect_anomalies' tool to calculate z-scores and anomaly flags.
        2. Use 'check_velocity' tool to detect unusual transaction frequency.
        
        After using tools, provide interpretation:
        - Which anomalies are most concerning?
        - What do these patterns suggest about fraud risk?
        - Rate overall suspicion level: LOW/MEDIUM/HIGH/CRITICAL
        
        Respond with your analysis and final assessment.
        """
        
        # Execute agent async
        result = await self.aexecute(input_text, callbacks=callbacks)
        
        # Parse result
        return {
            "agent": "data_agent",
            "anomalies": self._extract_anomalies(result),
            "interpretation": result["output"],
            "react_steps": result["steps"],
            "overall_risk": self._extract_risk_level(result["output"])
        }

from typing import Dict, Any
import json
from .base_agent import BaseAgent
from backend.config.langchain_config import DATA_AGENT_SYSTEM_PROMPT
from backend.tools.feature_engineer import engineer_features_tool
from backend.tools.anomaly_detector import detect_anomalies_tool

class DataAgent(BaseAgent):
    """
    Data Agent: Responsible for Feature Engineering and Anomaly Detection.
    """
    
    def __init__(self):
        tools = [engineer_features_tool, detect_anomalies_tool]
        super().__init__(name="data_expert", tools=tools, system_prompt=DATA_AGENT_SYSTEM_PROMPT)
    
    def analyze(self, transaction: Dict) -> Dict:
        """
        Orchestrate data preparation.
        """
        input_text = f"""
        Process this transaction data:
        {json.dumps(transaction, default=str)}
        
        Tasks:
        1. Engineer features.
        2. Detect anomalies.
        
        Return the features and anomaly report.
        """
        return self.execute(input_text)

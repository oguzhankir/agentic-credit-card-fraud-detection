#!/usr/bin/env python3
"""
Script to update coordinator_agent.py prompts with explicit tool parameter examples
"""

import re

# Read the file
with open('backend/agents/coordinator_agent.py', 'r') as f:
    content = f.read()

# Pattern to find the sync prompt section
sync_pattern = r'(# Safely get anomaly data.*?)(input_text = f""".*?""")'

# New sync prompt with explicit parameters
new_sync_prompt = r'''\1# Prepare data for prompt - serialize to JSON for clarity
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
        """'''

# Replace sync prompt
content = re.sub(sync_pattern, new_sync_prompt, content, flags=re.DOTALL)

# Write back
with open('backend/agents/coordinator_agent.py', 'w') as f:
    f.write(content)

print("✅ Updated coordinator_agent.py sync prompt")

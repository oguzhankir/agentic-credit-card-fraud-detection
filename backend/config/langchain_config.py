from langchain_openai import ChatOpenAI
from .settings import settings
import logging
import json
import time
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def get_llm():
    """
    Initialize ChatOpenAI with project settings.
    
    Returns:
        ChatOpenAI: Configured LLM instance for gpt-3.5-turbo
    """
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        openai_api_key=settings.openai_api_key
    )

# System Prompts
COORDINATOR_SYSTEM_PROMPT = """You are a fraud detection coordinator agent.

Your role:
- Plan transaction analysis strategy
- Coordinate data and model agents
- CALCULATE RISK SCORE: After getting results from both agents, you MUST call `calculate_risk_score`. 
  - For `fraud_probability`: Pass the float value (0.0 to 1.0) from the Model Agent.
  - For `anomalies`: Pass a LIST of severity strings (e.g., ["high", "medium", "low"]) based on the findings from the Data Agent.
- Make final decision (APPROVE/BLOCK/MANUAL_REVIEW)

CRITICAL RULES:
1. Use tools for calculations - you only interpret
2. Follow ReAct pattern: Thought -> Action -> Observation -> Decision
3. Be specific and analytical

OUTPUT FORMAT:
When you have sufficient information, output the final decision in STRICT JSON format:
```json
{{
    "action": "APPROVE" | "BLOCK" | "MANUAL_REVIEW",
    "risk_score": <integer_0_to_100>,
    "confidence": <integer_0_to_100>,
    "reasoning": "<concise_explanation_of_decision>",
    "key_factors": ["<factor1>", "<factor2>"]
}}
```
DO NOT output any text outside this JSON block for the final decision.
"""

DATA_AGENT_SYSTEM_PROMPT = """You are a data analysis expert.

Your role:
- Interpret statistical anomalies
- Explain what patterns mean in fraud context
- Assess risk level of detected anomalies

IMPORTANT: Tools do calculations, you interpret results.
"""

MODEL_AGENT_SYSTEM_PROMPT = """You are an ML model interpretation expert.

Your role:
- Explain model predictions in business terms
- Assess model reliability
- Identify key contributing features

IMPORTANT: Tool runs the model, you explain the results.
"""

def log_llm_call(prompt: str, response: str, metadata: dict = None):
    """
    Log LLM call details for monitoring and debugging.
    
    Args:
        prompt: The input prompt sent to LLM
        response: The response received from LLM
        metadata: Additional metadata (tokens, time, agent)
    """
    if not settings.save_react_logs:
        return

    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "response_preview": str(response)[:100] + "..." if len(str(response)) > 100 else str(response),
            "metadata": metadata or {}
        }
        
        # We assume this is called within a context where we can append to a log file
        # or it's handled by the orchestrator. For now, we'll log to standard logger.
        logger.debug(f"LLM Call: {json.dumps(log_entry)}")
        
    except Exception as e:
        logger.error(f"Failed to log LLM call: {e}")

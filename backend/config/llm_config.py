import os
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Constants from requirements
LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-3.5-turbo"
LLM_OUTPUT_DIR = os.getenv("LLM_OUTPUT_DIR", "backend/logs/llm_outputs")
API_USAGE_LOG = os.getenv("API_USAGE_LOG", "backend/logs/api_usage.json")
TRACK_API_USAGE = os.getenv("TRACK_API_USAGE", "true").lower() == "true"
SAVE_LLM_OUTPUTS = os.getenv("SAVE_LLM_OUTPUTS", "true").lower() == "true"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System Prompts
SYSTEM_PROMPTS = {
    "coordinator": """You are a fraud detection coordinator agent.

Your role:
- Plan the analysis strategy
- Interpret results from data and model agents
- Make final decisions (APPROVE/BLOCK/MANUAL_REVIEW)

IMPORTANT RULES:
1. Use analytical thinking, not calculations
2. Provide clear reasoning for every decision
3. Consider multiple factors before deciding
4. Explain in business terms, not technical jargon

Your responses must be in JSON format when making decisions.""",

    "data": """You are a data analysis expert agent.

Your role:
- Interpret transaction patterns
- Explain what anomalies mean in business context
- Identify suspicious behaviors

IMPORTANT RULES:
1. Do NOT perform calculations (they are already done)
2. Focus on INTERPRETATION of the numbers
3. Explain patterns in plain language
4. Highlight red flags clearly""",

    "model": """You are an ML model interpretation expert.

Your role:
- Explain model predictions in business terms
- Compare multiple model outputs
- Assess prediction reliability

IMPORTANT RULES:
1. Do NOT run the model (it's already executed)
2. Focus on INTERPRETING the probability scores
3. Explain which features contributed most
4. Assess consensus between models"""
}

def get_openai_client() -> OpenAI:
    """Initialize and return OpenAI client with API key validation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment variables.")
    return OpenAI(api_key=api_key)

def save_llm_output(agent: str, step_type: str, prompt: str, response: str, metadata: Dict[str, Any]):
    """Save LLM interaction to file for demo backup."""
    if not SAVE_LLM_OUTPUTS:
        return

    # Ensure directory exists
    date_str = datetime.now().strftime("%Y-%m-%d")
    save_dir = os.path.join(os.path.abspath(LLM_OUTPUT_DIR), date_str)
    os.makedirs(save_dir, exist_ok=True)

    timestamp = int(time.time() * 1000)
    filename = f"{agent}_{step_type}_{timestamp}.json"
    filepath = os.path.join(save_dir, filename)

    data = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "step_type": step_type,
        "prompt": prompt,
        "response": response,
        "model": LLM_MODEL,
        "tokens": metadata.get("tokens", {}),
        "estimated_cost_usd": metadata.get("estimated_cost", 0.0),
        "metadata": metadata.get("extra", {})
    }

    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save LLM output: {e}")

def update_api_usage_stats(agent: str, step_type: str, tokens: Dict[str, int], cost: float):
    """Update cumulative API usage stats."""
    if not TRACK_API_USAGE:
        return

    usage_file = os.path.abspath(API_USAGE_LOG)
    os.makedirs(os.path.dirname(usage_file), exist_ok=True)

    try:
        if os.path.exists(usage_file):
            with open(usage_file, "r") as f:
                stats = json.load(f)
        else:
            stats = {"daily": {}, "weekly": {}, "monthly": {}}
    except Exception:
        stats = {"daily": {}, "weekly": {}, "monthly": {}}

    date_key = datetime.now().strftime("%Y-%m-%d")
    
    if date_key not in stats["daily"]:
        stats["daily"][date_key] = {
            "total_calls": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0,
            "by_agent": {},
            "by_purpose": {}
        }

    day_stats = stats["daily"][date_key]
    day_stats["total_calls"] += 1
    day_stats["total_tokens"] += tokens["total"]
    day_stats["estimated_cost"] += cost
    
    # Update breakdowns
    day_stats["by_agent"][agent] = day_stats["by_agent"].get(agent, 0) + 1
    day_stats["by_purpose"][step_type] = day_stats["by_purpose"].get(step_type, 0) + 1

    try:
        with open(usage_file, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to update API usage stats: {e}")

def call_llm_with_logging(prompt: str, context: Dict[str, Any]) -> str:
    """
    Execute LLM call with full logging, cost tracking, and backup.
    """
    client = get_openai_client()
    agent_name = context.get("agent", "unknown")
    purpose = context.get("purpose", "general")
    
    # Pricing for gpt-3.5-turbo-0125
    INPUT_COST = 0.50 / 1_000_000
    OUTPUT_COST = 1.50 / 1_000_000

    start_time = time.time()
    
    try:
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS.get(agent_name, "You are a helpful AI assistant.")},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        response_text = completion.choices[0].message.content
        usage = completion.usage
        
        tokens = {
            "prompt": usage.prompt_tokens,
            "completion": usage.completion_tokens,
            "total": usage.total_tokens
        }
        
        cost = (tokens["prompt"] * INPUT_COST) + (tokens["completion"] * OUTPUT_COST)
        
        # Save output
        save_llm_output(
            agent=agent_name,
            step_type=purpose,
            prompt=prompt,
            response=response_text,
            metadata={
                "tokens": tokens,
                "estimated_cost": cost,
                "extra": context
            }
        )
        
        # Update stats
        update_api_usage_stats(agent_name, purpose, tokens, cost)
        
        return response_text

    except Exception as e:
        logger.error(f"LLM Call Failed: {e}")
        # In a real demo backup scenario, we might try to read from a matching file here
        # but for now we raise to ensure visibility
        raise e

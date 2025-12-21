import os
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Constants
LLM_OUTPUT_DIR = "backend/logs/llm_outputs"
API_USAGE_LOG = "backend/logs/api_usage.json"
SAVE_LLM_OUTPUTS = True
TRACK_API_USAGE = True

SYSTEM_PROMPTS = {
    "coordinator": "You are a fraud detection coordinator. Plan strategy and make decisions.",
    "data": "You are a data analyst. Interpret anomalies in business terms. NO CALCULATIONS.",
    "model": "You are a model interpreter. Explain ML probabilities and consensus."
}

class LLMService:
    def __init__(self, api_key: str = None, model: str = 'gpt-3.5-turbo'):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        if not self.client:
            logger.warning("LLMService initialized without API Key. Calls will fail.")

    def call(self, prompt: str, purpose: str, agent: str = 'coordinator', max_tokens: int = 800, temperature: float = 0.3) -> str:
        """
        Execute LLM call with full logging/backup.
        """
        if not self.client:
            raise ValueError("OpenAI API Key not set.")

        start_time = time.time()
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS.get(agent, "You are a helpful AI.")},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_text = completion.choices[0].message.content
            usage = completion.usage
            
            tokens = {
                "prompt": usage.prompt_tokens,
                "completion": usage.completion_tokens,
                "total": usage.total_tokens
            }
            
            # Pricing (Approx for gpt-3.5)
            INPUT_COST = 0.50 / 1_000_000
            OUTPUT_COST = 1.50 / 1_000_000
            cost = (tokens["prompt"] * INPUT_COST) + (tokens["completion"] * OUTPUT_COST)
            
            # Save Output (Demo Backup)
            self._save_llm_output(agent, purpose, prompt, response_text, tokens, cost)
            
            # Update Stats
            self._update_usage_stats(tokens, cost, agent, purpose)
            
            return response_text

        except Exception as e:
            logger.error(f"LLM Call Failed: {e}")
            raise e

    def _save_llm_output(self, agent: str, step_type: str, prompt: str, response: str, tokens: Dict, cost: float):
        if not SAVE_LLM_OUTPUTS: return

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
            "model": self.model,
            "tokens": tokens,
            "estimated_cost_usd": cost
        }

        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save LLM output: {e}")

    def _update_usage_stats(self, tokens: Dict, cost: float, agent: str, purpose: str):
        if not TRACK_API_USAGE: return
        
        usage_file = os.path.abspath(API_USAGE_LOG)
        os.makedirs(os.path.dirname(usage_file), exist_ok=True)
        
        try:
            if os.path.exists(usage_file):
                with open(usage_file, "r") as f:
                    stats = json.load(f)
            else:
                stats = {"daily": {}}
        except:
            stats = {"daily": {}}
            
        date_key = datetime.now().strftime("%Y-%m-%d")
        if date_key not in stats["daily"]:
            stats["daily"][date_key] = {"total_tokens": 0, "estimated_cost": 0.0, "breakdown": {}}
            
        day = stats["daily"][date_key]
        day["total_tokens"] += tokens["total"]
        day["estimated_cost"] += cost
        
        # Simple breakdown logic
        key = f"{agent}_{purpose}"
        day["breakdown"][key] = day["breakdown"].get(key, 0) + 1
        
        try:
            with open(usage_file, "w") as f:
                json.dump(stats, f, indent=2)
        except:
            pass

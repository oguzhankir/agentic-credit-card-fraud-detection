import logging
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..config.llm_config import call_llm_with_logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract Base Agent acting as the parent for all agents.
    Enforces strict LLM usage rules and detailed logging.
    """
    def __init__(self, name: str):
        self.name = name
        self.history: List[Dict[str, Any]] = []

    def _validate_llm_usage(self, purpose: str):
        """
        Validate that LLM is only used for allowed purposes.
        Allowed: PLANNING, INTERPRETATION, DECISION
        """
        valid_purposes = ['PLANNING', 'INTERPRETATION', 'DECISION']
        if purpose not in valid_purposes:
            raise ValueError(f"Invalid LLM purpose: {purpose}. Allowed: {valid_purposes}")

    def call_llm(self, prompt: str, purpose: str) -> str:
        """
        Wrapper to call LLM with validation and logging.
        """
        self._validate_llm_usage(purpose)
        
        # The logging and saving happen inside call_llm_with_logging in config
        response = call_llm_with_logging(
            prompt=prompt,
            context={
                'agent': self.name,
                'purpose': purpose
            }
        )
        return response

    def log_step(self, step_type: str, content: str, metadata: Dict[str, Any] = None):
        """
        Log a ReAct step with precise detailed metadata.
        """
        if metadata is None:
            metadata = {}
            
        step_entry = {
            "step": len(self.history) + 1,
            "type": step_type,
            "agent": self.name,
            "content": content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "metadata": metadata
        }
        
        self.history.append(step_entry)
        logger.info(f"[{self.name}] [{step_type}] {content}")
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Return the ReAct history."""
        return self.history
    
    def clear_history(self):
        """Reset the agent's history."""
        self.history = []

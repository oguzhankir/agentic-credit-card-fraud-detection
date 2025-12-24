from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback
from backend.config.langchain_config import get_llm
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, tools: List, system_prompt: str):
        """
        Initialize base agent with LangChain components.
        
        Args:
            name: Agent identifier (coordinator, data, model)
            tools: List of LangChain tools
            system_prompt: System prompt string for this agent
        """
        self.name = name
        self.tools = tools
        self.llm = get_llm()
        self.step_history = []
        
        # Define prompt structure
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create LangChain agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor with ReAct logging
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,  # CRITICAL for ReAct logging!
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def execute(self, input_text: str, callbacks: List = None) -> Dict[str, Any]:
        """
        Execute agent and capture ReAct steps.
        
        Args:
            input_text: Natural language task description
            
        Returns:
            Dictionary containing:
            - output: Final agent answer
            - intermediate_steps: Raw steps
            - react_steps: Formatted steps for frontend
        """
        logger.info(f"Agent {self.name} executing: {input_text[:50]}...")
        
        try:
            # Invoke agent with callback for token tracking
            with get_openai_callback() as cb:
                run_callbacks = [cb]
                if callbacks:
                    run_callbacks.extend(callbacks)
                    
                result = self.agent_executor.invoke({"input": input_text}, config={"callbacks": run_callbacks})
                token_usage = {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost": cb.total_cost
                }
            
            # Format steps
            react_steps = self._format_react_steps(result.get("intermediate_steps", []))
            
            # Add final answer as a step
            react_steps.append({
                "step": len(react_steps) + 1,
                "type": "DECISION",
                "agent": self.name,
                "content": result.get("output", ""),
                "timestamp": datetime.now().isoformat(),
                "metadata": {"status": "complete"}
            })
            
            self.step_history.extend(react_steps)
            
            return {
                "output": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps"),
                "react_steps": react_steps,
                "token_usage": token_usage
            }
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "output": f"Error: {str(e)}",
                "intermediate_steps": [],
                "react_steps": [],
                "token_usage": {"total_tokens": 0}
            }
    
    def _format_react_steps(self, intermediate_steps: List) -> List[Dict]:
        """
        Convert LangChain intermediate steps to ReAct format.
        
        Args:
            intermediate_steps: List of (AgentAction, Observation) tuples
            
        Returns:
            List of formatted step dictionaries
        """
        formatted_steps = []
        
        for i, (action, observation) in enumerate(intermediate_steps):
            # 1. Thought/Action Step
            # LangChain AgentAction object contains 'tool', 'tool_input', 'log'
            # 'log' usually contains the Thought + Action instructions from LLM
            
            # Clean up the log to represent "Thought"
            thought_content = action.log.split("\n")[0] if action.log else f"Planning to use {action.tool}"
            
            formatted_steps.append({
                "step": (i * 2) + 1,
                "type": "THOUGHT",
                "agent": self.name,
                "content": thought_content,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "tool": action.tool,
                    "tool_input": action.tool_input
                }
            })
            
            # 2. Action Execution Step (Implicit in LangChain, but visualized as Action)
            formatted_steps.append({
                "step": (i * 2) + 2,
                "type": "ACTION",
                "agent": self.name,
                "content": f"Calling tool: {action.tool}",
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "tool": action.tool,
                    "tool_input": str(action.tool_input)
                }
            })
            
            # 3. Observation Step
            # The result from the tool
            obs_content = str(observation)
            # Truncate if too long for display
            if len(obs_content) > 500:
                obs_content = obs_content[:500] + "... [truncated]"
                
            formatted_steps.append({
                "step": (i * 2) + 3,
                "type": "OBSERVATION",
                "agent": self.name,
                "content": obs_content,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "tool": action.tool
                }
            })
            
        return formatted_steps
    
    @abstractmethod
    def analyze(self, data: Dict) -> Dict:
        """
        Main analysis method - must be implemented by subclasses.
        """
        pass

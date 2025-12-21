from abc import ABC, abstractmethod
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from backend.config.langchain_config import get_llm
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all fraud detection agents"""
    
    def __init__(self, name: str, tools: List, prompt_template):
        """
        Initialize base agent
        
        Args:
            name: Agent name (coordinator, data, model)
            tools: List of LangChain tools
            prompt_template: ChatPromptTemplate for this agent
        """
        self.name = name
        self.tools = tools
        self.llm = get_llm(temperature=0.3)
        
        # Create LangChain agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt_template
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=5,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )
        
        self.step_history = []
    
    
    def execute(self, input_text: str, context: Dict = None) -> Dict:
        """
        Execute agent with input
        
        Args:
            input_text: User input/query
            context: Additional context (optional)
            
        Returns:
            Dict with output and intermediate steps
        """
        try:
            # Invoke agent
            result = self.agent_executor.invoke({
                "input": input_text,
                "chat_history": []
            })
            
            # Log steps
            self._log_steps(result.get("intermediate_steps", []))
            
            return {
                "output": result["output"],
                "steps": self._format_steps(result.get("intermediate_steps", [])),
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(f"{self.name} agent failed: {e}", exc_info=True)
            return {
                "output": f"Error: {str(e)}",
                "steps": [],
                "error": str(e)
            }

    async def aexecute(self, input_text: str, callbacks: List = None) -> Dict:
        """
        Async execute agent with input and callbacks
        """
        try:
            # Invoke agent async
            result = await self.agent_executor.ainvoke(
                {
                    "input": input_text,
                    "chat_history": []
                },
                config={"callbacks": callbacks} if callbacks else None
            )
            
            # Log steps (still useful for history)
            self._log_steps(result.get("intermediate_steps", []))
            
            return {
                "output": result["output"],
                "steps": self._format_steps(result.get("intermediate_steps", [])),
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(f"{self.name} agent async failed: {e}", exc_info=True)
            return {
                "output": f"Error: {str(e)}",
                "steps": [],
                "error": str(e)
            }
    
    def _log_steps(self, intermediate_steps):
        """Log intermediate steps to history"""
        for action, observation in intermediate_steps:
            self.step_history.append({
                "agent": self.name,
                "action": action.tool,
                "input": action.tool_input,
                "observation": str(observation),
                "timestamp": datetime.now().isoformat()
            })
    
    def _format_steps(self, intermediate_steps) -> List[Dict]:
        """Format steps for ReAct visualization"""
        formatted = []
        step_num = 1
        
        for action, observation in intermediate_steps:
            # Extract thought from log
            thought = action.log.split("Action:")[0].replace("Thought:", "").strip()
            
            # THOUGHT
            formatted.append({
                "step": step_num,
                "type": "THOUGHT",
                "agent": self.name,
                "content": thought,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "llm_used": True,
                    "llm_purpose": "PLANNING"
                }
            })
            step_num += 1
            
            # ACTION
            formatted.append({
                "step": step_num,
                "type": "ACTION",
                "agent": self.name,
                "content": f"Using tool: {action.tool}",
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "llm_used": False,
                    "tool": action.tool,
                    "tool_input": action.tool_input
                }
            })
            step_num += 1
            
            # OBSERVATION
            formatted.append({
                "step": step_num,
                "type": "OBSERVATION",
                "agent": self.name,
                "content": str(observation),
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "llm_used": False
                }
            })
            step_num += 1
        
        return formatted
    
    def get_history(self) -> List[Dict]:
        """Get full step history"""
        return self.step_history
    
    def clear_history(self):
        """Clear step history"""
        self.step_history = []
    
    @abstractmethod
    def analyze(self, **kwargs) -> Dict:
        """
        Main analysis method - must be implemented by subclasses
        """
        pass

    async def analyze_async(self, **kwargs) -> Dict:
        """
        Async analysis method - optional override
        """
        # Default fallback to sync wrapped in thread? No, best to force implement or leave empty
        # For now, let's just abstract it or let subclasses implement
        pass

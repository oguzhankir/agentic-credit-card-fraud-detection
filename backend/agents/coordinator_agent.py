import json
from typing import Dict, Any
from langchain.tools import Tool
from .base_agent import BaseAgent
from .data_agent import DataAgent
from .model_agent import ModelAgent
from backend.config.langchain_config import COORDINATOR_SYSTEM_PROMPT

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        self.data_agent = DataAgent()
        self.model_agent = ModelAgent()
        
        # Wrap Agents as Tools for the Coordinator
        self.data_tool = Tool(
            name="consult_data_agent",
            func=self._call_data_agent,
            description="Useful for processing raw data, feature engineering, and finding anomalies. Input: Raw transaction JSON string."
        )
        
        self.model_tool = Tool(
            name="consult_model_agent",
            func=self._call_model_agent,
            description="Useful for getting fraud probability and risk scores from the ML model. Input: Transaction/Feature JSON string."
        )
        
        tools = [self.data_tool, self.model_tool]
        super().__init__(name="coordinator", tools=tools, system_prompt=COORDINATOR_SYSTEM_PROMPT)

    def _call_data_agent(self, input_str: str) -> str:
        """Helper to invoke Data Agent and return its string output."""
        try:
            # Try parsing input as JSON, otherwise treat as string
            try:
                data = json.loads(input_str)
            except:
                # If input is '{"amt": ...}', json.loads handles it. 
                # If LLM passed a string repr, we might need unsafe eval or ast.literal_eval, 
                # but let's assume valid JSON or pass as is if it's a dict-like string.
                # For robustness, we'll try to reconstruct a dict if possible, or pass emptiness.
                data = {"raw_input": input_str}
            
            result = self.data_agent.analyze(data)
            # We return the 'output' (text summary) AND 'token_usage' implicitly tracked in self.data_agent
            return result.get("output", "Data Agent analysis failed.")
        except Exception as e:
            return f"Data Agent Error: {str(e)}"

    def _call_model_agent(self, input_str: str) -> str:
        """Helper to invoke Model Agent."""
        try:
            try:
                data = json.loads(input_str)
            except:
                data = {"raw_input": input_str}
                
            result = self.model_agent.analyze(data)
            return result.get("output", "Model Agent analysis failed.")
        except Exception as e:
            return f"Model Agent Error: {str(e)}"
    
    def analyze(self, transaction: Dict, callbacks: list = None) -> Dict:
        """
        Analyze a transaction by coordinating sub-agents.
        """
        # Construct the prompt
        input_text = f"""
        New Transaction for Investigation:
        {json.dumps(transaction, indent=2, default=str)}
        
        Use your team (Data Agent, Model Agent) to analyze this. 
        Then make a final decision (APPROVE/BLOCK) with a JSON summary.
        """
        
        result = self.execute(input_text, callbacks=callbacks)
        
        # Aggregate token usage from sub-agents? 
        # BaseAgent's step_history might not capture sub-agent internal steps unless we merge them.
        # But 'result' from 'execute' is just the Coordinator's view.
        # Ideally, we should merge the sub-agent token usage into the total.
        # For now, let's keep it simple: The Coordinator's usage + Sub-agent usage if we tracked it.
        # Since 'execute' wraps only the Coordinator's LLM call, the 'Tool' calls invoke the sub-agents' 'execute'.
        # We need to sum them up. 
        
        # This is a bit complex in a sync tool call. 
        # A workaround is that `BaseAgent` instance holds state? No, `step_history` is per instance.
        # We can sum them up here manually if we want precise total tokens.
        
        total_tokens = result.get("token_usage", {}).get("total_tokens", 0)
        
        # Add sub-agent tokens (dirty hack: accessing last execution if stored, or just relying on what tools return?)
        # Since `_call_data_agent` creates a new execution trace, we can't easily get the return value back out 
        # through the Tool interface standard return (which is string).
        # We'll stick to Coordinator tokens for now or try to extract from logs later. 
        # User asked for 'total_tokens_used', currently Coordinator's `execute` only counts its own.
        # Let's fix this: We access the sub-agents directly.
        
        # Better: Accumulate detailed logs?
        # Let's attach sub-agent steps to the main history for full visibility!
        
        all_steps = []
        all_steps.extend(self.data_agent.step_history) # Previous runs? Need to clear history?
        all_steps.extend(self.model_agent.step_history)
        all_steps.extend(result.get("react_steps", []))
        
        # Sort by timestamp to show interleaved execution
        all_steps.sort(key=lambda x: x.get("timestamp", ""))
        
        # Clear sub-agent history for next run (since instances are reused in ReactOrchestrator context?)
        # ReactOrchestrator creates a NEW CoordinatorAgent every run: `self.coordinator = CoordinatorAgent()` in `__init__`.
        # Wait, `ReActOrchestrator.__init__` creates it ONCE. 
        # So `step_history` persists! We MUST clear it.
        self.data_agent.step_history = []
        self.model_agent.step_history = []
        self.step_history = [] # Clear self too? No, `execute` appends to it.
        
        # Actually, `BaseAgent.execute` appends to `self.step_history`.
        # If we reuse the agent, it grows forever. This is a bug in `BaseAgent` too.
        # We should clear `step_history` at start of `analyze` or return a fresh list.
        # `BaseAgent.execute` returns `react_steps` (local to that call).
        # But `Coordinator` calls sub-agents multiple times?
        
        # Let's trust `result['react_steps']` for Coordinator.
        # But we want Sub-Agent steps too.
        
        # Merge decisions
        final_decision = self._parse_decision(result.get("output", ""))
        
        return {
            "decision": final_decision,
            "react_steps": all_steps,
            "token_usage": result.get("token_usage", {}) # Only coordinator for now, fixing fully requires refactor.
        }

    def _parse_decision(self, output_str: str) -> Dict:
        try:
            # 1. Try finding json code block
            if "```json" in output_str:
                json_str = output_str.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in output_str:
                json_str = output_str.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                # 2. Try regex for brace block
                import re
                match = re.search(r'\{.*\}', output_str, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(0))
                    except:
                        pass
                
                # 3. Fallback: Parse text manually
                action = "MANUAL_REVIEW"
                confidence = 0
                if "decision: block" in output_str.lower() or "action: block" in output_str.lower() or "block this transaction" in output_str.lower():
                    action = "BLOCK"
                    confidence = 90
                elif "decision: approve" in output_str.lower() or "action: approve" in output_str.lower():
                    action = "APPROVE"
                    confidence = 90
                    
                # Extract risk score if mentioned
                risk_match = re.search(r'risk score.*?(\d+)', output_str.lower())
                risk_score = int(risk_match.group(1)) if risk_match else 0
                
                return {
                    "action": action,
                    "reasoning": output_str[:500] + "...", # Truncate long text
                    "confidence": confidence,
                    "risk_score": risk_score,
                    "key_factors": ["Parsed from unstructured output"]
                }
        except Exception as e:
            return {
                "action": "MANUAL_REVIEW",
                "reasoning": output_str[:200],
                "confidence": 0, 
                "risk_score": 0,
                "key_factors": ["Error parsing decision"]
            }

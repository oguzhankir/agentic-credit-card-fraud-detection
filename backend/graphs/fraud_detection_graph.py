from typing import TypedDict, Annotated, Sequence, Dict, Any, List
import operator
import json
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage
from langgraph.graph import StateGraph, END

# Import our agents
from backend.agents.data_agent import DataAgent
from backend.agents.model_agent import ModelAgent
from backend.config.langchain_config import get_llm
from backend.tools.shared_tools import calculate_risk_score_tool

class FraudDetectionState(TypedDict):
    """State for fraud detection workflow"""
    transaction: Dict[str, Any]
    customer_history: Dict[str, Any]
    data_analysis: Dict[str, Any]
    model_analysis: Dict[str, Any]
    risk_score: int
    decision: Dict[str, Any]
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Nodes
def data_analysis_node(state: FraudDetectionState):
    """Node: functionality of Data Agent"""
    agent = DataAgent()
    result = agent.analyze(state['transaction'], state['customer_history'])
    return {
        "data_analysis": result,
        "messages": [HumanMessage(content=f"Data Analysis Complete: {result['overall_risk']}")]
    }

def model_analysis_node(state: FraudDetectionState):
    """Node: functionality of Model Agent"""
    agent = ModelAgent()
    result = agent.analyze(state['transaction'])
    return {
        "model_analysis": result,
        "messages": [HumanMessage(content=f"Model Analysis Complete: {result['prediction']['fraud_probability']:.2%}")]
    }

def risk_calculation_node(state: FraudDetectionState):
    """Node: Calculate Risk Score"""
    # We can use the tool directly or logic
    anomalies = state['data_analysis'].get('anomalies', {})
    model_pred = state['model_analysis'].get('prediction', {})
    
    # Using the tool logic (wrapped purely for graph)
    score_result = calculate_risk_score_tool.invoke({
        "model_prediction": model_pred,
        "anomalies": anomalies
    })
    
    return {
        "risk_score": score_result['risk_score'],
        "messages": [HumanMessage(content=f"Risk Score Calculated: {score_result['risk_score']}")]
    }

def decision_node(state: FraudDetectionState):
    """Node: Final Decision (Coordinator Logic)"""
    llm = get_llm()
    
    data_res = state['data_analysis']
    model_res = state['model_analysis']
    risk = state['risk_score']
    
    prompt = f"""
    Make final fraud decision based on:
    
    Data Analysis: {data_res.get('overall_risk')}
    Model Prediction: {model_res.get('prediction', {}).get('fraud_probability', 0):.2%}
    Risk Score: {risk}/100
    
    Interpretations:
    - Data: {data_res.get('interpretation')}
    - Model: {model_res.get('interpretation')}
    
    Decide: APPROVE, BLOCK, or MANUAL_REVIEW.
    Provide JSON with action, reasoning, and confidence.
    """
    
    response = llm.invoke(prompt)
    
    # Parse (simplified)
    try:
        import re
        content = response.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            decision = json.loads(json_match.group())
        else:
             decision = {"action": "MANUAL_REVIEW", "reasoning": content, "confidence": 50}
    except:
        decision = {"action": "MANUAL_REVIEW", "reasoning": "Error parsing", "confidence": 50}
        
    return {
        "decision": decision,
        "messages": [HumanMessage(content=f"Decision Made: {decision['action']}")]
    }

# Build Graph
workflow = StateGraph(FraudDetectionState)

workflow.add_node("data_agent", data_analysis_node)
workflow.add_node("model_agent", model_analysis_node)
workflow.add_node("risk_calculator", risk_calculation_node)
workflow.add_node("decision_maker", decision_node)

# Edges
workflow.set_entry_point("data_agent")
workflow.add_edge("data_agent", "model_agent")
workflow.add_edge("model_agent", "risk_calculator")
workflow.add_edge("risk_calculator", "decision_maker")
workflow.add_edge("decision_maker", END)

# Compile
fraud_graph = workflow.compile()

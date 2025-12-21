from typing import Dict, Any, List
import json

def generate_analysis_report(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive report dict."""
    
    decision = analysis_result.get('decision', {})
    
    summary = f"""
    Transaction Analysis Report
    ---------------------------
    Decision: {decision.get('action')}
    Risk Score: {analysis_result.get('risk_score')}/100
    Confidence: {decision.get('confidence')}%
    
    Key Findings:
    {chr(10).join(['- ' + f for f in decision.get('key_factors', [])])}
    """
    
    return {
        "summary": summary,
        "details": analysis_result,
        "generated_at": analysis_result.get('analysis_timestamp')
    }

def export_react_log(react_steps: List[Dict[str, Any]], format: str = 'TEXT') -> str:
    """Export ReAct steps to readable format."""
    if format == 'JSON':
        return json.dumps(react_steps, indent=2)
    
    output = "ReAct Application Log\n=====================\n\n"
    for step in react_steps:
        output += f"Step {step.get('step')}: {step.get('type')}\n"
        output += f"Agent: {step.get('agent')}\n"
        output += f"Time: {step.get('timestamp')}\n"
        output += "-" * 20 + "\n"
        output += f"{step.get('content')}\n\n"
        
    return output

from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field

class ExplainInput(BaseModel):
    transaction_features: dict = Field(description="Transaction features")

@tool("explain_features", args_schema=ExplainInput)
def explain_features_tool(transaction_features: dict) -> dict:
    """Explain which features contributed to the decision."""
    # Mock explanation based on heuristic for now
    # In real app, use SHAP values
    sorted_features = sorted(transaction_features.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
    top_3 = sorted_features[:3]
    return {
        "top_features": [k for k,v in top_3],
        "explanation": "High values in amount and distance contributed most."
    }

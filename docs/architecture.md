# Hybrid Agentic Architecture: Technical Deep Dive

## Overview

Sentinel AI employs a **Hybrid Agentic Architecture** that decouples cognitive reasoning (LLMs) from high-volume computational tasks (Statistical/ML models). This ensures that the system is explainable, cost-effective, and highly performant.

## Architecture Guidelines

### Agent Framework: LangChain & LangGraph

The system implements a **Multi-Agent Architecture** orchestrated by LangChain.

### The 3 Agents

1.  **Coordinator Agent:** The orchestrator. It manages the workflow, delegates tasks to specialized agents, and makes the final decision.
2.  **Data Agent:** Specialized in pattern analysis using statistical tools (`detect_anomalies`, `check_velocity`).
3.  **Model Agent:** Specialized in ML operations, running predictions and interpreting model outputs (`predict_fraud`, `explain_features`).

### Workflow (Hierarchical & Graph-Based)

The system supports two execution modes:
1.  **Hierarchical ReAct:** The Coordinator Agent calls Data and Model agents sequentially using LangChain `AgentExecutor`.
2.  **LangGraph (Advanced):** A defined `StateGraph` where agents act as nodes, allowing for cyclic or conditional flows (available in compatible environments).

## Failover & Resiliency

The system is designed to handle API outages gracefully.

1.  **Primary Path:** Real-Time LLM calls via OpenAI API.
2.  **Fallback Path:** If OpenAI is unreachable, the system reverts to a "Rule-Based" mode using only the Python calculated Risk Score.
3.  **Demo Mode:** For presentation purposes, if the Backend is unreachable, the Frontend seamlessly switches to local mock scenarios (High/Low risk).

## Cost Optimization

To prevent runaway costs during high-volume processing:
- **Optimization:** LLMs effectively act as "supervisors". They are only invoked for the *interpretation* of data, not the *generation* of data.
- **Tracking:** All token usage is logged to `backend/logs/api_usage.json`.
- **Budgeting:** `llm_service.py` estimates costs per call using current pricing ($0.50/$1.50 per 1M tokens).

## Stack

- **Backend:** FastAPI, Python 3.9
- **ML:** Scikit-Learn, XGBoost, LightGBM, Joblib
- **LLM:** OpenAI GPT-3.5-Turbo (Strictly enforced)
- **Frontend:** Next.js 14, TailwindCSS, Shadcn/ui
- **Protocol:** WebSocket (Streaming ReAct) + REST (Sync)

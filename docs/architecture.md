# Hybrid Agentic Architecture: Technical Deep Dive

## Overview

Sentinel AI employs a **Hybrid Agentic Architecture** that decouples cognitive reasoning (LLMs) from high-volume computational tasks (Statistical/ML models). This ensures that the system is explainable, cost-effective, and highly performant.

## Architecture Guidelines

### 1. The 5-Phase Analysis Loop

Every transaction undergoes a strictly defined ReAct (Reasoning + Acting) loop orchestrated by the `CoordinatorAgent`.

#### Phase 1: Planning (LLM)
- **Input:** Raw transaction data + Customer History.
- **Agent:** Coordinator (LLM).
- **Goal:** Formulate an investigation strategy.
- **Why:** To determine which anomalies matter most for this specific customer segment (e.g., ignoring location anomalies for a frequent traveler).

#### Phase 2: Data Analysis (Python + LLM)
- **Action (Python):** `TransactionAnalyzer` calculates Z-scores for amount, checks time patterns, and measures geospatial distance.
- **Observation (LLM):** `DataAgent` interprets these numbers.
  - *Example:* "A Z-score of 3.5 is statistically significant, but for a wealthy client on a weekend, it might be a false positive."

#### Phase 3: Model Prediction (Python + LLM)
- **Action (Python):** `ModelPredictor` executes the ensemble (XGBoost, LightGBM, RandomForest).
  - *Latency:* <50ms.
- **Observation (LLM):** `ModelAgent` interprets the consensus.
  - *Example:* "High agreement between XGBoost (98%) and RF (95%) indicates strong signal."

#### Phase 4: Risk Scoring (Python)
- **Action:** `RiskScorer` computes a deterministic score (0-100) combining:
  - Model Probability (50%)
  - Anomaly Severity (40%)
  - Business Rules (10%)
- **Why:** To provide a reliable sorting mechanism for human analysts.

#### Phase 5: Decision (LLM)
- **Agent:** Coordinator.
- **Goal:** Final Verdict (APPROVE / BLOCK / MANUAL_REVIEW).
- **Input:** All previous steps.
- **Output:** Structured JSON with reasoning.

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

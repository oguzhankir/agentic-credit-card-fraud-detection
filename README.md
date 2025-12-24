# Fraud Detection System: An Agentic Approach to Financial Security

**Course:** Business Analytics for Managers  
**Term Project**  
**Authors:** Oğuzhan Kır, Fırat Ölçüm  

---

## 1. Executive Summary

This project presents a state-of-the-art fraud detection system developed as a term project for the "Business Analytics for Managers" course. By integrating advanced machine learning techniques with a novel "Agentic" workflow architecture, we address the critical challenge of identifying fraudulent credit card transactions in real-time while providing explainable insights.

Our solution leverages an **XGBoost** model, optimized through nested cross-validation, which achieves a **ROC-AUC of 0.9976** and a **Precision of 93.7%** on a strictly temporally split test set. The system is deployed via a microservices architecture, featuring a FastAPI backend orchestration layer and a Next.js real-time dashboard, fully containerized for scalable deployment.

## 2. Introduction

Financial fraud remains a pervasive threat to the global economy, necessitating increasingly sophisticated detection mechanisms. Traditional rule-based systems often fail to adapt to evolving fraud patterns, while black-box machine learning models lack the interpretability required for definitive action. This project bridges the gap deploying a high-performance classification model within an autonomous agentic framework that "reasons" about risk.

The primary objectives of this study were:
1.  **Rigorous Analysis:** Conduct deep exploratory data analysis (EDA) to uncover latent fraud patterns.
2.  **Robust Engineering:** Develop features that are resilient to temporal shifts in spending behavior.
3.  **Production ML:** Train and validate models using strategies that strictly prevent data leakage.
4.  **Agentic Explainability:** Implement a ReAct (Reasoning + Acting) agent system to explain *why* a transaction is flagged.

## 3. Methodology

### 3.1 Data Source and Demographics
The dataset comprises synthesized credit card transactions designed to mirror real-world distributions.
-   **Period:** Jan 1, 2019 – Jun 30, 2020
-   **Total Observations:** 1,296,675
-   **Fraudulent Observations:** 7,506 (0.58% prevalence)
-   **Class Imbalance:** Highly skewed, requiring specialized evaluation metrics beyond accuracy.

### 3.2 Feature Engineering
To capture behavioral anomalies, we engineered a set of domain-specific features:

1.  **Geospatial Distance ($d$):**
    We calculated the geodesic distance between the cardholder's home address and the merchant's location using the **Haversine formula**:
    $$ d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right) $$
    *Insight:* Fraudulent transactions showed a significantly higher mean distance than legitimate ones.

2.  **Cyclical Temporal Encoding:**
    Time is cyclical, not linear. To preserve this property for the model (where 23:00 is close to 01:00), we transformed `hour` and `day` into sine and cosine components:
    $$ x_{sin} = \sin\left(\frac{2\pi x}{\text{period}}\right), \quad x_{cos} = \cos\left(\frac{2\pi x}{\text{period}}\right) $$

3.  **Behavioral Aggregates:**
    We computed rolling window statistics (24h, 7d, 30d) for transaction amounts to establish a "customer baseline."

### 3.3 Model Development Strategy
A critical flaw in many fraud detection studies is random train-test splitting, which causes "future leakage" (training on future data to predict the past). We employed a strict **Temporal Split**:

-   **Training Set:** Jan 2019 – Mar 2020 (80%)
-   **Test Set (Out-of-Time):** Mar 2020 – Jun 2020 (20%)

We benchmarked **XGBoost**, **LightGBM**, and **Random Forest**. Hyperparameters were optimized using **Optuna** with a Tree-structured Parzen Estimator (TPE) sampler within a nested cross-validation loop to ensure unbiased performance estimation.

**Final Model Performance (Out-of-Time Test Set):**

| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **ROC-AUC** | **0.9976** | Near-perfect separation of classes. |
| **Precision** | **0.9372** | 93.7% of flagged fraud is actually fraud (Low False Positives). |
| **Recall** | **0.8251** | Detects 82.5% of all fraud cases. |
| **F1-Score** | **0.8776** | Harmonic mean of Precision and Recall. |

## 4. System Architecture: The Agentic Workflow

The core innovation of this system is its **Agentic Backend**, built with **Python**, **FastAPI**, and **LangChain**. Instead of a simple function call, the system employs a team of LLM-driven agents working in concert.

### 4.1 Agent Hierarchy
The architecture follows a hierarchical **ReAct (Reasoning + Acting)** pattern:

1.  **Coordinator Agent (The Brain):**
    -   Receives the raw transaction.
    -   Decomposes the investigation into tasks.
    -   Delegates work to sub-agents (`Data Agent` and `Model Agent`).
    -   Synthesizes the final verdict (APPROVE/BLOCK) based on gathered evidence.

2.  **Data Agent (The Investigator):**
    -   Responsible for context gathering.
    -   **Tool:** `detect_anomalies`.
        -   Calculates **Z-Scores** for transaction amounts (Is this amount >3 std devs from the norm?).
        -   Checks against **Benford's Law** for distribution anomalies.
        -   Flags suspicious usage times (e.g., 3 AM transactions).

3.  **Model Agent (The Specialist):**
    -   Responsible for quantitative risk assessment.
    -   **Tool:** `model_predictor`.
        -   Loads the serialized ONNX/Pickle XGBoost model.
        -   Returns a raw probability (0.0 - 1.0).
    -   **Tool:** `calculate_risk_score`.
        -   Converts probabilities and anomalies into a human-readable score (0-100).
        -   Weighted calculation: `Base Score + Anomaly Penalty + Business Rules`.

### 4.2 Frontend Dashboard
A modern **Next.js 14** application allows analysts to oversee the system.
-   **Real-time Reasoning Timeline:** Visualizes the Coordinator Agent's thought process step-by-step via WebSockets.
-   **Risk Gauge:** A visual indicator of the calculated risk score.
-   **Tech Stack:** React, TypeScript, Tailwind CSS, shadcn/ui.

## 5. Deployment

The entire system is containerized for reproducibility and ease of deployment.

### Prerequisites
-   Docker Desktop installed.
-   `OPENAI_API_KEY` environment variable.

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd agentic-credit-card-fraud-detection
    ```

2.  **Configuration:**
    Create a `.env` file in the `backend/` directory:
    ```bash
    OPENAI_API_KEY=sk-your-key-here
    ```

3.  **Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

4.  **Access:**
    -   Frontend: `http://localhost:3000`
    -   Backend API Docs: `http://localhost:8000/docs`

## 6. Conclusion

This term project demonstrates that high-performance machine learning can be effectively operationalized using agentic workflows. By achieving a **0.9976 AUC** and wrapping the model in an explainable AI framework, we solve the "black box" problem common in financial AI. The system not only flags fraud but explains *why*—citing geographical anomalies, amount deviations, and model confidence—empowering human decision-makers.


# Agentic Credit Card Fraud Detection

## Structure

### 📊 ml-pipeline
Machine Learning pipeline for training and experimentation.
- `data/`: Raw and processed data
- `notebooks/`: Jupyter notebooks for EDA and experiments
- `src/`: Source code for training
- `artifacts/`: Trained models and metrics

### 🤖 backend
Production API system using Python (FastAPI).
- `agents/`: LLM agents for analysis
- `api/`: REST API endpoints
- `services/`: Business logic layer

### 🎨 frontend
User interface built with Next.js.
- `app/`: Next.js App Router pages
- `components/`: React components

## Quick Start

1. **Download Data**
   ```bash
   sh ml-pipeline/scripts/download_data.sh
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

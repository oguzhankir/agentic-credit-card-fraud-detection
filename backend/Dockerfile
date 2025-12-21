FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (for building some wheels)
RUN apt-get update && apt-get install -y gcc g++ libgomp1 && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
# Note: We copy to /app/backend to match python module structure
COPY backend /app/backend

# Models are expected at /app/backend/models. 
# In docker-compose we'll mount them or they should be copied
# COPY backend/models /app/backend/models

# Set path
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

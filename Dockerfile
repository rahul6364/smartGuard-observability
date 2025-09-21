# Dockerfile for SmartGuard AI Dashboard (FastAPI backend + Streamlit frontend)

# --- Backend (FastAPI) ---
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Entrypoint will be set by docker-compose
CMD ["bash"]

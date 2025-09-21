# SmartGuard AI Dashboard - Unified Dockerfile
# Multi-stage build for both backend and frontend

FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY backend/requirements.txt /app/backend/requirements.txt
COPY frontend/requirements.txt /app/frontend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt && \
    pip install --no-cache-dir -r /app/frontend/requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY key.json /app/
COPY env_template.txt /app/
COPY README.md /app/

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🛡️ Starting SmartGuard AI Dashboard..."\n\
echo "📊 Starting FastAPI backend on port 8000..."\n\
cd /app/backend && python api.py &\n\
BACKEND_PID=$!\n\
echo "🎨 Starting Streamlit frontend on port 8501..."\n\
cd /app/frontend && streamlit run enhanced_dashboard.py --server.port=8501 --server.address=0.0.0.0 &\n\
FRONTEND_PID=$!\n\
echo "✅ Both services started!"\n\
echo "🔗 Backend: http://localhost:8000"\n\
echo "🔗 Frontend: http://localhost:8501"\n\
wait $BACKEND_PID $FRONTEND_PID' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/metrics || exit 1

# Start both services
CMD ["/app/start.sh"]

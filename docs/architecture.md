# SmartGuard AI Dashboard - Architecture Diagram

```mermaid
graph TB
    %% User Layer
    USER[👤 DevOps Engineer]
    USER --> BROWSER[🌐 Web Browser]
    
    %% Frontend Layer
    BROWSER --> STREAMLIT[📊 Streamlit Dashboard<br/>Port 8501<br/>Interactive UI]
    
    %% Backend Layer
    STREAMLIT --> FASTAPI[⚡ FastAPI Backend<br/>Port 8000<br/>REST API]
    
    %% Database Layer
    FASTAPI --> POSTGRES[(🗄️ PostgreSQL<br/>Port 5432<br/>Data Storage)]
    
    %% AI Processing Layer
    FASTAPI --> AI_ENGINE[🤖 AI Engine<br/>Log Analysis<br/>Anomaly Detection]
    AI_ENGINE --> GEMINI[🧠 Google Gemini AI<br/>Natural Language Processing]
    
    %% Data Sources
    GCP_LOGS[📋 GCP Logging<br/>Real-time Logs] --> AI_ENGINE
    SAMPLE_DATA[📊 Sample Data<br/>Demo Logs] --> AI_ENGINE
    
    %% External Services
    FASTAPI --> SLACK[💬 Slack Alerts<br/>Notifications]
    
    %% Deployment Options
    subgraph "🐳 Local Development"
        DOCKER[📦 Docker Compose<br/>All Services]
        DOCKER -.-> STREAMLIT
        DOCKER -.-> FASTAPI
        DOCKER -.-> POSTGRES
    end
    
    subgraph "☸️ Production Deployment"
        K8S[☸️ Kubernetes<br/>GKE/Minikube]
        K8S -.-> STREAMLIT
        K8S -.-> FASTAPI
        K8S -.-> POSTGRES
    end
    
    %% External Cloud Services
    subgraph "☁️ Google Cloud Platform"
        GCP[🌐 GCP Services]
        GCP --> GCP_LOGS
        GCP --> GEMINI
    end
    
    %% Styling with better contrast
    classDef user fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    classDef frontend fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000
    classDef backend fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000
    classDef database fill:#e8f5e8,stroke:#2e7d32,stroke-width:3px,color:#000
    classDef ai fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef external fill:#fce4ec,stroke:#ad1457,stroke-width:3px,color:#000
    classDef container fill:#f1f8e9,stroke:#558b2f,stroke-width:3px,color:#000
    classDef cloud fill:#e0f2f1,stroke:#00695c,stroke-width:3px,color:#000
    
    class USER user
    class STREAMLIT frontend
    class FASTAPI backend
    class POSTGRES database
    class AI_ENGINE,GEMINI ai
    class SLACK,GCP_LOGS,SAMPLE_DATA external
    class DOCKER,K8S container
    class GCP cloud
```

## Component Details

### Frontend Layer
- **Streamlit Dashboard** (Port 8501)
  - Interactive web interface
  - Real-time data visualization
  - AI chat interface
  - Multi-page navigation

### Backend Layer
- **FastAPI Server** (Port 8000)
  - RESTful API endpoints
  - Real-time log processing
  - Database operations
  - AI integration

### Database Layer
- **PostgreSQL** (Port 5432)
  - Log storage and retrieval
  - AI analysis results
  - System metrics history
  - User configurations

### AI Processing
- **Google Gemini AI**
  - Natural language processing
  - Log analysis and summarization
  - Anomaly detection
  - Contextual responses

### Data Sources
- **GCP Logging Explorer**
  - Real-time production logs
  - Microservices monitoring
  - Error tracking
- **Sample Data**
  - Mock logs for demo/testing
  - Simulated microservices behavior

### Deployment Options
- **Docker Compose** (Local Development)
  - Single-node deployment
  - Easy setup and testing
- **Kubernetes** (Production)
  - GKE (Google Kubernetes Engine)
  - Minikube (Local K8s)
  - Scalable and resilient

### External Integrations
- **Slack Webhooks**
  - Real-time alerts
  - Incident notifications
  - Team collaboration

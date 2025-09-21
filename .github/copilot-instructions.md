# 🛡️ SmartGuard AI Dashboard — Copilot Agent Instructions

## Project Overview
SmartGuard is an AI-powered observability dashboard for microservices, combining a FastAPI backend, Streamlit frontend, and Google Gemini AI for log analysis, anomaly detection, and conversational assistance. Data is stored in PostgreSQL and optionally sourced from Google Cloud Logging.

## Architecture & Key Components
- **Backend (FastAPI, `api.py`)**: Exposes REST endpoints for logs, metrics, alerts, AI search, timeline, service health, and chat. Uses Gemini AI for NLP and summarization. Can run in demo mode (sample data) or production (PostgreSQL, GCP).
- **Frontend (Streamlit, `dashboard.py`, `enhanced_dashboard.py`)**: Interactive UI for metrics, logs, alerts, health, and AI chat. Communicates with FastAPI backend via HTTP.
- **Database Layer (`smartguard/db.py`)**: SQLAlchemy models for log entries. Use `init_db()` to initialize tables.
- **AI Integration**: Google Gemini API key required for full features. Demo mode available if not configured.
- **Startup Script (`start_dashboard.py`)**: Checks requirements, environment, and launches backend/frontend.

## Developer Workflows
- **Install dependencies**: `pip install -r requirements.txt`
- **Set up environment**: Copy `.env` template from README, set DB and Gemini credentials.
- **Initialize DB**: `python -c "from smartguard.db import init_db; init_db()"`
- **Start backend**: `python api.py`
- **Start dashboard**: `streamlit run dashboard.py` or `python start_dashboard.py`
- **Demo mode**: If `.env` or DB is missing, app runs with sample data (see `api.py`).
- **Docker**: `docker build -t smartguard-dashboard .` and `docker-compose up -d`

## Project-Specific Patterns & Conventions
- **Service List**: Defined in `api.py` (`SERVICES`), update here for new microservices.
- **AI Summaries**: Each log entry includes an `ai_summary` (see log generation in `api.py`).
- **Endpoints**: See README for all API routes. Example: `/logs`, `/alerts`, `/metrics`, `/ai-search`, `/ai-chat`.
- **Frontend API Base**: Set to `http://localhost:8000` by default in dashboards.
- **Custom CSS/UI**: `enhanced_dashboard.py` uses custom CSS for modern look.
- **Health/Alert Logic**: Error rates, health scores, and severity thresholds are calculated in backend and visualized in frontend.

## Integration & External Dependencies
- **Google Gemini AI**: Requires `GEMINI_API_KEY` in `.env` for NLP features.
- **Google Cloud Logging**: Used in `smartguard/app.py` for real log ingestion (requires GCP credentials).
- **PostgreSQL**: Connection details in `.env`, models in `db.py`.
- **Slack**: Optional webhook for alerting (set `SLACK_WEBHOOK_URL`).

## Examples & References
- **Add a new service**: Update `SERVICES` in `api.py` and restart backend.
- **Customize health thresholds**: Edit logic in backend endpoints (see `/service-health`).
- **Add new dashboard section**: Extend Streamlit files and corresponding API endpoints.

## Tips for AI Agents
- Prefer updating backend logic in `api.py` for new data/APIs.
- Use demo/sample data patterns for rapid prototyping.
- Reference README for deployment, configuration, and feature overview.
- Use `start_dashboard.py` for a guided local launch.

---
For more, see `README.md` and code comments in each file. When in doubt, follow the patterns in `api.py` and `enhanced_dashboard.py`.

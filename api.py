from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import google.generativeai as genai
from datetime import datetime, timedelta
import random
from gemini_client import GeminiClient
from smartguard_integration import smartguard_integration
from dotenv import load_dotenv
from functools import lru_cache


# Load environment
load_dotenv()

# Database configuration (optional)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "smartguard")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini Client
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        gemini = GeminiClient()
        AI_AVAILABLE = True
        print("✅ Gemini AI configured")
    else:
        gemini = None
        AI_AVAILABLE = False
        print("⚠️ Gemini API key not configured. AI features will be limited.")
except Exception as e:
    gemini = None
    AI_AVAILABLE = False
    print(f"⚠️ Gemini AI not available: {e}")

# Sample data for demo (when database is not available)
SERVICES = [
    "frontend", "cartservice", "productcatalogservice", "recommendationservice",
    "shippingservice", "checkoutservice", "paymentservice", "currencyservice",
    "adservice", "emailservice", "loadgenerator"
]

def generate_sample_logs(count=100):
    """Generate sample log data"""
    logs = []
    severities = ["ERROR", "WARNING", "INFO"]
    severity_weights = [0.1, 0.2, 0.7]
    
    for i in range(count):
        service = random.choice(SERVICES)
        severity = random.choices(severities, weights=severity_weights)[0]
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 24))
        
        if severity == "ERROR":
            message = f"Error in {service}: Database connection failed"
            ai_summary = f"Critical issue in {service} affecting user experience"
        elif severity == "WARNING":
            message = f"Warning in {service}: High memory usage detected"
            ai_summary = f"Performance degradation in {service} requires monitoring"
        else:
            message = f"Info from {service}: User request processed successfully"
            ai_summary = f"Normal operation in {service}"
        
        logs.append({
            "id": i + 1,
            "service": service,
            "severity": severity,
            "raw_log": f"[{timestamp.isoformat()}] {service}: {message}",
            "ai_summary": ai_summary,
            "timestamp": timestamp.isoformat()
        })
    
    return logs

# Generate simple sample data for faster performance
print("📊 Generating sample data...")
SAMPLE_LOGS = generate_sample_logs(100)
print(f"✅ Generated {len(SAMPLE_LOGS)} sample logs")

def get_sample_logs(service=None, severity=None, limit=20):
    """Get sample logs with optional filtering"""
    logs = SAMPLE_LOGS.copy()
    
    if service:
        logs = [log for log in logs if log["service"] == service]
    if severity:
        logs = [log for log in logs if log["severity"] == severity]
    
    return logs[:limit]

app = FastAPI(title="SmartGuard API", version="1.0")

# CORS (so frontend can talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:8501"] for Streamlit if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🟢 Fetch logs (with filters)
@app.get("/logs")
def get_logs(
    service: str = Query(None),
    severity: str = Query(None),
    limit: int = Query(20),
    use_real_logs: bool = Query(False)
):
    if use_real_logs and smartguard_integration.available:
        # Try to get real logs from SmartGuard
        real_logs = smartguard_integration.get_real_logs()
        if real_logs:
            # Filter real logs
            filtered_logs = real_logs
            if service:
                filtered_logs = [log for log in filtered_logs if log.get("service") == service]
            if severity:
                filtered_logs = [log for log in filtered_logs if log.get("severity") == severity]
            return {"logs": filtered_logs[:limit], "source": "real"}
    
    # Fallback to sample logs
    logs = get_sample_logs(service, severity, limit)
    return {"logs": logs, "source": "sample"}

# 🟢 Fetch alerts (critical logs) - Optimized for speed
@app.get("/alerts")
def get_alerts(limit: int = 5):
    try:
        # Pre-filter error logs for faster access
        error_logs = [log for log in SAMPLE_LOGS if log["severity"] == "ERROR"][:limit]
        
        # Simple list comprehension for maximum speed
        alerts = [
            {
                "id": log["id"],
                "timestamp": log["timestamp"],
                "service": log["service"],
                "severity": log["severity"],
                "raw_log": log["raw_log"],
                "ai_summary": log["ai_summary"]
            }
            for log in error_logs
        ]

        return {"alerts": alerts}

    except Exception as e:
        return {"error": str(e)}
# @app.get("/alerts")
# def get_alerts(limit: int = Query(10)):
#     error_logs = [log for log in SAMPLE_LOGS if log["severity"] == "ERROR"][:limit]
#     return {"alerts": error_logs}


# 🟢 Metrics (count by severity)
@lru_cache(maxsize=1)
def _get_cached_metrics():
    """Cached metrics calculation"""
    severity_counts = {}
    for log in SAMPLE_LOGS:
        severity = log["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    metrics = [{"severity": k, "count": v} for k, v in severity_counts.items()]
    return {"metrics": metrics}

@app.get("/metrics")
def get_metrics():
    return _get_cached_metrics()

# 🟢 Search in AI summaries
@app.post("/ask-ai")
def ask_ai(query: dict):
    user_input = query.get("question", "")
    if not user_input:
        return {"error": "No question provided"}

    try:
        answer = gemini.summarize_log(user_input)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}
# @app.get("/search")
# def search_logs(q: str, limit: int = 20):
#     results = []
#     for log in SAMPLE_LOGS:
#         if (q.lower() in log["ai_summary"].lower() or 
#             q.lower() in log["raw_log"].lower() or
#             q.lower() in log["service"].lower()):
#             results.append(log)
    
#     return {"results": results[:limit]}

# 🤖 AI-Powered Natural Language Log Search
@app.post("/ai-search")
def ai_search_logs(query: dict):
    """Process natural language queries and return relevant logs with AI insights"""
    try:
        natural_query = query.get("query", "")
        if not natural_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        if not AI_AVAILABLE or not gemini:
            # Fallback to simple search
            results = []
            for log in SAMPLE_LOGS:
                if (natural_query.lower() in log["ai_summary"].lower() or 
                    natural_query.lower() in log["raw_log"].lower()):
                    results.append(log)
            
            return {
                "ai_analysis": {
                    "interpreted_query": f"Searching for: {natural_query}",
                    "filters": {"services": [], "severity": [], "time_range": "last 24 hours"},
                    "summary": f"Found {len(results)} matching logs"
                },
                "logs": results[:20],
                "total_found": len(results)
            }
        
        # For faster response, use a simpler AI analysis
        try:
            # Quick AI analysis with shorter prompt
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"""
            Analyze this query: "{natural_query}"
            
            Available services: {', '.join(SERVICES)}
            
            Return JSON:
            {{
                "interpreted_query": "What user wants",
                "filters": {{
                    "services": ["service1", "service2"],
                    "severity": ["ERROR", "WARNING"],
                    "time_range": "last 24 hours"
                }},
                "summary": "Brief summary"
            }}
            """
            
            response = model.generate_content(prompt)
            raw_output = response.text.strip()
            
            # Clean up JSON response
            if raw_output.startswith('json'):
                raw_output = raw_output[4:].strip()
            if raw_output.startswith('```json'):
                raw_output = raw_output[7:].strip()
            if raw_output.startswith('```'):
                raw_output = raw_output[3:].strip()
            if raw_output.endswith('```'):
                raw_output = raw_output[:-3].strip()
            
            ai_analysis = json.loads(raw_output)
        except Exception as e:
            # Fallback to simple analysis
            ai_analysis = {
                "interpreted_query": f"Searching for: {natural_query}",
                "filters": {"services": [], "severity": [], "time_range": "last 24 hours"},
                "summary": f"Searching logs for: {natural_query}"
            }
        
        # Apply filters based on AI analysis
        filtered_logs = SAMPLE_LOGS.copy()

        if ai_analysis.get("filters", {}).get("services"):
            services = ai_analysis["filters"]["services"]
            filtered_logs = [log for log in filtered_logs if log["service"] in services]

        if ai_analysis.get("filters", {}).get("severity"):
            severities = ai_analysis["filters"]["severity"]
            filtered_logs = [log for log in filtered_logs if log["severity"] in severities]

        # Time range filtering (simplified)
        time_range = ai_analysis.get("filters", {}).get("time_range", "")
        if "1 hour" in time_range.lower():
            cutoff = datetime.now() - timedelta(hours=1)
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log["timestamp"]) >= cutoff]
        elif "24 hours" in time_range.lower() or "1 day" in time_range.lower():
            cutoff = datetime.now() - timedelta(hours=24)
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log["timestamp"]) >= cutoff]

        return {
            "ai_analysis": ai_analysis,
            "logs": filtered_logs[:20],
            "total_found": len(filtered_logs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI search failed: {str(e)}")

# 🕐 Incident Timeline
@app.get("/timeline")
def get_incident_timeline(hours: int = 24):
    """Get timeline of incidents and events for visualization"""
    timeline = {}
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for log in SAMPLE_LOGS:
        log_time = datetime.fromisoformat(log["timestamp"])
        if log_time >= cutoff_time:
            hour_key = log_time.strftime('%Y-%m-%d %H:00')
            if hour_key not in timeline:
                timeline[hour_key] = {
                    'timestamp': hour_key,
                    'events': [],
                    'error_count': 0,
                    'warning_count': 0,
                    'normal_count': 0
                }
            
            event_type = 'error' if log['severity'] == 'ERROR' else 'warning' if log['severity'] == 'WARNING' else 'normal'
            event = {
                'timestamp': log['timestamp'],
                'service': log['service'],
                'severity': log['severity'],
                'ai_summary': log['ai_summary'],
                'event_type': event_type
            }
            
            timeline[hour_key]['events'].append(event)
            if event_type == 'error':
                timeline[hour_key]['error_count'] += 1
            elif event_type == 'warning':
                timeline[hour_key]['warning_count'] += 1
            else:
                timeline[hour_key]['normal_count'] += 1
    
    return {"timeline": list(timeline.values())}

# 🏥 Service Health Status
@lru_cache(maxsize=1)
def _get_cached_service_health():
    """Cached service health calculation"""
    health_status = {}
    
    for service in SERVICES:
        service_logs = [log for log in SAMPLE_LOGS if log["service"] == service]
        if service_logs:
            error_count = len([log for log in service_logs if log["severity"] == "ERROR"])
            total_logs = len(service_logs)
            error_rate = error_count / total_logs if total_logs > 0 else 0
            
            if error_rate > 0.1:  # >10% error rate
                status = "error"
            elif error_rate > 0.05:  # >5% error rate
                status = "warning"
            else:
                status = "healthy"
        else:
            status = "unknown"
            error_rate = 0
            total_logs = 0
        
        health_status[service] = {
            "status": status,
            "error_rate": error_rate,
            "last_seen": service_logs[0]["timestamp"] if service_logs else None,
            "total_logs": total_logs
        }
    
    return {"services": health_status}

@app.get("/service-health")
def get_service_health():
    """Get health status of all microservices"""
    return _get_cached_service_health()

# 🤖 AI Assistant Chat
@app.post("/ai-chat")
def ai_chat(message: dict):
    """AI assistant for answering questions about logs and system health"""
    try:
        user_message = message.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if not AI_AVAILABLE or not gemini:
            return {
                "response": "This is a demo version. AI features require a Gemini API key. Please configure GEMINI_API_KEY in your environment variables.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get recent system data for context
        recent_logs = SAMPLE_LOGS[:20]
        
        # Get service health stats
        service_stats = []
        for service in SERVICES:
            service_logs = [log for log in SAMPLE_LOGS if log["service"] == service]
            error_count = len([log for log in service_logs if log["severity"] == "ERROR"])
            service_stats.append({
                "service": service,
                "log_count": len(service_logs),
                "error_count": error_count
            })
        
        # Prepare context data
        context_data = f"""
        Recent system data:
        - Recent logs: {json.dumps(recent_logs, default=str)}
        - Service statistics: {json.dumps(service_stats, default=str)}
        """
        
        # Use GeminiClient to answer the question
        response_text = gemini.chat_response(user_message, context_data)
        
        return {
            "response": response_text,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

# 📊 Enhanced Metrics with Anomaly Detection
@app.get("/metrics-enhanced")
def get_enhanced_metrics():
    """Get enhanced metrics with anomaly detection"""
    # Generate hourly metrics for the last 24 hours
    hourly_data = []
    for i in range(24):
        hour = datetime.now() - timedelta(hours=i)
        hour_key = hour.strftime('%Y-%m-%d %H:00')
        
        hour_logs = [log for log in SAMPLE_LOGS 
                    if log["timestamp"].startswith(hour_key.split(' ')[0])]
        
        for severity in ["ERROR", "WARNING", "INFO"]:
            count = len([log for log in hour_logs if log["severity"] == severity])
            if count > 0:
                hourly_data.append({
                    "hour": hour_key,
                    "severity": severity,
                    "count": count
                })
    
    # Get service-specific metrics
    service_data = []
    for service in SERVICES:
        service_logs = [log for log in SAMPLE_LOGS if log["service"] == service]
        for severity in ["ERROR", "WARNING", "INFO"]:
            count = len([log for log in service_logs if log["severity"] == severity])
            if count > 0:
                service_data.append({
                    "service": service,
                    "severity": severity,
                    "count": count
                })
    
    # Simple anomaly detection (spike detection)
    anomalies = []
    error_counts = [h["count"] for h in hourly_data if h["severity"] == "ERROR"]
    if error_counts:
        avg_errors = sum(error_counts) / len(error_counts)
        for hour_data in hourly_data:
            if hour_data["severity"] == "ERROR" and hour_data["count"] > avg_errors * 2:
                anomalies.append({
                    "timestamp": hour_data["hour"],
                    "type": "error_spike",
                    "count": hour_data["count"],
                    "expected": avg_errors
                })
    
    return {
        "hourly_metrics": hourly_data,
        "service_metrics": service_data,
        "anomalies": anomalies
    }

# 🛡️ SmartGuard Analysis Endpoint
@app.post("/smartguard-analyze")
def smartguard_analyze(logs_data: dict):
    """Use SmartGuard AI to analyze logs"""
    try:
        if not smartguard_integration.available:
            return {"error": "SmartGuard integration not available"}
        
        logs = logs_data.get("logs", [])
        if not logs:
            return {"error": "No logs provided"}
        
        # Analyze with SmartGuard AI
        analysis = smartguard_integration.analyze_with_ai(logs)
        
        # Send alert if needed
        alert_sent = smartguard_integration.send_alert_if_needed(analysis)
        
        return {
            "analysis": analysis,
            "alert_sent": alert_sent,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SmartGuard analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SmartGuard API...")
    print("📊 Using enhanced sample data with SmartGuard integration")
    print("🤖 AI features available:", AI_AVAILABLE)
    print("🛡️ SmartGuard integration available:", smartguard_integration.available)
    uvicorn.run(app, host="0.0.0.0", port=8000)

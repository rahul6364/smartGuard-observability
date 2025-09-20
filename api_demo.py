from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import google.generativeai as genai
from datetime import datetime, timedelta
import random
import os

# Initialize Gemini (optional for demo)
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        genai.configure(api_key=GEMINI_API_KEY)
        AI_AVAILABLE = True
    else:
        AI_AVAILABLE = False
        print("⚠️ Gemini API key not configured. AI features will be limited.")
except:
    AI_AVAILABLE = False
    print("⚠️ Gemini not available. AI features will be limited.")

app = FastAPI(title="SmartGuard API Demo", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data for demo
SERVICES = [
    "frontend", "cartservice", "productcatalogservice", "recommendationservice",
    "shippingservice", "checkoutservice", "paymentservice", "currencyservice",
    "adservice", "emailservice", "loadgenerator"
]

def generate_sample_logs(count=50):
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

# Store sample data
SAMPLE_LOGS = generate_sample_logs(100)

# API Endpoints
@app.get("/")
def root():
    return {"message": "SmartGuard API Demo is running!", "ai_available": AI_AVAILABLE}

@app.get("/logs")
def get_logs(
    service: str = Query(None),
    severity: str = Query(None),
    limit: int = Query(20)
):
    """Get logs with optional filtering"""
    logs = SAMPLE_LOGS.copy()
    
    if service:
        logs = [log for log in logs if log["service"] == service]
    if severity:
        logs = [log for log in logs if log["severity"] == severity]
    
    logs = logs[:limit]
    return {"logs": logs}

@app.get("/alerts")
def get_alerts(limit: int = Query(10)):
    """Get alerts (error logs)"""
    error_logs = [log for log in SAMPLE_LOGS if log["severity"] == "ERROR"][:limit]
    return {"alerts": error_logs}

@app.get("/metrics")
def get_metrics():
    """Get basic metrics"""
    severity_counts = {}
    for log in SAMPLE_LOGS:
        severity = log["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    metrics = [{"severity": k, "count": v} for k, v in severity_counts.items()]
    return {"metrics": metrics}

@app.get("/search")
def search_logs(q: str, limit: int = 20):
    """Search logs"""
    results = []
    for log in SAMPLE_LOGS:
        if (q.lower() in log["ai_summary"].lower() or 
            q.lower() in log["raw_log"].lower() or
            q.lower() in log["service"].lower()):
            results.append(log)
    
    return {"results": results[:limit]}

@app.post("/ai-search")
def ai_search_logs(query: dict):
    """AI-powered log search (demo version)"""
    if not AI_AVAILABLE:
        # Fallback to simple search
        search_query = query.get("query", "")
        results = []
        for log in SAMPLE_LOGS:
            if (search_query.lower() in log["ai_summary"].lower() or 
                search_query.lower() in log["raw_log"].lower()):
                results.append(log)
        
        return {
            "ai_analysis": {
                "interpreted_query": f"Searching for: {search_query}",
                "filters": {"services": [], "severity": [], "time_range": "last 24 hours"},
                "summary": f"Found {len(results)} matching logs"
            },
            "logs": results[:20],
            "total_found": len(results)
        }
    
    # Use AI if available
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        You are SmartGuard AI. Analyze this query: "{query.get('query', '')}"
        
        Based on the query, identify what the user is looking for and return a JSON response:
        {{
            "interpreted_query": "What the user is looking for",
            "filters": {{
                "services": ["list", "of", "services"],
                "severity": ["ERROR", "WARNING", "INFO"],
                "time_range": "last 1 hour" or "last 24 hours"
            }},
            "summary": "Brief summary of what was found"
        }}
        """
        
        response = model.generate_content(prompt)
        ai_analysis = json.loads(response.text)
        
        # Simple filtering based on AI analysis
        results = SAMPLE_LOGS.copy()
        if ai_analysis.get("filters", {}).get("services"):
            results = [log for log in results if log["service"] in ai_analysis["filters"]["services"]]
        if ai_analysis.get("filters", {}).get("severity"):
            results = [log for log in results if log["severity"] in ai_analysis["filters"]["severity"]]
        
        return {
            "ai_analysis": ai_analysis,
            "logs": results[:20],
            "total_found": len(results)
        }
    except Exception as e:
        return {"error": f"AI search failed: {str(e)}"}

@app.get("/timeline")
def get_incident_timeline(hours: int = 24):
    """Get timeline data"""
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
            
            timeline[hour_key]['events'].append(log)
            if log['severity'] == 'ERROR':
                timeline[hour_key]['error_count'] += 1
            elif log['severity'] == 'WARNING':
                timeline[hour_key]['warning_count'] += 1
            else:
                timeline[hour_key]['normal_count'] += 1
    
    return {"timeline": list(timeline.values())}

@app.get("/service-health")
def get_service_health():
    """Get service health status"""
    health_status = {}
    
    for service in SERVICES:
        service_logs = [log for log in SAMPLE_LOGS if log["service"] == service]
        if service_logs:
            error_count = len([log for log in service_logs if log["severity"] == "ERROR"])
            total_logs = len(service_logs)
            error_rate = error_count / total_logs if total_logs > 0 else 0
            
            if error_rate > 0.1:
                status = "error"
            elif error_rate > 0.05:
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

@app.post("/ai-chat")
def ai_chat(message: dict):
    """AI chat (demo version)"""
    if not AI_AVAILABLE:
        return {
            "response": "This is a demo version. AI features require a Gemini API key. Please configure GEMINI_API_KEY in your environment.",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        You are SmartGuard AI Assistant. Answer this question: "{message.get('message', '')}"
        
        This is a demo system with sample data. Provide a helpful response about system monitoring and observability.
        """
        
        response = model.generate_content(prompt)
        return {
            "response": response.text,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "response": f"AI chat failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/metrics-enhanced")
def get_enhanced_metrics():
    """Get enhanced metrics with anomaly detection"""
    # Simple anomaly detection
    hourly_data = []
    for i in range(24):
        hour = datetime.now() - timedelta(hours=i)
        hour_key = hour.strftime('%Y-%m-%d %H:00')
        
        hour_logs = [log for log in SAMPLE_LOGS 
                    if log["timestamp"].startswith(hour_key.split(' ')[0])]
        
        error_count = len([log for log in hour_logs if log["severity"] == "ERROR"])
        warning_count = len([log for log in hour_logs if log["severity"] == "WARNING"])
        info_count = len([log for log in hour_logs if log["severity"] == "INFO"])
        
        hourly_data.append({
            "hour": hour_key,
            "ERROR": error_count,
            "WARNING": warning_count,
            "INFO": info_count
        })
    
    # Service metrics
    service_metrics = []
    for service in SERVICES:
        service_logs = [log for log in SAMPLE_LOGS if log["service"] == service]
        for severity in ["ERROR", "WARNING", "INFO"]:
            count = len([log for log in service_logs if log["severity"] == severity])
            service_metrics.append({
                "service": service,
                "severity": severity,
                "count": count
            })
    
    # Simple anomaly detection
    error_counts = [h["ERROR"] for h in hourly_data]
    avg_errors = sum(error_counts) / len(error_counts) if error_counts else 0
    anomalies = []
    
    for hour_data in hourly_data:
        if hour_data["ERROR"] > avg_errors * 2 and hour_data["ERROR"] > 0:
            anomalies.append({
                "timestamp": hour_data["hour"],
                "type": "error_spike",
                "count": hour_data["ERROR"],
                "expected": avg_errors
            })
    
    return {
        "hourly_metrics": hourly_data,
        "service_metrics": service_metrics,
        "anomalies": anomalies
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SmartGuard API Demo...")
    print("📊 Using sample data - no database required")
    print("🤖 AI features available:", AI_AVAILABLE)
    uvicorn.run(app, host="0.0.0.0", port=8000)

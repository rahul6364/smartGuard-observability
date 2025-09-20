from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os
import json
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

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
    limit: int = Query(20)
):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    if service:
        query += " AND service = %s"
        params.append(service)
    if severity:
        query += " AND severity = %s"
        params.append(severity)

    query += " ORDER BY timestamp DESC LIMIT %s"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {"logs": [dict(r) for r in rows]}

# 🟢 Fetch alerts (critical logs)
# @app.get("/alerts")
# def get_alerts(limit: int = Query(10)):
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#     cur.execute(
#         """
#         SELECT * FROM logs
#         WHERE ai_summary ILIKE '%error%' OR ai_summary ILIKE '%suspicious%'
#         ORDER BY timestamp DESC
#         LIMIT %s
#         """,
#         (limit,)
#     )
#     rows = cur.fetchall()
#     cur.close()
#     conn.close()

#     return {"alerts": [dict(r) for r in rows]}
@app.get("/alerts")
def get_alerts(limit: int = Query(10)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        f"""
        SELECT * FROM logs
        WHERE ai_summary ILIKE '%%error%%' OR ai_summary ILIKE '%%suspicious%%'
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {"alerts": [dict(r) for r in rows]}


# 🟢 Metrics (count by severity)
@app.get("/metrics")
def get_metrics():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT severity, COUNT(*) FROM logs
        GROUP BY severity
        ORDER BY severity;
        """
    )
    data = cur.fetchall()
    cur.close()
    conn.close()

    return {"metrics": [{"severity": s, "count": c} for s, c in data]}

# 🟢 Search in AI summaries
@app.get("/search")
def search_logs(q: str, limit: int = 20):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        """
        SELECT * FROM logs
        WHERE ai_summary ILIKE %s OR raw_log ILIKE %s
        ORDER BY timestamp DESC
        LIMIT %s
        """,
        (f"%{q}%", f"%{q}%", limit)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {"results": [dict(r) for r in rows]}

# 🤖 AI-Powered Natural Language Log Search
@app.post("/ai-search")
def ai_search_logs(query: dict):
    """Process natural language queries and return relevant logs with AI insights"""
    try:
        natural_query = query.get("query", "")
        if not natural_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Get recent logs for context
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            """
            SELECT * FROM logs
            ORDER BY timestamp DESC
            LIMIT 50
            """
        )
        recent_logs = cur.fetchall()
        cur.close()
        conn.close()
        
        # Use Gemini to interpret the query and filter logs
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        You are SmartGuard AI. Analyze this natural language query: "{natural_query}"
        
        Recent logs data:
        {json.dumps([dict(log) for log in recent_logs], default=str)}
        
        Based on the query, identify:
        1. Which logs are relevant
        2. What time range to focus on
        3. What service(s) to filter by
        4. What severity levels to include
        
        Return a JSON response with:
        {{
            "interpreted_query": "What the user is looking for",
            "filters": {{
                "services": ["list", "of", "services"],
                "severity": ["ERROR", "WARNING", "INFO"],
                "time_range": "last 1 hour" or "last 24 hours" etc
            }},
            "summary": "Brief summary of what was found"
        }}
        """
        
        response = model.generate_content(prompt)
        ai_analysis = json.loads(response.text)
        
        # Apply filters based on AI analysis
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        where_conditions = []
        params = []
        
        if ai_analysis.get("filters", {}).get("services"):
            services = ai_analysis["filters"]["services"]
            placeholders = ",".join(["%s"] * len(services))
            where_conditions.append(f"service IN ({placeholders})")
            params.extend(services)
        
        if ai_analysis.get("filters", {}).get("severity"):
            severities = ai_analysis["filters"]["severity"]
            placeholders = ",".join(["%s"] * len(severities))
            where_conditions.append(f"severity IN ({placeholders})")
            params.extend(severities)
        
        # Time range filtering
        time_range = ai_analysis.get("filters", {}).get("time_range", "")
        if "1 hour" in time_range.lower():
            where_conditions.append("timestamp >= NOW() - INTERVAL '1 hour'")
        elif "24 hours" in time_range.lower() or "1 day" in time_range.lower():
            where_conditions.append("timestamp >= NOW() - INTERVAL '24 hours'")
        
        query_sql = "SELECT * FROM logs"
        if where_conditions:
            query_sql += " WHERE " + " AND ".join(where_conditions)
        query_sql += " ORDER BY timestamp DESC LIMIT 20"
        
        cur.execute(query_sql, params)
        filtered_logs = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "ai_analysis": ai_analysis,
            "logs": [dict(log) for log in filtered_logs],
            "total_found": len(filtered_logs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI search failed: {str(e)}")

# 🕐 Incident Timeline
@app.get("/timeline")
def get_incident_timeline(hours: int = 24):
    """Get timeline of incidents and events for visualization"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute(
        """
        SELECT 
            timestamp,
            service,
            severity,
            ai_summary,
            CASE 
                WHEN severity = 'ERROR' THEN 'error'
                WHEN severity = 'WARNING' THEN 'warning'
                ELSE 'normal'
            END as event_type
        FROM logs
        WHERE timestamp >= NOW() - INTERVAL '%s hours'
        ORDER BY timestamp DESC
        """,
        (hours,)
    )
    
    events = cur.fetchall()
    cur.close()
    conn.close()
    
    # Group events by hour for timeline visualization
    timeline = {}
    for event in events:
        hour_key = event['timestamp'].strftime('%Y-%m-%d %H:00')
        if hour_key not in timeline:
            timeline[hour_key] = {
                'timestamp': hour_key,
                'events': [],
                'error_count': 0,
                'warning_count': 0,
                'normal_count': 0
            }
        
        timeline[hour_key]['events'].append(dict(event))
        if event['event_type'] == 'error':
            timeline[hour_key]['error_count'] += 1
        elif event['event_type'] == 'warning':
            timeline[hour_key]['warning_count'] += 1
        else:
            timeline[hour_key]['normal_count'] += 1
    
    return {"timeline": list(timeline.values())}

# 🏥 Service Health Status
@app.get("/service-health")
def get_service_health():
    """Get health status of all microservices"""
    # Online Boutique services
    services = [
        "frontend", "cartservice", "productcatalogservice", "recommendationservice",
        "shippingservice", "checkoutservice", "paymentservice", "currencyservice",
        "adservice", "emailservice", "loadgenerator"
    ]
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    health_status = {}
    
    for service in services:
        # Get recent error rate for this service
        cur.execute(
            """
            SELECT 
                COUNT(*) as total_logs,
                COUNT(CASE WHEN severity = 'ERROR' THEN 1 END) as error_count,
                MAX(timestamp) as last_seen
            FROM logs 
            WHERE service = %s 
            AND timestamp >= NOW() - INTERVAL '1 hour'
            """,
            (service,)
        )
        
        result = cur.fetchone()
        if result and result['total_logs'] > 0:
            error_rate = result['error_count'] / result['total_logs']
            
            if error_rate > 0.1:  # >10% error rate
                status = "error"
            elif error_rate > 0.05:  # >5% error rate
                status = "warning"
            else:
                status = "healthy"
        else:
            status = "unknown"
        
        health_status[service] = {
            "status": status,
            "error_rate": error_rate if result else 0,
            "last_seen": result['last_seen'].isoformat() if result and result['last_seen'] else None,
            "total_logs": result['total_logs'] if result else 0
        }
    
    cur.close()
    conn.close()
    
    return {"services": health_status}

# 🤖 AI Assistant Chat
@app.post("/ai-chat")
def ai_chat(message: dict):
    """AI assistant for answering questions about logs and system health"""
    try:
        user_message = message.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get recent system data for context
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get recent logs
        cur.execute(
            """
            SELECT service, severity, ai_summary, timestamp
            FROM logs
            ORDER BY timestamp DESC
            LIMIT 20
            """
        )
        recent_logs = cur.fetchall()
        
        # Get service health
        cur.execute(
            """
            SELECT service, COUNT(*) as log_count,
                   COUNT(CASE WHEN severity = 'ERROR' THEN 1 END) as error_count
            FROM logs
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            GROUP BY service
            """
        )
        service_stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Use Gemini to answer the question
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        You are SmartGuard AI Assistant. Answer this question: "{user_message}"
        
        Recent system data:
        - Recent logs: {json.dumps([dict(log) for log in recent_logs], default=str)}
        - Service statistics: {json.dumps([dict(stat) for stat in service_stats], default=str)}
        
        Provide a helpful, concise answer about the system status, any issues, or suggestions.
        If there are errors or warnings, explain what might be causing them and suggest fixes.
        """
        
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

# 📊 Enhanced Metrics with Anomaly Detection
@app.get("/metrics-enhanced")
def get_enhanced_metrics():
    """Get enhanced metrics with anomaly detection"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get hourly metrics for the last 24 hours
    cur.execute(
        """
        SELECT 
            DATE_TRUNC('hour', timestamp) as hour,
            severity,
            COUNT(*) as count
        FROM logs
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
        GROUP BY hour, severity
        ORDER BY hour
        """
    )
    
    hourly_data = cur.fetchall()
    
    # Get service-specific metrics
    cur.execute(
        """
        SELECT 
            service,
            severity,
            COUNT(*) as count
        FROM logs
        WHERE timestamp >= NOW() - INTERVAL '1 hour'
        GROUP BY service, severity
        """
    )
    
    service_data = cur.fetchall()
    cur.close()
    conn.close()
    
    # Simple anomaly detection (spike detection)
    anomalies = []
    if hourly_data:
        # Calculate average error rate
        error_counts = [row['count'] for row in hourly_data if row['severity'] == 'ERROR']
        if error_counts:
            avg_errors = sum(error_counts) / len(error_counts)
            for row in hourly_data:
                if row['severity'] == 'ERROR' and row['count'] > avg_errors * 2:
                    anomalies.append({
                        "timestamp": row['hour'].isoformat(),
                        "type": "error_spike",
                        "count": row['count'],
                        "expected": avg_errors
                    })
    
    return {
        "hourly_metrics": [dict(row) for row in hourly_data],
        "service_metrics": [dict(row) for row in service_data],
        "anomalies": anomalies
    }

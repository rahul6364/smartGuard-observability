# smartguard.py

import os
import json
import requests
import psycopg2
from dotenv import load_dotenv
from google.cloud import logging_v2
import google.generativeai as genai
from datetime import datetime, timedelta

# 🔹 Load .env file
load_dotenv()

# 🔹 Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 🔹 GCP authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# 🔹 Initialize clients
logging_client = logging_v2.Client()
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 DB connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    """Create logs table if it doesn't exist"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            service TEXT,
            severity TEXT,
            raw_log TEXT,
            ai_summary TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def store_log(timestamp, service, severity, raw_log, ai_summary):
    """Insert log into DB"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (timestamp, service, severity, raw_log, ai_summary)
        VALUES (%s, %s, %s, %s, %s)
    """, (timestamp, service, severity, raw_log, ai_summary))
    conn.commit()
    cur.close()
    conn.close()

def fetch_logs():
    """Fetch recent error logs from GCP (last 5 minutes)"""
    now = datetime.utcnow()
    five_min_ago = now - timedelta(minutes=5)

    filter_str = f"""
        timestamp >= "{five_min_ago.isoformat()}Z"
        severity >= ERROR
    """

    entries = logging_client.list_entries(
        filter_=filter_str,
        order_by=logging_v2.DESCENDING,
        page_size=5
    )

    logs = []
    for entry in entries:
        try:
            logs.append({
                "timestamp": entry.timestamp.isoformat(),
                "service": entry.resource.labels.get("container_name", "unknown"),
                "severity": entry.severity,
                "raw_log": str(entry.payload)
            })
        except Exception as e:
            logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                "service": "unknown",
                "severity": "ERROR",
                "raw_log": str(entry)
            })
    return logs

def analyze_logs(logs):
    """Analyze logs with Gemini"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    You are SmartGuard, an AI for DevOps.
    Analyze these logs:
    {logs}

    Detect:
    - Security risks
    - Deployment issues
    - Errors or anomalies

    Respond concisely.
    """
    response = model.generate_content(prompt)
    return response.text

def send_alert(msg):
    """Send alert to Slack"""
    data = {"text": f"🚨 SmartGuard Alert 🚨\n{msg}"}
    resp = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
    if resp.status_code == 200:
        print("✅ Alert sent to Slack")
    else:
        print(f"❌ Failed to send alert: {resp.status_code}, {resp.text}")

if __name__ == "__main__":
    init_db()  # Ensure DB table exists

    logs = fetch_logs()
    print(f"📄 Got {len(logs)} logs")

    for log in logs:
        analysis = analyze_logs(log["raw_log"])
        print("\n🤖 AI Analysis:\n", analysis)

        # Save to DB
        store_log(
            timestamp=log["timestamp"],
            service=log["service"],
            severity=log["severity"],
            raw_log=log["raw_log"],
            ai_summary=analysis
        )

        # Slack alert if serious
        if "error" in analysis.lower() or "suspicious" in analysis.lower():
            send_alert(analysis)

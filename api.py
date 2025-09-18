from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

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

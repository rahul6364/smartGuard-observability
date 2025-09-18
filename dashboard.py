import streamlit as st
import requests
import pandas as pd

# 🔹 Backend API base URL (FastAPI running locally on port 8000)
API_BASE = "http://localhost:8000"

st.set_page_config(page_title="SmartGuard Dashboard", layout="wide")

st.title("🛡️ SmartGuard Dashboard")

# Sidebar for controls
st.sidebar.header("Filters")
service_filter = st.sidebar.text_input("Service name (optional)")
severity_filter = st.sidebar.text_input("Severity (optional, e.g., ERROR, WARNING, INFO)")
limit = st.sidebar.slider("Number of logs", 5, 100, 20)

# --- Metrics Section ---
st.subheader("📊 Metrics (Logs by Severity)")
try:
    resp = requests.get(f"{API_BASE}/metrics")
    if resp.status_code == 200:
        metrics = resp.json()["metrics"]
        df_metrics = pd.DataFrame(metrics)
        st.bar_chart(df_metrics.set_index("severity"))
    else:
        st.error(f"Failed to fetch metrics: {resp.text}")
except Exception as e:
    st.error(f"Error fetching metrics: {e}")

# --- Alerts Section ---
st.subheader("🚨 Critical Alerts")
try:
    resp = requests.get(f"{API_BASE}/alerts?limit=5")
    if resp.status_code == 200:
        alerts = resp.json()["alerts"]
        if alerts:
            for alert in alerts:
                st.error(f"[{alert['timestamp']}] {alert['service']} → {alert['ai_summary']}")
        else:
            st.success("✅ No critical alerts.")
    else:
        st.error(f"Failed to fetch alerts: {resp.text}")
except Exception as e:
    st.error(f"Error fetching alerts: {e}")

# --- Logs Table ---
st.subheader("📄 Logs")
try:
    params = {"limit": limit}
    if service_filter:
        params["service"] = service_filter
    if severity_filter:
        params["severity"] = severity_filter

    resp = requests.get(f"{API_BASE}/logs", params=params)
    if resp.status_code == 200:
        logs = resp.json()["logs"]
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs)
        else:
            st.info("No logs found with the given filters.")
    else:
        st.error(f"Failed to fetch logs: {resp.text}")
except Exception as e:
    st.error(f"Error fetching logs: {e}")

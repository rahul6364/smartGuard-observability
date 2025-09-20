# import streamlit as st
# import requests
# import pandas as pd

# # 🔹 Backend API base URL (FastAPI running locally on port 8000)
# API_BASE = "http://localhost:8000"

# st.set_page_config(page_title="SmartGuard Dashboard", layout="wide")

# st.title("🛡️ SmartGuard Dashboard")

# # Sidebar for controls
# st.sidebar.header("Filters")
# service_filter = st.sidebar.text_input("Service name (optional)")
# severity_filter = st.sidebar.text_input("Severity (optional, e.g., ERROR, WARNING, INFO)")
# limit = st.sidebar.slider("Number of logs", 5, 100, 20)

# # --- Metrics Section ---
# st.subheader("📊 Metrics (Logs by Severity)")
# try:
#     resp = requests.get(f"{API_BASE}/metrics")
#     if resp.status_code == 200:
#         metrics = resp.json()["metrics"]
#         df_metrics = pd.DataFrame(metrics)
#         st.bar_chart(df_metrics.set_index("severity"))
#     else:
#         st.error(f"Failed to fetch metrics: {resp.text}")
# except Exception as e:
#     st.error(f"Error fetching metrics: {e}")

# # --- Alerts Section ---
# st.subheader("🚨 Critical Alerts")
# try:
#     resp = requests.get(f"{API_BASE}/alerts?limit=5")
#     if resp.status_code == 200:
#         alerts = resp.json()["alerts"]
#         if alerts:
#             for alert in alerts:
#                 st.error(f"[{alert['timestamp']}] {alert['service']} → {alert['ai_summary']}")
#         else:
#             st.success("✅ No critical alerts.")
#     else:
#         st.error(f"Failed to fetch alerts: {resp.text}")
# except Exception as e:
#     st.error(f"Error fetching alerts: {e}")

# # --- Logs Table ---
# st.subheader("📄 Logs")
# try:
#     params = {"limit": limit}
#     if service_filter:
#         params["service"] = service_filter
#     if severity_filter:
#         params["severity"] = severity_filter

#     resp = requests.get(f"{API_BASE}/logs", params=params)
#     if resp.status_code == 200:
#         logs = resp.json()["logs"]
#         if logs:
#             df_logs = pd.DataFrame(logs)
#             st.dataframe(df_logs)
#         else:
#             st.info("No logs found with the given filters.")
#     else:
#         st.error(f"Failed to fetch logs: {resp.text}")
# except Exception as e:
#     st.error(f"Error fetching logs: {e}")
# import streamlit as st
# import requests
# import time
# import pandas as pd
# import plotly.express as px

# API_BASE = "http://localhost:8000"  # FastAPI backend URL

# st.set_page_config(page_title="SmartGuard Dashboard", layout="wide")

# st.title("🛡️ SmartGuard Dashboard")

# # Sidebar filters
# st.sidebar.header("Filters")
# service_filter = st.sidebar.text_input("Service name (optional)")
# severity_filter = st.sidebar.text_input("Severity (e.g., ERROR, WARNING, INFO)")
# num_logs = st.sidebar.slider("Number of logs", 5, 100, 20)

# # --- Streamlit containers (for live updates) ---
# metrics_placeholder = st.empty()
# alerts_placeholder = st.empty()
# logs_placeholder = st.empty()

# def fetch_data(endpoint):
#     try:
#         res = requests.get(f"{API_BASE}/{endpoint}")
#         if res.status_code == 200:
#             return res.json()
#     except Exception as e:
#         st.error(f"API error: {e}")
#     return {}

# # --- Live refresh loop ---
# while True:
#     # Fetch logs
#     logs_data = fetch_data("logs")
#     if logs_data and "logs" in logs_data:
#         logs_df = pd.DataFrame(logs_data["logs"])
#         if not logs_df.empty:
#             # Chart by severity
#             fig = px.histogram(logs_df, x="severity", title="Logs by Severity", color="severity")
#             metrics_placeholder.plotly_chart(fig, use_container_width=True)

#             # Show latest logs
#             with logs_placeholder.container():
#                 st.subheader("📜 Recent Logs")
#                 for _, row in logs_df.head(num_logs).iterrows():
#                     st.write(f"[{row['timestamp']}] {row['service']} - {row['severity']}: {row['ai_summary']}")
#     else:
#         metrics_placeholder.warning("No log data available.")

#     # Fetch alerts
#     alerts_data = fetch_data("alerts")
#     with alerts_placeholder.container():
#         st.subheader("🚨 Active Alerts")
#         if alerts_data and "alerts" in alerts_data:
#             if alerts_data["alerts"]:
#                 for alert in alerts_data["alerts"]:
#                     severity = alert.get("severity", "Unknown")
#                     desc = alert.get("description", "No description available")
#                     ts = alert.get("timestamp", "N/A")
#                     st.error(f"[{severity}] {desc} @ {ts}")
#             else:
#                 st.success("✅ No active alerts.")
#         else:
#             st.warning("No alert data available.")

#     time.sleep(5)  # refresh every 5 sec

# Import the enhanced dashboard
from enhanced_dashboard import main

# Run the enhanced dashboard
if __name__ == "__main__":
    main()

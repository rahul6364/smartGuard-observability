import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Configure page
st.set_page_config(
    page_title="SmartGuard AI Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sample data for demo
def generate_sample_data():
    """Generate sample data for demonstration"""
    services = [
        "frontend", "cartservice", "productcatalogservice", "recommendationservice",
        "shippingservice", "checkoutservice", "paymentservice", "currencyservice",
        "adservice", "emailservice", "loadgenerator"
    ]
    
    severities = ["ERROR", "WARNING", "INFO"]
    severity_weights = [0.1, 0.2, 0.7]  # 10% errors, 20% warnings, 70% info
    
    logs = []
    for i in range(50):
        service = random.choice(services)
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
            "service": service,
            "severity": severity,
            "message": message,
            "ai_summary": ai_summary,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return logs

def main():
    st.markdown('<h1 class="main-header">🛡️ SmartGuard AI Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/667eea/ffffff?text=SmartGuard", width=200)
        st.write("**Demo Mode** - Using sample data")
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Generate sample data
    logs = generate_sample_data()
    logs_df = pd.DataFrame(logs)
    
    # Key metrics
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        error_count = len(logs_df[logs_df['severity'] == 'ERROR'])
        st.metric("🚨 Errors", error_count)
    
    with col2:
        warning_count = len(logs_df[logs_df['severity'] == 'WARNING'])
        st.metric("⚠️ Warnings", warning_count)
    
    with col3:
        info_count = len(logs_df[logs_df['severity'] == 'INFO'])
        st.metric("ℹ️ Info", info_count)
    
    with col4:
        unique_services = logs_df['service'].nunique()
        st.metric("🏥 Services", unique_services)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Logs by Severity")
        severity_counts = logs_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index, 
                     color_discrete_map={'ERROR': 'red', 'WARNING': 'orange', 'INFO': 'blue'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏥 Logs by Service")
        service_counts = logs_df['service'].value_counts().head(10)
        fig = px.bar(x=service_counts.values, y=service_counts.index, orientation='h')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent logs
    st.subheader("📜 Recent Logs")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_service = st.selectbox("Filter by Service", ["All"] + list(logs_df['service'].unique()))
    with col2:
        selected_severity = st.selectbox("Filter by Severity", ["All"] + list(logs_df['severity'].unique()))
    
    # Apply filters
    filtered_logs = logs_df.copy()
    if selected_service != "All":
        filtered_logs = filtered_logs[filtered_logs['service'] == selected_service]
    if selected_severity != "All":
        filtered_logs = filtered_logs[filtered_logs['severity'] == selected_severity]
    
    # Display logs
    for _, log in filtered_logs.head(20).iterrows():
        severity_icon = {"ERROR": "🔴", "WARNING": "⚠️", "INFO": "ℹ️"}.get(log["severity"], "📝")
        
        with st.expander(f"{severity_icon} {log['service']} - {log['timestamp']}"):
            st.write(f"**Severity:** {log['severity']}")
            st.write(f"**Message:** {log['message']}")
            st.write(f"**AI Summary:** {log['ai_summary']}")
    
    # Service health
    st.subheader("🏥 Service Health")
    
    service_health = []
    for service in logs_df['service'].unique():
        service_logs = logs_df[logs_df['service'] == service]
        error_rate = len(service_logs[service_logs['severity'] == 'ERROR']) / len(service_logs)
        
        if error_rate > 0.1:
            status = "Error"
            color = "red"
        elif error_rate > 0.05:
            status = "Warning"
            color = "orange"
        else:
            status = "Healthy"
            color = "green"
        
        service_health.append({
            "Service": service,
            "Status": status,
            "Error Rate": f"{error_rate:.1%}",
            "Total Logs": len(service_logs)
        })
    
    health_df = pd.DataFrame(service_health)
    
    # Color code the status
    def color_status(val):
        if val == "Healthy":
            return "background-color: #d4edda; color: #155724"
        elif val == "Warning":
            return "background-color: #fff3cd; color: #856404"
        elif val == "Error":
            return "background-color: #f8d7da; color: #721c24"
        else:
            return "background-color: #f8f9fa; color: #6c757d"
    
    styled_df = health_df.style.applymap(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)
    
    # AI Assistant Demo
    st.subheader("🤖 AI Assistant Demo")
    st.info("This is a demo version. In the full version, you can chat with an AI assistant about your system health!")
    
    # Quick stats
    st.subheader("📊 Quick Stats")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Logs", len(logs_df))
    with col2:
        avg_logs_per_service = len(logs_df) / len(logs_df['service'].unique())
        st.metric("Avg Logs/Service", f"{avg_logs_per_service:.1f}")
    with col3:
        health_score = max(0, 100 - (error_count * 2) - (warning_count * 1))
        st.metric("Health Score", f"{health_score}/100")

if __name__ == "__main__":
    main()

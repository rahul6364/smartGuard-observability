import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import json
from datetime import datetime, timedelta
import numpy as np
from streamlit_chat import message
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components

# Configure page
st.set_page_config(
    page_title="SmartGuard AI Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE = "http://localhost:8000"

# Custom CSS for modern UI
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
    
    .status-healthy { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-error { color: #dc3545; font-weight: bold; }
    .status-unknown { color: #6c757d; font-weight: bold; }
    
    .timeline-event {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        border-left: 4px solid;
    }
    
    .timeline-error { border-left-color: #dc3545; background-color: #f8d7da; }
    .timeline-warning { border-left-color: #ffc107; background-color: #fff3cd; }
    .timeline-normal { border-left-color: #28a745; background-color: #d4edda; }
    
    .service-node {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 0.5rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    
    .ai-message {
        background-color: #f3e5f5;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data(ttl=30)
def fetch_data(endpoint, params=None):
    """Fetch data from API with caching"""
    try:
        if params:
            response = requests.get(f"{API_BASE}/{endpoint}", params=params, timeout=5)
        else:
            response = requests.get(f"{API_BASE}/{endpoint}", timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"API error: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Cannot connect to API. Make sure the backend is running on http://localhost:8000")
        return {}
    except Exception as e:
        st.warning(f"Connection error: {e}")
        return {}

def post_data(endpoint, data):
    """Post data to API"""
    try:
        response = requests.post(f"{API_BASE}/{endpoint}", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"API error: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Cannot connect to API. Make sure the backend is running on http://localhost:8000")
        return {}
    except Exception as e:
        st.warning(f"Connection error: {e}")
        return {}

# Main App
def main():
    st.markdown('<h1 class="main-header">🛡️ SmartGuard AI Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/667eea/ffffff?text=SmartGuard", width=200)
        
        selected = option_menu(
            "Navigation",
            ["🏠 Dashboard", "🔍 Log Explorer", "📊 Timeline", "🤖 AI Assistant", "🏥 Service Health", "🚨 Alerts", "📈 Metrics"],
            icons=['house', 'search', 'clock', 'robot', 'heart-pulse', 'exclamation-triangle', 'graph-up'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#667eea", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
    
    # Dashboard Overview
    if selected == "🏠 Dashboard":
        show_dashboard_overview()
    
    # AI-Powered Log Explorer
    elif selected == "🔍 Log Explorer":
        show_log_explorer()
    
    # Incident Timeline
    elif selected == "📊 Timeline":
        show_incident_timeline()
    
    # AI Assistant
    elif selected == "🤖 AI Assistant":
        show_ai_assistant()
    
    # Service Health
    elif selected == "🏥 Service Health":
        show_service_health()
    
    # Alerts Center
    elif selected == "🚨 Alerts":
        show_alerts_center()
    
    # Enhanced Metrics
    elif selected == "📈 Metrics":
        show_enhanced_metrics()

def show_dashboard_overview():
    """Main dashboard overview with key metrics"""
    st.header("📊 System Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Get basic metrics
    metrics_data = fetch_data("metrics")
    alerts_data = fetch_data("alerts", {"limit": 5})
    service_health = fetch_data("service-health")
    
    with col1:
        if metrics_data and "metrics" in metrics_data:
            error_count = sum(m["count"] for m in metrics_data["metrics"] if m["severity"] == "ERROR")
            st.metric("🚨 Errors", error_count)
        else:
            st.metric("🚨 Errors", "N/A")
    
    with col2:
        if metrics_data and "metrics" in metrics_data:
            warning_count = sum(m["count"] for m in metrics_data["metrics"] if m["severity"] == "WARNING")
            st.metric("⚠️ Warnings", warning_count)
        else:
            st.metric("⚠️ Warnings", "N/A")
    
    with col3:
        if service_health and "services" in service_health:
            healthy_services = sum(1 for s in service_health["services"].values() if s["status"] == "healthy")
            total_services = len(service_health["services"])
            st.metric("✅ Healthy Services", f"{healthy_services}/{total_services}")
        else:
            st.metric("✅ Healthy Services", "N/A")
    
    with col4:
        if alerts_data and "alerts" in alerts_data:
            active_alerts = len(alerts_data["alerts"])
            st.metric("🔔 Active Alerts", active_alerts)
        else:
            st.metric("🔔 Active Alerts", "N/A")
    
    # Recent logs
    st.subheader("📜 Recent Activity")
    logs_data = fetch_data("logs", {"limit": 10})
    
    if logs_data and "logs" in logs_data:
        logs_df = pd.DataFrame(logs_data["logs"])
        if not logs_df.empty:
            # Display logs in a nice format
            for _, log in logs_df.iterrows():
                severity_icon = {"ERROR": "🔴", "WARNING": "⚠️", "INFO": "ℹ️"}.get(log["severity"], "📝")
                st.write(f"{severity_icon} **{log['service']}** - {log['timestamp']}")
                st.write(f"   {log['ai_summary']}")
                st.write("---")
        else:
            st.info("No recent logs found")
    else:
        st.warning("Unable to fetch recent logs")

def show_log_explorer():
    """AI-powered log explorer with natural language search"""
    st.header("🔍 AI-Powered Log Explorer")
    st.markdown("Ask questions about your logs in plain English!")
    
    # Natural language search
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Ask about your logs...",
            placeholder="e.g., 'Show me paymentservice errors in the last hour' or 'Why did shippingservice fail yesterday?'",
            key="log_search"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary")
    
    if search_button and search_query:
        with st.spinner("🤖 AI is analyzing your query..."):
            ai_search_result = post_data("ai-search", {"query": search_query})
            
            if ai_search_result:
                # Display AI analysis
                st.subheader("🤖 AI Analysis")
                ai_analysis = ai_search_result.get("ai_analysis", {})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Interpreted Query:**")
                    st.info(ai_analysis.get("interpreted_query", "N/A"))
                
                with col2:
                    st.write("**Summary:**")
                    st.success(ai_analysis.get("summary", "N/A"))
                
                # Display filters applied
                filters = ai_analysis.get("filters", {})
                if filters:
                    st.write("**Filters Applied:**")
                    filter_text = []
                    if filters.get("services"):
                        filter_text.append(f"Services: {', '.join(filters['services'])}")
                    if filters.get("severity"):
                        filter_text.append(f"Severity: {', '.join(filters['severity'])}")
                    if filters.get("time_range"):
                        filter_text.append(f"Time Range: {filters['time_range']}")
                    
                    st.write(" | ".join(filter_text))
                
                # Display results
                st.subheader(f"📋 Search Results ({ai_search_result.get('total_found', 0)} found)")
                
                logs = ai_search_result.get("logs", [])
                if logs:
                    for log in logs:
                        severity_icon = {"ERROR": "🔴", "WARNING": "⚠️", "INFO": "ℹ️"}.get(log.get("severity"), "📝")
                        
                        with st.expander(f"{severity_icon} {log.get('service', 'Unknown')} - {log.get('timestamp', 'N/A')}"):
                            st.write("**AI Summary:**")
                            st.write(log.get("ai_summary", "No summary available"))
                            st.write("**Raw Log:**")
                            st.code(log.get("raw_log", "No raw log available"))
                else:
                    st.info("No logs found matching your query")
            else:
                st.error("Failed to process your query. Please try again.")
    
    # Quick search examples
    st.subheader("💡 Quick Search Examples")
    examples = [
        "Show me all errors from the last hour",
        "What's wrong with the paymentservice?",
        "Find all warnings related to database connections",
        "Show me logs from shippingservice in the last 24 hours",
        "What errors occurred yesterday?"
    ]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(example, key=f"example_{i}"):
                # Use a different approach to trigger search
                st.session_state[f"search_query_{i}"] = example
                st.rerun()
    
    # Check if any example was clicked
    for i, example in enumerate(examples):
        if f"search_query_{i}" in st.session_state:
            # Update the search query and trigger search
            search_query = st.session_state[f"search_query_{i}"]
            del st.session_state[f"search_query_{i}"]  # Clean up
            
            # Trigger the search automatically
            with st.spinner("🤖 AI is analyzing your query..."):
                ai_search_result = post_data("ai-search", {"query": search_query})
                
                if ai_search_result:
                    # Display AI analysis
                    st.subheader("🤖 AI Analysis")
                    ai_analysis = ai_search_result.get("ai_analysis", {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Interpreted Query:**")
                        st.info(ai_analysis.get("interpreted_query", "N/A"))
                    
                    with col2:
                        st.write("**Summary:**")
                        st.success(ai_analysis.get("summary", "N/A"))
                    
                    # Display filters applied
                    filters = ai_analysis.get("filters", {})
                    if filters:
                        st.write("**Filters Applied:**")
                        filter_text = []
                        if filters.get("services"):
                            filter_text.append(f"Services: {', '.join(filters['services'])}")
                        if filters.get("severity"):
                            filter_text.append(f"Severity: {', '.join(filters['severity'])}")
                        if filters.get("time_range"):
                            filter_text.append(f"Time Range: {filters['time_range']}")
                        
                        st.write(" | ".join(filter_text))
                    
                    # Display results
                    st.subheader(f"📋 Search Results ({ai_search_result.get('total_found', 0)} found)")
                    
                    logs = ai_search_result.get("logs", [])
                    if logs:
                        for log in logs:
                            severity_icon = {"ERROR": "🔴", "WARNING": "⚠️", "INFO": "ℹ️"}.get(log.get("severity"), "📝")
                            
                            with st.expander(f"{severity_icon} {log.get('service', 'Unknown')} - {log.get('timestamp', 'N/A')}"):
                                st.write("**AI Summary:**")
                                st.write(log.get("ai_summary", "No summary available"))
                                st.write("**Raw Log:**")
                                st.code(log.get("raw_log", "No raw log available"))
                    else:
                        st.info("No logs found matching your query")
                else:
                    st.error("Failed to process your query. Please try again.")

def show_incident_timeline():
    """Interactive incident timeline"""
    st.header("📊 Incident Timeline")
    
    # Timeline controls
    col1, col2 = st.columns([1, 3])
    with col1:
        hours = st.selectbox("Time Range", [1, 6, 12, 24, 48, 72], index=3)
    
    with col2:
        st.write(f"Showing events from the last {hours} hours")
    
    # Fetch timeline data
    timeline_data = fetch_data("timeline", {"hours": hours})
    
    if timeline_data and "timeline" in timeline_data:
        timeline = timeline_data["timeline"]
        
        if timeline:
            # Create timeline visualization
            st.subheader("📈 Timeline Overview")
            
            # Prepare data for plotting
            timeline_df = pd.DataFrame(timeline)
            timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
            
            # Create timeline chart
            fig = go.Figure()
            
            # Add error events
            error_data = timeline_df[timeline_df['error_count'] > 0]
            if not error_data.empty:
                fig.add_trace(go.Scatter(
                    x=error_data['timestamp'],
                    y=error_data['error_count'],
                    mode='markers+lines',
                    name='Errors',
                    marker=dict(color='red', size=10),
                    line=dict(color='red', width=2)
                ))
            
            # Add warning events
            warning_data = timeline_df[timeline_df['warning_count'] > 0]
            if not warning_data.empty:
                fig.add_trace(go.Scatter(
                    x=warning_data['timestamp'],
                    y=warning_data['warning_count'],
                    mode='markers+lines',
                    name='Warnings',
                    marker=dict(color='orange', size=8),
                    line=dict(color='orange', width=2)
                ))
            
            # Add normal events
            normal_data = timeline_df[timeline_df['normal_count'] > 0]
            if not normal_data.empty:
                fig.add_trace(go.Scatter(
                    x=normal_data['timestamp'],
                    y=normal_data['normal_count'],
                    mode='markers+lines',
                    name='Normal',
                    marker=dict(color='green', size=6),
                    line=dict(color='green', width=1)
                ))
            
            fig.update_layout(
                title="System Events Timeline",
                xaxis_title="Time",
                yaxis_title="Event Count",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed timeline view
            st.subheader("📋 Detailed Timeline")
            
            for hour_data in timeline:
                if hour_data['events']:
                    st.write(f"**{hour_data['timestamp']}**")
                    
                    # Event counts
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Errors", hour_data['error_count'], delta=None)
                    with col2:
                        st.metric("Warnings", hour_data['warning_count'], delta=None)
                    with col3:
                        st.metric("Normal", hour_data['normal_count'], delta=None)
                    
                    # Individual events
                    for event in hour_data['events']:
                        event_type = event.get('event_type', 'normal')
                        severity_icon = {"error": "🔴", "warning": "⚠️", "normal": "🟢"}.get(event_type, "📝")
                        
                        event_class = f"timeline-{event_type}"
                        st.markdown(f"""
                        <div class="timeline-event {event_class}">
                            {severity_icon} <strong>{event.get('service', 'Unknown')}</strong> - {event.get('timestamp', 'N/A')}<br>
                            {event.get('ai_summary', 'No summary available')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.write("---")
        else:
            st.info("No events found in the selected time range")
    else:
        st.warning("Unable to fetch timeline data")

def show_ai_assistant():
    """AI Assistant chatbot"""
    st.header("🤖 SmartGuard AI Assistant")
    st.markdown("Ask me anything about your system health, logs, or get suggestions!")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat input
    user_input = st.text_input("Ask me anything...", key="chat_input")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        send_button = st.button("Send", type="primary")
    
    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Process user input
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("🤖 AI is thinking..."):
            ai_response = post_data("ai-chat", {"message": user_input})
            
            if ai_response and "response" in ai_response:
                # Add AI response to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": ai_response["response"]
                })
            else:
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": "Sorry, I couldn't process your request. Please try again."
                })
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💬 Conversation")
        
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 SmartGuard AI:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Quick questions
    st.subheader("💡 Quick Questions")
    quick_questions = [
        "What's the current system status?",
        "Are there any errors I should be concerned about?",
        "Which services are having issues?",
        "What can I do to improve system performance?",
        "Show me a summary of recent activity"
    ]
    
    cols = st.columns(len(quick_questions))
    for i, question in enumerate(quick_questions):
        with cols[i]:
            if st.button(question, key=f"quick_{i}"):
                # Use a different approach to trigger chat
                st.session_state[f"quick_question_{i}"] = question
                st.rerun()
    
    # Check if any quick question was clicked
    for i, question in enumerate(quick_questions):
        if f"quick_question_{i}" in st.session_state:
            # Process the quick question
            user_input = st.session_state[f"quick_question_{i}"]
            del st.session_state[f"quick_question_{i}"]  # Clean up
            
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("🤖 AI is thinking..."):
                ai_response = post_data("ai-chat", {"message": user_input})
                
                if ai_response and "response" in ai_response:
                    # Add AI response to history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": ai_response["response"]
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": "Sorry, I couldn't process your request. Please try again."
                    })
            
            st.rerun()

def show_service_health():
    """Service health view with microservice network graph"""
    st.header("🏥 Service Health Dashboard")
    
    # Fetch service health data
    health_data = fetch_data("service-health")
    
    if health_data and "services" in health_data:
        services = health_data["services"]
        
        # Service health overview
        st.subheader("📊 Health Overview")
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes for each service
        for service_name, service_data in services.items():
            status = service_data.get("status", "unknown")
            error_rate = service_data.get("error_rate", 0)
            
            # Color based on status
            if status == "healthy":
                color = "green"
            elif status == "warning":
                color = "orange"
            elif status == "error":
                color = "red"
            else:
                color = "gray"
            
            G.add_node(service_name, 
                      status=status, 
                      error_rate=error_rate,
                      color=color)
        
        # Add edges (simplified connections)
        # In a real system, you'd have actual service dependencies
        service_list = list(services.keys())
        for i, service in enumerate(service_list):
            if i < len(service_list) - 1:
                G.add_edge(service, service_list[i + 1])
        
        # Create network visualization
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Create plotly network graph
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            service_data = services[node]
            status = service_data.get("status", "unknown")
            error_rate = service_data.get("error_rate", 0)
            total_logs = service_data.get("total_logs", 0)
            
            node_text.append(f"{node}<br>Status: {status}<br>Error Rate: {error_rate:.2%}<br>Logs: {total_logs}")
            
            if status == "healthy":
                node_colors.append("green")
            elif status == "warning":
                node_colors.append("orange")
            elif status == "error":
                node_colors.append("red")
            else:
                node_colors.append("gray")
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node for node in G.nodes()],
            textposition="middle center",
            hovertext=node_text,
            marker=dict(
                size=50,
                color=node_colors,
                line=dict(width=2, color='white')
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Microservice Health Network',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Click on nodes to see details",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor="left", yanchor="bottom",
                               font=dict(color="gray", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           height=500
                       ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed service status table
        st.subheader("📋 Detailed Service Status")
        
        service_df = pd.DataFrame([
            {
                "Service": service,
                "Status": data.get("status", "unknown").title(),
                "Error Rate": f"{data.get('error_rate', 0):.2%}",
                "Total Logs": data.get("total_logs", 0),
                "Last Seen": data.get("last_seen", "Never")
            }
            for service, data in services.items()
        ])
        
        # Color code the status column
        def color_status(val):
            if val == "Healthy":
                return "background-color: #d4edda; color: #155724"
            elif val == "Warning":
                return "background-color: #fff3cd; color: #856404"
            elif val == "Error":
                return "background-color: #f8d7da; color: #721c24"
            else:
                return "background-color: #f8f9fa; color: #6c757d"
        
        styled_df = service_df.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)
        
    else:
        st.warning("Unable to fetch service health data")

def show_alerts_center():
    """Enhanced alerts center with AI-generated incident reports"""
    st.header("🚨 Alert Center")
    
    # Fetch alerts
    alerts_data = fetch_data("alerts", {"limit": 20})
    
    if alerts_data and "alerts" in alerts_data:
        alerts = alerts_data["alerts"]
        
        if alerts:
            st.subheader(f"🔔 Active Alerts ({len(alerts)})")
            
            # Alert summary
            col1, col2, col3 = st.columns(3)
            with col1:
                error_alerts = sum(1 for alert in alerts if alert.get("severity") == "ERROR")
                st.metric("Critical Alerts", error_alerts)
            with col2:
                warning_alerts = sum(1 for alert in alerts if alert.get("severity") == "WARNING")
                st.metric("Warning Alerts", warning_alerts)
            with col3:
                st.metric("Total Alerts", len(alerts))
            
            # Individual alerts
            for i, alert in enumerate(alerts):
                severity = alert.get("severity", "UNKNOWN")
                service = alert.get("service", "Unknown")
                timestamp = alert.get("timestamp", "N/A")
                ai_summary = alert.get("ai_summary", "No summary available")
                
                # Color coding
                if severity == "ERROR":
                    alert_color = "red"
                    icon = "🔴"
                elif severity == "WARNING":
                    alert_color = "orange"
                    icon = "⚠️"
                else:
                    alert_color = "blue"
                    icon = "ℹ️"
                
                with st.expander(f"{icon} {severity} - {service} ({timestamp})"):
                    st.write("**AI Summary:**")
                    st.write(ai_summary)
                    
                    # AI-generated suggested fix
                    st.write("**🤖 Suggested Actions:**")
                    if "error" in ai_summary.lower():
                        st.write("• Check service logs for detailed error information")
                        st.write("• Verify service dependencies are healthy")
                        st.write("• Consider restarting the service if issues persist")
                    elif "warning" in ai_summary.lower():
                        st.write("• Monitor the service closely")
                        st.write("• Check resource utilization")
                        st.write("• Review recent configuration changes")
                    else:
                        st.write("• No specific actions required")
                        st.write("• Continue monitoring")
                    
                    # Raw log details
                    if "raw_log" in alert:
                        st.write("**Raw Log Details:**")
                        st.code(alert["raw_log"], language="text")
        else:
            st.success("✅ No active alerts! Your system is running smoothly.")
    else:
        st.warning("Unable to fetch alerts data")
    
    # Alert history chart
    st.subheader("📈 Alert Trends")
    
    # Get timeline data for alert trends
    timeline_data = fetch_data("timeline", {"hours": 24})
    
    if timeline_data and "timeline" in timeline_data:
        timeline = timeline_data["timeline"]
        timeline_df = pd.DataFrame(timeline)
        
        if not timeline_df.empty:
            timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timeline_df['timestamp'],
                y=timeline_df['error_count'],
                mode='lines+markers',
                name='Errors',
                line=dict(color='red', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=timeline_df['timestamp'],
                y=timeline_df['warning_count'],
                mode='lines+markers',
                name='Warnings',
                line=dict(color='orange', width=2)
            ))
            
            fig.update_layout(
                title="Alert Trends (Last 24 Hours)",
                xaxis_title="Time",
                yaxis_title="Alert Count",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_enhanced_metrics():
    """Enhanced metrics with anomaly detection"""
    st.header("📈 Enhanced Metrics & Anomaly Detection")
    
    # Fetch enhanced metrics
    metrics_data = fetch_data("metrics-enhanced")
    
    if metrics_data:
        # Anomaly detection section
        st.subheader("🔍 AI-Detected Anomalies")
        
        anomalies = metrics_data.get("anomalies", [])
        if anomalies:
            st.warning(f"🚨 {len(anomalies)} anomaly(ies) detected!")
            
            for anomaly in anomalies:
                st.write(f"**{anomaly.get('type', 'Unknown')}** at {anomaly.get('timestamp', 'N/A')}")
                st.write(f"Count: {anomaly.get('count', 0)} (Expected: {anomaly.get('expected', 0):.1f})")
                st.write("---")
        else:
            st.success("✅ No anomalies detected in the current data")
        
        # Hourly metrics chart
        st.subheader("📊 Hourly Metrics")
        
        hourly_metrics = metrics_data.get("hourly_metrics", [])
        if hourly_metrics:
            hourly_df = pd.DataFrame(hourly_metrics)
            if not hourly_df.empty and 'hour' in hourly_df.columns and 'severity' in hourly_df.columns:
                hourly_df['hour'] = pd.to_datetime(hourly_df['hour'])
                
                # Pivot for better visualization
                try:
                    pivot_df = hourly_df.pivot(index='hour', columns='severity', values='count').fillna(0)
                    
                    fig = px.bar(
                        pivot_df.reset_index(),
                        x='hour',
                        y=pivot_df.columns,
                        title="Logs by Severity Over Time",
                        color_discrete_map={
                            'ERROR': 'red',
                            'WARNING': 'orange',
                            'INFO': 'blue'
                        }
                    )
                    
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Log Count",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create hourly metrics chart: {e}")
                    st.dataframe(hourly_df)
            else:
                st.warning("No hourly metrics data available")
        
        # Service-specific metrics
        st.subheader("🏥 Service-Specific Metrics")
        
        service_metrics = metrics_data.get("service_metrics", [])
        if service_metrics:
            service_df = pd.DataFrame(service_metrics)
            
            if not service_df.empty and 'service' in service_df.columns and 'severity' in service_df.columns:
                # Create service metrics heatmap
                try:
                    pivot_service = service_df.pivot(index='service', columns='severity', values='count').fillna(0)
                    
                    fig = px.imshow(
                        pivot_service.values,
                        x=pivot_service.columns,
                        y=pivot_service.index,
                        title="Service Health Heatmap",
                        color_continuous_scale='RdYlGn_r',
                        aspect="auto"
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create service heatmap: {e}")
                
                # Service metrics table
                st.subheader("📋 Detailed Service Metrics")
                st.dataframe(service_df, use_container_width=True)
            else:
                st.warning("No service metrics data available")
        
        # System health score
        st.subheader("💯 System Health Score")
        
        if hourly_metrics:
            # Calculate a simple health score
            total_logs = sum(m['count'] for m in hourly_metrics)
            error_logs = sum(m['count'] for m in hourly_metrics if m['severity'] == 'ERROR')
            warning_logs = sum(m['count'] for m in hourly_metrics if m['severity'] == 'WARNING')
            
            if total_logs > 0:
                error_rate = error_logs / total_logs
                warning_rate = warning_logs / total_logs
                
                # Health score calculation (0-100)
                health_score = max(0, 100 - (error_rate * 100) - (warning_rate * 50))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Health Score", f"{health_score:.1f}/100")
                with col2:
                    st.metric("Error Rate", f"{error_rate:.2%}")
                with col3:
                    st.metric("Warning Rate", f"{warning_rate:.2%}")
                
                # Health score visualization
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = health_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "System Health"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Unable to fetch enhanced metrics data")

# Auto-refresh functionality
if st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False):
    time.sleep(30)
    st.rerun()

# Run the main app
if __name__ == "__main__":
    main()

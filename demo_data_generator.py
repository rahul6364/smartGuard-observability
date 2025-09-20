#!/usr/bin/env python3
"""
Demo Data Generator for SmartGuard Dashboard
This script generates sample log data for testing the dashboard.
"""

import random
import json
from datetime import datetime, timedelta
import requests
import time

# Sample services from Online Boutique
SERVICES = [
    "frontend", "cartservice", "productcatalogservice", "recommendationservice",
    "shippingservice", "checkoutservice", "paymentservice", "currencyservice",
    "adservice", "emailservice", "loadgenerator"
]

# Sample log messages
ERROR_MESSAGES = [
    "Database connection failed: timeout after 30 seconds",
    "Payment processing error: invalid credit card format",
    "Shipping service unavailable: external API rate limit exceeded",
    "Product catalog service error: failed to load product data",
    "Recommendation engine failed: insufficient user data",
    "Checkout process error: inventory validation failed",
    "Currency conversion error: invalid exchange rate",
    "Ad service error: failed to fetch personalized ads",
    "Email service error: SMTP server connection refused",
    "Load generator error: unable to simulate user traffic"
]

WARNING_MESSAGES = [
    "High memory usage detected: 85% of allocated memory",
    "Slow response time: 2.5 seconds average response time",
    "Database connection pool nearly exhausted",
    "Cache hit rate below threshold: 60%",
    "External service response time increased",
    "Disk space usage high: 80% of available space",
    "Network latency spike detected",
    "CPU usage above normal: 75%",
    "Database query performance degraded",
    "Service dependency health check failed"
]

INFO_MESSAGES = [
    "User session started successfully",
    "Product recommendation generated",
    "Payment processed successfully",
    "Order shipped to customer",
    "Inventory updated",
    "User authentication completed",
    "Cache refreshed successfully",
    "Health check passed",
    "Service started successfully",
    "Configuration loaded"
]

# AI-generated summaries
AI_SUMMARIES = {
    "ERROR": [
        "Critical database connectivity issue affecting payment processing",
        "External API rate limiting causing service degradation",
        "Configuration error preventing proper service initialization",
        "Resource exhaustion leading to service unavailability",
        "Network timeout causing transaction failures"
    ],
    "WARNING": [
        "Performance degradation detected in service response times",
        "Resource utilization approaching critical thresholds",
        "External dependency showing signs of instability",
        "Cache performance below expected levels",
        "System load approaching capacity limits"
    ],
    "INFO": [
        "Normal operation with successful user interactions",
        "Service functioning within expected parameters",
        "Routine maintenance completed successfully",
        "User activity processed without issues",
        "System health checks passing normally"
    ]
}

def generate_log_entry():
    """Generate a single log entry"""
    service = random.choice(SERVICES)
    severity = random.choices(
        ["ERROR", "WARNING", "INFO"],
        weights=[0.1, 0.2, 0.7]  # 10% errors, 20% warnings, 70% info
    )[0]
    
    # Generate timestamp within last 24 hours
    now = datetime.now()
    hours_ago = random.randint(0, 24)
    timestamp = now - timedelta(hours=hours_ago)
    
    # Select appropriate message
    if severity == "ERROR":
        message = random.choice(ERROR_MESSAGES)
    elif severity == "WARNING":
        message = random.choice(WARNING_MESSAGES)
    else:
        message = random.choice(INFO_MESSAGES)
    
    # Generate AI summary
    ai_summary = random.choice(AI_SUMMARIES[severity])
    
    return {
        "service": service,
        "severity": severity,
        "raw_log": f"[{timestamp.isoformat()}] {service}: {message}",
        "ai_summary": ai_summary,
        "timestamp": timestamp.isoformat()
    }

def send_log_to_api(log_entry):
    """Send log entry to the API (simulate database insertion)"""
    try:
        # This would normally go to your database
        # For demo purposes, we'll just print it
        print(f"📝 Generated log: {log_entry['service']} - {log_entry['severity']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send log: {e}")
        return False

def generate_demo_data(num_logs=50):
    """Generate demo data"""
    print(f"🎲 Generating {num_logs} demo log entries...")
    
    logs_generated = 0
    for i in range(num_logs):
        log_entry = generate_log_entry()
        
        if send_log_to_api(log_entry):
            logs_generated += 1
        
        # Small delay to simulate real-time log generation
        time.sleep(0.1)
    
    print(f"✅ Generated {logs_generated} log entries")
    return logs_generated

def create_sample_incidents():
    """Create some sample incidents for timeline visualization"""
    print("🚨 Creating sample incidents...")
    
    incidents = []
    
    # Create a few error spikes
    for i in range(3):
        incident_time = datetime.now() - timedelta(hours=random.randint(1, 12))
        service = random.choice(SERVICES)
        
        # Generate multiple error logs for the same service at similar times
        for j in range(random.randint(3, 8)):
            log_entry = generate_log_entry()
            log_entry["service"] = service
            log_entry["severity"] = "ERROR"
            log_entry["timestamp"] = (incident_time + timedelta(minutes=j*5)).isoformat()
            log_entry["ai_summary"] = f"Incident in {service}: Multiple related errors detected"
            
            incidents.append(log_entry)
    
    print(f"✅ Created {len(incidents)} incident logs")
    return incidents

def main():
    """Main function"""
    print("🎭 SmartGuard Demo Data Generator")
    print("=" * 40)
    
    # Generate regular logs
    regular_logs = generate_demo_data(30)
    
    # Generate incident logs
    incident_logs = create_sample_incidents()
    
    # Generate some recent logs
    recent_logs = generate_demo_data(20)
    
    total_logs = regular_logs + len(incident_logs) + recent_logs
    
    print(f"\n🎉 Demo data generation complete!")
    print(f"📊 Total logs generated: {total_logs}")
    print(f"   - Regular logs: {regular_logs}")
    print(f"   - Incident logs: {len(incident_logs)}")
    print(f"   - Recent logs: {recent_logs}")
    
    print(f"\n🚀 You can now start the dashboard with:")
    print(f"   python start_dashboard.py")
    print(f"   or")
    print(f"   streamlit run dashboard.py")

if __name__ == "__main__":
    main()

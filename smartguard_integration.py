# smartguard_integration.py
"""
Integration module to use smartguard.py functionality in the working components.
This bridges the gap between the working api.py/dashboard.py and the smartguard.py monitoring logic.
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import smartguard functionality
try:
    from smartguard import (
        get_db_connection, 
        init_db, 
        store_log, 
        fetch_logs, 
        analyze_logs,
        send_alert
    )
    SMARTGUARD_AVAILABLE = True
    print("✅ SmartGuard monitoring integration available")
except ImportError as e:
    SMARTGUARD_AVAILABLE = False
    print(f"⚠️ SmartGuard monitoring not available: {e}")

class SmartGuardIntegration:
    """Integration class to use SmartGuard monitoring features"""
    
    def __init__(self):
        self.available = SMARTGUARD_AVAILABLE
        if self.available:
            try:
                # Initialize database if needed
                init_db()
                print("✅ SmartGuard database initialized")
            except Exception as e:
                print(f"⚠️ SmartGuard database initialization failed: {e}")
                self.available = False
    
    def get_real_logs(self, hours: int = 1):
        """Get real logs from GCP (if configured)"""
        if not self.available:
            return []
        
        try:
            logs = fetch_logs()
            return logs
        except Exception as e:
            print(f"⚠️ Failed to fetch real logs: {e}")
            return []
    
    def analyze_with_ai(self, logs_data):
        """Analyze logs using SmartGuard AI"""
        if not self.available:
            return "SmartGuard AI analysis not available"
        
        try:
            analysis = analyze_logs(logs_data)
            return analysis
        except Exception as e:
            print(f"⚠️ SmartGuard AI analysis failed: {e}")
            return "AI analysis failed"
    
    def store_log_with_ai(self, timestamp, service, severity, raw_log, ai_summary):
        """Store log with AI analysis"""
        if not self.available:
            return False
        
        try:
            store_log(timestamp, service, severity, raw_log, ai_summary)
            return True
        except Exception as e:
            print(f"⚠️ Failed to store log: {e}")
            return False
    
    def send_alert_if_needed(self, analysis):
        """Send alert if analysis indicates serious issues"""
        if not self.available:
            return False
        
        try:
            if "error" in analysis.lower() or "suspicious" in analysis.lower():
                send_alert(analysis)
                return True
        except Exception as e:
            print(f"⚠️ Failed to send alert: {e}")
        
        return False
    
    def get_enhanced_sample_logs(self, count: int = 100):
        """Get enhanced sample logs with SmartGuard AI analysis"""
        import random
        
        services = [
            "frontend", "cartservice", "productcatalogservice", "recommendationservice",
            "shippingservice", "checkoutservice", "paymentservice", "currencyservice",
            "adservice", "emailservice", "loadgenerator"
        ]
        
        severities = ["ERROR", "WARNING", "INFO"]
        severity_weights = [0.1, 0.2, 0.7]
        
        enhanced_logs = []
        
        for i in range(count):
            service = random.choice(services)
            severity = random.choices(severities, weights=severity_weights)[0]
            timestamp = datetime.now() - timedelta(hours=random.randint(0, 24))
            
            if severity == "ERROR":
                message = f"Error in {service}: Database connection failed"
                ai_summary = f"Critical issue in {service} affecting user experience. Database connectivity problems detected."
            elif severity == "WARNING":
                message = f"Warning in {service}: High memory usage detected"
                ai_summary = f"Performance degradation in {service} requires monitoring. Memory usage above threshold."
            else:
                message = f"Info from {service}: User request processed successfully"
                ai_summary = f"Normal operation in {service}. Request processed without issues."
            
            log_entry = {
                "id": i + 1,
                "service": service,
                "severity": severity,
                "raw_log": f"[{timestamp.isoformat()}] {service}: {message}",
                "ai_summary": ai_summary,
                "timestamp": timestamp.isoformat()
            }
            
            enhanced_logs.append(log_entry)
            
            # Store in database if SmartGuard is available
            if self.available:
                self.store_log_with_ai(
                    timestamp, service, severity, 
                    log_entry["raw_log"], ai_summary
                )
        
        return enhanced_logs

# Global instance
smartguard_integration = SmartGuardIntegration()

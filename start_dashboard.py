#!/usr/bin/env python3
"""
SmartGuard AI Dashboard Startup Script
This script helps you start the SmartGuard dashboard with proper setup.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import requests
        import pandas
        import plotly
        import networkx
        import google.generativeai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not Path(".env").exists():
        print("⚠️ .env file not found - using demo mode")
        print("For full AI features, create a .env file with GEMINI_API_KEY")
        return True  # Allow demo mode
    print("✅ .env file found")
    return True

def start_api():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    try:
        # Start the main API from backend directory
        api_process = subprocess.Popen([
            sys.executable, "api.py"
        ], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for API to start
        time.sleep(5)
        
        # Check if API is running
        try:
            import requests
            response = requests.get("http://localhost:8000/metrics", timeout=10)
            if response.status_code == 200:
                print("✅ FastAPI backend is running on http://localhost:8000")
                print("📊 Using enhanced sample data with SmartGuard integration")
                return api_process
            else:
                print(f"❌ FastAPI backend returned status {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            print("❌ FastAPI backend failed to start - connection refused")
            return None
        except Exception as e:
            print(f"❌ FastAPI backend check failed: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start FastAPI backend: {e}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("🚀 Starting Streamlit dashboard...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], cwd="frontend")
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")

def main():
    """Main startup function"""
    print("🛡️ SmartGuard AI Dashboard Startup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Start API
    api_process = start_api()
    if not api_process:
        sys.exit(1)
    
    try:
        # Start dashboard
        start_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        # Clean up API process
        if api_process:
            print("🛑 Stopping FastAPI backend...")
            api_process.terminate()
            api_process.wait()
            print("✅ FastAPI backend stopped")

if __name__ == "__main__":
    main()

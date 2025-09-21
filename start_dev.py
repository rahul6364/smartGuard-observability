#!/usr/bin/env python3
"""
SmartGuard AI Dashboard - Development Startup Script
Starts both backend and frontend for development
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_dir = Path(__file__).parent / "backend"
    return subprocess.Popen([
        sys.executable, "api.py"
    ], cwd=backend_dir)

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ], cwd=frontend_dir)

def main():
    """Main startup function"""
    print("🛡️ SmartGuard AI Dashboard - Development Mode")
    print("=" * 50)
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Wait for backend to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("\n✅ Both services started!")
        print("🔗 Backend API: http://localhost:8000")
        print("🔗 Frontend Dashboard: http://localhost:8501")
        print("\nPress Ctrl+C to stop both services")
        
        # Wait for processes
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n👋 Shutting down services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Services stopped")
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
RepoPulse Startup Script
Professional Repository Analysis & AI Detection
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Print the RepoPulse banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    🫀 RepoPulse 🫀                          ║
    ║                                                              ║
    ║        Professional Repository Analysis & AI Detection      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import flask_cors
        print("✅ Flask and Flask-CORS are installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")

def start_server():
    """Start the RepoPulse server"""
    print("🚀 Starting RepoPulse server...")
    print("📍 Server will be available at: http://127.0.0.1:5001")
    print("🌐 Web interface: http://127.0.0.1:5001")
    print("📊 API endpoint: http://127.0.0.1:5001/api/analyze")
    print()
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "server.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function"""
    print_banner()
    check_dependencies()
    start_server()

if __name__ == "__main__":
    main() 
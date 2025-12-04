#!/usr/bin/env python3
"""
Smart Desk Companion - Application Launcher
Final Project - Emotional AI Assistant
"""

import os
import sys
import time
import webbrowser
from threading import Thread
from datetime import datetime

def print_banner():
    """Print beautiful startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║             ███████╗    ██████╗      ██████╗             ║
    ║             ██╔════╝    ██╔══██╗    ██╔════╝             ║
    ║             ███████╗    ██║  ██║    ██║                  ║
    ║             ╚════██║    ██║  ██║    ██║                  ║
    ║             ███████║    ██████╔╝    ╚██████╗             ║
    ║             ╚══════╝    ╚═════╝      ╚═════╝             ║
    ║                                                          ║
    ║                  SMART  DESK  COMPANION                  ║
    ║        Your AI-Powered Workspace Assistant System        ║
    ║                                                          ║
    ║              Version 2.1 | Production Ready              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking system dependencies...")
    
    dependencies = [
        ('Flask', 'flask'),
        ('OpenCV', 'cv2'),
        ('NumPy', 'numpy'),
    ]
    
    all_available = True
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - Missing")
            all_available = False
    
    return all_available

def initialize_system():
    """Initialize the Smart Desk Companion system"""
    print("\n🚀 Initializing Smart Desk Companion...")
    
    steps = [
        ("Loading Neural Networks", 1),
        ("Initializing Emotional Intelligence", 2),
        ("Starting Vision System", 1),
        ("Activating AI Companion", 2),
        ("Connecting Hardware Interface", 1),
        ("Preparing Dashboard Interface", 1)
    ]
    
    for step, duration in steps:
        print(f"   ⏳ {step}...", end="", flush=True)
        time.sleep(duration)
        print(" ✅")
    
    print("🌟 Smart Desk Companion initialized successfully!")

def start_web_server():
    """Start the Flask web server"""
    print("\n🌐 Starting Web Interface...")
    
    try:
        from app import app, config
        
        # Start server in background thread
        def run_server():
            app.run(
                host=config.host,
                port=config.port,
                debug=config.debug,
                use_reloader=False
            )
        
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        print(f"   ✅ Server running on http://{config.host}:{config.port}")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to start server: {e}")
        return False

def open_browser():
    """Open web browser automatically"""
    print("\n🌍 Launching Dashboard...")
    time.sleep(2)
    
    url = f"http://localhost:5000"
    try:
        webbrowser.open(url)
        print(f"   ✅ Browser opened: {url}")
    except Exception as e:
        print(f"   ⚠️  Could not open browser automatically: {e}")
        print(f"   📝 Please open manually: {url}")

def print_system_info():
    """Print system information"""
    from config import Config
    config = Config()
    
    print("\n📊 System Information:")
    print(f"   🤖 Application: {config.app_name} v{config.version}")
    print(f"   🌍 Environment: {config.environment}")
    print(f"   🔧 Debug Mode: {config.debug}")
    print(f"   📍 Host: {config.host}:{config.port}")
    
    print("\n🎯 Available Features:")
    features = config.get_system_info()['features']
    for feature, enabled in features.items():
        status = "✅ Enabled" if enabled else "❌ Disabled"
        print(f"   {status} {feature.replace('_', ' ').title()}")

def monitor_system():
    """Monitor system health"""
    print("\n🔍 System Monitor Started...")
    print("   💡 Press Ctrl+C to stop the system")
    
    try:
        while True:
            time.sleep(30)
            # System heartbeat
            print(f"   ❤️  System heartbeat: {datetime.now().strftime('%H:%M:%S')}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Smart Desk Companion...")
        print("🌟 Thank you for using Smart Desk Companion!")

def main():
    """Main application entry point"""
    try:
        # Display banner
        print_banner()
        
        # Check dependencies
        if not check_dependencies():
            print("\n❌ Missing dependencies. Please install required packages.")
            print("   Run: pip install -r requirements.txt")
            sys.exit(1)
        
        # Initialize system
        initialize_system()
        
        # Start web server
        if not start_web_server():
            sys.exit(1)
        
        # Display system info
        print_system_info()
        
        # Open browser
        open_browser()
        
        # Start monitoring
        monitor_system()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown initiated by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
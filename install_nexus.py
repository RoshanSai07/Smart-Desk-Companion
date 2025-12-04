#!/usr/bin/env python3
"""
Nexus AI Installation Script
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Run shell command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    success, output = run_command("pip install -r requirements.txt")
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print(f"❌ Dependency installation failed: {output}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directory structure...")
    
    directories = ['static', 'templates', 'logs', 'models']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created {directory}/")
        else:
            print(f"   ✅ {directory}/ already exists")

def check_camera_access():
    """Check camera accessibility"""
    print("\n📷 Checking camera access...")
    
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            ret, frame = camera.read()
            camera.release()
            if ret and frame is not None:
                print("✅ Camera access confirmed")
                return True
            else:
                print("⚠️  Camera detected but cannot read frames")
                return False
        else:
            print("⚠️  No camera detected or access denied")
            return False
    except Exception as e:
        print(f"⚠️  Camera check failed: {e}")
        return False

def create_env_file():
    """Create environment configuration file"""
    print("\n⚙️  Creating environment configuration...")
    
    env_content = """# Nexus AI Configuration
NEXUS_ENV=development
NEXUS_HOST=0.0.0.0
NEXUS_PORT=5000
NEXUS_DEBUG=True
NEXUS_SECRET_KEY=nexus_ai_quantum_secure_key_2024

# Camera Settings
NEXUS_CAMERA_INDEX=0

# External APIs (Optional)
SPARK_API_KEY=demo_key
SPARK_API_SECRET=demo_secret
SPARK_APP_ID=demo_app_id

# Hardware Settings
PI_HOST=localhost
PI_PORT=5001

# Logging
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Environment file created (.env)")

def main():
    """Main installation routine"""
    print("🚀 Nexus AI Quantum System Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check camera
    check_camera_access()
    
    # Create environment file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Run: python start_nexus.py")
    print("   2. Open http://localhost:5000 in your browser")
    print("   3. Activate camera for emotion analysis")
    print("   4. Connect Pi hardware (optional)")
    print("\n🌟 Enjoy your Smart Desk Companion!")

if __name__ == "__main__":
    main()
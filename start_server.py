#!/usr/bin/env python3
"""
Startup Script for PersonaForge AI
Handles port conflicts, environment validation, and graceful startup.
"""

import os
import sys
import signal
import subprocess
import time
import socket
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        # Find process using the port
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🔄 Killing process {pid} on port {port}")
                    subprocess.run(['kill', '-9', pid], check=False)
            time.sleep(1)  # Give time for port to be released
            return True
    except Exception as e:
        print(f"⚠️  Warning: Could not kill process on port {port}: {e}")
    return False

def check_port_available(port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=8080):
    """Find an available port starting from start_port."""
    port = start_port
    while port < start_port + 100:  # Try up to 100 ports
        if check_port_available(port):
            return port
        port += 1
    return None

def setup_environment():
    """Setup the Python environment."""
    # Check if we're in the virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
        return True
    
    # Check if venv exists
    venv_path = Path("venv")
    if venv_path.exists():
        print("🔄 Activating virtual environment...")
        # Update PATH to use venv Python
        venv_python = venv_path / "bin" / "python"
        if venv_python.exists():
            os.environ['VIRTUAL_ENV'] = str(venv_path.absolute())
            os.environ['PATH'] = f"{venv_path / 'bin'}:{os.environ.get('PATH', '')}"
            return True
        else:
            print("❌ Virtual environment Python not found")
            return False
    else:
        print("❌ Virtual environment not found. Please run setup first.")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting PersonaForge AI...")
    
    # Setup environment
    if not setup_environment():
        print("❌ Failed to setup environment")
        return 1
    
    # Kill any existing processes on port 8080
    if kill_process_on_port(8080):
        print("✅ Cleared port 8080")
    
    # Find available port
    port = find_available_port(8080)
    if not port:
        print("❌ No available ports found")
        return 1
    
    print(f"🌐 Starting server on port {port}")
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY', 'your-groq-api-key-here'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here'),
        'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID', ''),
        'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET', ''),
        'REDDIT_USER_AGENT': os.getenv('REDDIT_USER_AGENT', 'PersonaAI/1.0')
    })
    
    # Use the virtual environment Python
    venv_python = Path("venv") / "bin" / "python"
    if not venv_python.exists():
        print("❌ Virtual environment Python not found")
        return 1
    
    try:
        # Start the server
        cmd = [
            str(venv_python),
            "-c",
            "from web_dashboard import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8080)"
        ]
        
        print(f"🎯 Running: {' '.join(cmd)}")
        print(f"🌐 Server will be available at: http://localhost:{port}")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Run the server
        process = subprocess.Popen(cmd, env=env)
        
        # Wait for the process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped")
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
import subprocess
import os
import sys
import time
import threading

def install_frontend_deps():
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    node_modules = os.path.join(frontend_dir, 'node_modules')
    
    if not os.path.exists(node_modules):
        print("Installing frontend dependencies (this may take a while)...")
        # Use npm.cmd for Windows
        subprocess.check_call("npm.cmd install", cwd=frontend_dir, shell=True)
        print("Frontend dependencies installed.")
    else:
        print("Frontend dependencies already installed.")

def run_backend():
    print("Starting Backend...")
    backend_dir = os.path.join(os.getcwd(), 'backend')
    env = os.environ.copy()
    # Force SQLite for local run
    env['DATABASE_URL'] = 'sqlite:///instance/comic_editor.db'
    env['FLASK_ENV'] = 'development'
    
    # Use the python from the virtual environment if available, else system python
    python_exe = sys.executable
    
    # Check if .venv exists in root
    venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        python_exe = venv_python
    
    cmd = [python_exe, 'run.py']
    
    try:
        process = subprocess.Popen(
            cmd, 
            cwd=backend_dir, 
            env=env,
            shell=True
        )
        return process
    except Exception as e:
        print(f"Failed to start backend: {e}")
        return None

def run_frontend():
    print("Starting Frontend...")
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    
    # npm start
    cmd = "npm.cmd start"
    
    try:
        process = subprocess.Popen(
            cmd, 
            cwd=frontend_dir, 
            shell=True
        )
        return process
    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return None

def main():
    print("=======================================")
    print("      ComicGenerator Local Runner      ")
    print("=======================================")
    
    # 1. Install frontend deps
    try:
        install_frontend_deps()
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return

    # 2. Start Backend
    backend_proc = run_backend()
    if not backend_proc:
        return
        
    # Give backend a moment to start
    time.sleep(5)
    
    # 3. Start Frontend
    frontend_proc = run_frontend()
    if not frontend_proc:
        backend_proc.terminate()
        return
        
    print("\n✅ Services started!")
    print("Backend: http://localhost:5000")
    print("Frontend: http://localhost:3000 (Opening soon...)")
    print("\nPress Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Stopped.")

if __name__ == "__main__":
    main()

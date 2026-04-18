"""
Stock Price Prediction System — Launch Script
Starts both the Flask backend and Streamlit frontend.
"""
import subprocess
import sys
import os
import time
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("=" * 60)
    print("  Stock Price Prediction System")
    print("=" * 60)
    print()

    # Ensure data/models directory exists
    os.makedirs(os.path.join(ROOT_DIR, "data", "models"), exist_ok=True)

    # Start Flask backend
    print("Starting Flask backend on http://localhost:5000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT_DIR, "backend", "app.py")],
        cwd=ROOT_DIR,
    )
    time.sleep(2)

    # Start Streamlit frontend
    print("Starting Streamlit frontend on http://localhost:8501 ...")
    frontend_proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            os.path.join(ROOT_DIR, "frontend", "app.py"),
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=ROOT_DIR,
    )

    print()
    print("Both servers are running!")
    print("   Frontend:  http://localhost:8501")
    print("   Backend:   http://localhost:5000")
    print()
    print("   Press Ctrl+C to stop both servers.")
    print()

    try:
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("All servers stopped.")


if __name__ == "__main__":
    main()

"""
Serverless function entrypoint for Vercel.
Exports the Flask application instance as `app`.
"""
import os
import sys

# Ensure project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

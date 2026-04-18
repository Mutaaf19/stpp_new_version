"""
Stock Price Prediction System — Flask Backend Application
Entry point for the REST API server.
"""
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from backend.routes.stock_routes import api


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api)
    
    @app.route("/")
    def health():
        return {"status": "ok", "service": "Stock Price Prediction System API"}
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000, host="0.0.0.0", threaded=True)

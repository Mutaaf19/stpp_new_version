"""
Serverless function entrypoint for Vercel.
Uses lazy imports inside each route to prevent module-level crashes.
"""
import os
import sys

# Ensure project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "Stock Price Prediction API", "version": "1.0"})


@app.route("/api/validate-ticker")
def api_validate_ticker():
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"valid": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.stock_service import validate_ticker
        return jsonify(validate_ticker(ticker))
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500


@app.route("/api/stock-data")
def api_stock_data():
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.stock_service import fetch_stock_data
        result = fetch_stock_data(ticker, period)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/indicators")
def api_indicators():
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    rsi_period = int(request.args.get("rsi_period", 14))
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.stock_service import fetch_stock_data
        from backend.services.indicator_service import calculate_all_indicators
        stock_data = fetch_stock_data(ticker, period)
        if not stock_data["success"]:
            return jsonify(stock_data), 404
        indicators = calculate_all_indicators(
            close_prices=stock_data["data"]["close"],
            dates=stock_data["data"]["dates"],
            rsi_period=rsi_period,
        )
        return jsonify({"success": True, "ticker": ticker, **indicators})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/predict")
def api_predict():
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    return jsonify({
        "success": False,
        "error": "LSTM prediction is not available on this deployment (TensorFlow not installed). "
                 "Run the app locally for full ML predictions."
    }), 503


@app.route("/api/recommend")
def api_recommend():
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.stock_service import fetch_stock_data
        from backend.services.indicator_service import calculate_all_indicators
        from backend.services.recommendation_service import generate_recommendation
        from backend.services.stock_service import fetch_fundamentals_news

        stock_data = fetch_stock_data(ticker, period)
        if not stock_data["success"]:
            return jsonify(stock_data), 404

        rsi_overbought = int(request.args.get("rsi_overbought", 70))
        rsi_oversold = int(request.args.get("rsi_oversold", 30))
        rsi_period = int(request.args.get("rsi_period", 14))

        indicators = calculate_all_indicators(
            close_prices=stock_data["data"]["close"],
            dates=stock_data["data"]["dates"],
            rsi_period=rsi_period,
        )
        news_result = fetch_fundamentals_news(ticker)
        sentiment_score = news_result.get("sentiment", {}).get("score", 0.0) if news_result.get("success") else 0.0

        recommendation = generate_recommendation(
            close_prices=stock_data["data"]["close"],
            ma20=indicators["indicators"]["MA20"],
            ma50=indicators["indicators"]["MA50"],
            rsi_values=indicators["indicators"]["RSI"],
            predicted_trend_pct=0,  # No ML on Vercel
            rsi_overbought=rsi_overbought,
            rsi_oversold=rsi_oversold,
            sentiment_score=sentiment_score,
        )
        return jsonify({"success": True, "ticker": ticker, **recommendation})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/fundamentals")
def api_fundamentals():
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.stock_service import fetch_fundamentals_news
        result = fetch_fundamentals_news(ticker)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ratios")
def api_ratios():
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.screener_service import fetch_financial_ratios
        result = fetch_financial_ratios(ticker)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/peers")
def api_peers():
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.screener_service import fetch_peer_comparison
        result = fetch_peer_comparison(ticker)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/financials-history")
def api_financials_history():
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.screener_service import fetch_historical_financials
        result = fetch_historical_financials(ticker)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

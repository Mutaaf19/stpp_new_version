"""
Stock Price Prediction System — API Routes
All REST API endpoints for stock data, indicators, predictions, and recommendations.
"""
from flask import Blueprint, request, jsonify
from backend.services.stock_service import fetch_stock_data, validate_ticker
from backend.services.indicator_service import calculate_all_indicators
from backend.services.prediction_service import predict_prices
from backend.services.recommendation_service import generate_recommendation


api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/validate-ticker", methods=["GET"])
def api_validate_ticker():
    """Validate if a stock ticker exists."""
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"valid": False, "error": "Ticker is required"}), 400
    
    result = validate_ticker(ticker)
    return jsonify(result)


@api.route("/stock-data", methods=["GET"])
def api_stock_data():
    """Fetch historical stock data."""
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    
    result = fetch_stock_data(ticker, period)
    if not result["success"]:
        return jsonify(result), 404
    
    return jsonify(result)


@api.route("/indicators", methods=["GET"])
def api_indicators():
    """Calculate technical indicators for a stock."""
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    
    try:
        rsi_period = int(request.args.get("rsi_period", 14))
    except ValueError:
        rsi_period = 14
        
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    
    # First fetch the data
    stock_data = fetch_stock_data(ticker, period)
    if not stock_data["success"]:
        return jsonify(stock_data), 404
    
    # Calculate indicators
    indicators = calculate_all_indicators(
        close_prices=stock_data["data"]["close"],
        dates=stock_data["data"]["dates"],
        rsi_period=rsi_period,
    )
    
    return jsonify({"success": True, "ticker": ticker, **indicators})


@api.route("/predict", methods=["GET"])
def api_predict():
    """Predict future stock prices using LSTM."""
    ticker = request.args.get("ticker", "").strip()
    days = request.args.get("days", "30")
    
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    
    try:
        days = int(days)
        days = max(7, min(days, 90))  # Clamp between 7-90 days
    except ValueError:
        days = 30
    
    result = predict_prices(ticker, days)
    return jsonify(result)


@api.route("/recommend", methods=["GET"])
def api_recommend():
    """Generate BUY/SELL/HOLD recommendation."""
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    
    # Fetch stock data
    stock_data = fetch_stock_data(ticker, period)
    if not stock_data["success"]:
        return jsonify(stock_data), 404
    
    # Get custom RSI thresholds
    try:
        rsi_overbought = int(request.args.get("rsi_overbought", 70))
        rsi_oversold = int(request.args.get("rsi_oversold", 30))
        rsi_period = int(request.args.get("rsi_period", 14))
    except ValueError:
        rsi_overbought = 70
        rsi_oversold = 30
        rsi_period = 14
        
    # Calculate indicators
    indicators = calculate_all_indicators(
        close_prices=stock_data["data"]["close"],
        dates=stock_data["data"]["dates"],
        rsi_period=rsi_period,
    )
    
    # Get prediction for trend
    prediction = predict_prices(ticker, days=30)
    trend_pct = 0
    if prediction["success"]:
        trend_pct = prediction["trend"]["change_pct"]
        
    # Get sentiment score
    from backend.services.stock_service import fetch_fundamentals_news
    news_result = fetch_fundamentals_news(ticker)
    sentiment_score = 0.0
    if news_result.get("success"):
        sentiment_score = news_result.get("sentiment", {}).get("score", 0.0)
    
    # Generate recommendation
    recommendation = generate_recommendation(
        close_prices=stock_data["data"]["close"],
        ma20=indicators["indicators"]["MA20"],
        ma50=indicators["indicators"]["MA50"],
        rsi_values=indicators["indicators"]["RSI"],
        predicted_trend_pct=trend_pct,
        rsi_overbought=rsi_overbought,
        rsi_oversold=rsi_oversold,
        sentiment_score=sentiment_score,
    )
    
    return jsonify({
        "success": True,
        "ticker": ticker,
        **recommendation,
    })

@api.route("/fundamentals", methods=["GET"])
def api_fundamentals():
    """Fetch company fundamentals and news sentiment."""
    from backend.services.stock_service import fetch_fundamentals_news
    
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
        
    result = fetch_fundamentals_news(ticker)
    if not result["success"]:
        return jsonify(result), 404
    
    return jsonify(result)

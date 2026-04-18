"""
Stock Price Prediction System — Recommendation Service
Generates BUY / SELL / HOLD recommendations based on
technical indicators and ML predictions.
"""


def generate_recommendation(
    close_prices: list,
    ma20: list,
    ma50: list,
    rsi_values: list,
    predicted_trend_pct: float,
    rsi_overbought: int = 70,
    rsi_oversold: int = 30,
    sentiment_score: float = 0.0,
) -> dict:
    """
    Generate a BUY / SELL / HOLD recommendation.
    
    Scoring system (total = sum of signals):
        MA Crossover:
            +2  if MA20 > MA50 (bullish crossover)
            -2  if MA20 < MA50 (bearish crossover)
        
        RSI Signal:
            +2  if RSI < 30 (oversold — buy opportunity)
            -2  if RSI > 70 (overbought — sell signal)
            +1  if 30 <= RSI < 40
            -1  if 60 < RSI <= 70
             0  otherwise (neutral)
        
        ML Trend:
            +3  if predicted change > 5% (strong bullish)
            +2  if predicted change > 2%
            +1  if predicted change > 0%
            -1  if predicted change < 0%
            -2  if predicted change < -2%
            -3  if predicted change < -5% (strong bearish)

        News Sentiment (Time-Decayed):
            +2  if sentiment > 0.2 (Strong Positive)
            +1  if sentiment > 0.05 (Slightly Positive)
            -1  if sentiment < -0.05 (Slightly Negative)
            -2  if sentiment < -0.2 (Strong Negative)
    
    Final decision:
        score >= 3 → BUY
        score <= -3 → SELL
        otherwise → HOLD
    """
    score = 0
    signals = []
    
    # === MA Crossover Signal ===
    # Use the latest valid values
    latest_ma20 = _get_latest_valid(ma20)
    latest_ma50 = _get_latest_valid(ma50)
    
    if latest_ma20 is not None and latest_ma50 is not None:
        if latest_ma20 > latest_ma50:
            score += 2
            signals.append({
                "indicator": "Moving Average Crossover",
                "signal": "BULLISH",
                "detail": f"MA20 ({latest_ma20:.2f}) is above MA50 ({latest_ma50:.2f}), indicating upward momentum.",
            })
        else:
            score -= 2
            signals.append({
                "indicator": "Moving Average Crossover",
                "signal": "BEARISH",
                "detail": f"MA20 ({latest_ma20:.2f}) is below MA50 ({latest_ma50:.2f}), indicating downward pressure.",
            })
    
    # === RSI Signal ===
    latest_rsi = _get_latest_valid(rsi_values)
    
    if latest_rsi is not None:
        if latest_rsi < rsi_oversold:
            score += 2
            signals.append({
                "indicator": "RSI",
                "signal": "OVERSOLD",
                "detail": f"RSI is {latest_rsi:.1f} (below {rsi_oversold}). The stock may be oversold — potential buy opportunity.",
            })
        elif latest_rsi < (rsi_oversold + 10):
            score += 1
            signals.append({
                "indicator": "RSI",
                "signal": "SLIGHTLY OVERSOLD",
                "detail": f"RSI is {latest_rsi:.1f}. Approaching oversold territory.",
            })
        elif latest_rsi > rsi_overbought:
            score -= 2
            signals.append({
                "indicator": "RSI",
                "signal": "OVERBOUGHT",
                "detail": f"RSI is {latest_rsi:.1f} (above {rsi_overbought}). The stock may be overbought — potential sell signal.",
            })
        elif latest_rsi > (rsi_overbought - 10):
            score -= 1
            signals.append({
                "indicator": "RSI",
                "signal": "SLIGHTLY OVERBOUGHT",
                "detail": f"RSI is {latest_rsi:.1f}. Approaching overbought territory.",
            })
        else:
            signals.append({
                "indicator": "RSI",
                "signal": "NEUTRAL",
                "detail": f"RSI is {latest_rsi:.1f}. In the neutral zone ({rsi_oversold}-{rsi_overbought}).",
            })
    
    # === ML Trend Signal ===
    if predicted_trend_pct > 5:
        score += 3
        signals.append({
            "indicator": "ML Prediction",
            "signal": "STRONG BULLISH",
            "detail": f"Model predicts a {predicted_trend_pct:.1f}% increase over the next 30 days.",
        })
    elif predicted_trend_pct > 2:
        score += 2
        signals.append({
            "indicator": "ML Prediction",
            "signal": "BULLISH",
            "detail": f"Model predicts a {predicted_trend_pct:.1f}% increase over the next 30 days.",
        })
    elif predicted_trend_pct > 0:
        score += 1
        signals.append({
            "indicator": "ML Prediction",
            "signal": "SLIGHTLY BULLISH",
            "detail": f"Model predicts a slight {predicted_trend_pct:.1f}% increase over the next 30 days.",
        })
    elif predicted_trend_pct > -2:
        score -= 1
        signals.append({
            "indicator": "ML Prediction",
            "signal": "SLIGHTLY BEARISH",
            "detail": f"Model predicts a slight {predicted_trend_pct:.1f}% decrease over the next 30 days.",
        })
    elif predicted_trend_pct > -5:
        score -= 2
        signals.append({
            "indicator": "ML Prediction",
            "signal": "BEARISH",
            "detail": f"Model predicts a {predicted_trend_pct:.1f}% decrease over the next 30 days.",
        })
    else:
        score -= 3
        signals.append({
            "indicator": "ML Prediction",
            "signal": "STRONG BEARISH",
            "detail": f"Model predicts a significant {predicted_trend_pct:.1f}% decrease over the next 30 days.",
        })
        
    # === News Sentiment Signal ===
    if sentiment_score > 0.2:
        score += 2
        signals.append({
            "indicator": "News Sentiment",
            "signal": "STRONG POSITIVE",
            "detail": f"Recent news shows highly positive sentiment (Score: {sentiment_score:.2f}).",
        })
    elif sentiment_score > 0.05:
        score += 1
        signals.append({
            "indicator": "News Sentiment",
            "signal": "SLIGHTLY POSITIVE",
            "detail": f"Recent news shows somewhat positive sentiment (Score: {sentiment_score:.2f}).",
        })
    elif sentiment_score < -0.2:
        score -= 2
        signals.append({
            "indicator": "News Sentiment",
            "signal": "STRONG NEGATIVE",
            "detail": f"Recent news shows highly negative sentiment (Score: {sentiment_score:.2f}).",
        })
    elif sentiment_score < -0.05:
        score -= 1
        signals.append({
            "indicator": "News Sentiment",
            "signal": "SLIGHTLY NEGATIVE",
            "detail": f"Recent news shows somewhat negative sentiment (Score: {sentiment_score:.2f}).",
        })
    else:
        signals.append({
            "indicator": "News Sentiment",
            "signal": "NEUTRAL",
            "detail": f"Recent news is mostly neutral or too old to heavily impact prices (Score: {sentiment_score:.2f}).",
        })
    
    # === Final Recommendation ===
    # Adjusted max score logic from 7 to 9 because we added sentiment max score (+2)
    max_possible_abs_score = 9 
    
    if score >= 3:
        recommendation = "BUY"
        confidence = min(abs(score) / max_possible_abs_score * 100, 95)
        summary = "Indicators, ML prediction, and news sentiment suggest a favorable buying opportunity."
    elif score <= -3:
        recommendation = "SELL"
        confidence = min(abs(score) / max_possible_abs_score * 100, 95)
        summary = "Indicators, ML prediction, and news sentiment suggest considering selling or avoiding this stock."
    else:
        recommendation = "HOLD"
        confidence = max(30, 70 - (abs(score) / max_possible_abs_score * 100) * 0.4)
        summary = "Mixed signals from technical indicators, prediction, and news sentiment. Consider holding."
    
    return {
        "recommendation": recommendation,
        "score": score,
        "confidence": round(confidence, 1),
        "summary": summary,
        "signals": signals,
    }


def _get_latest_valid(values: list):
    """Get the latest non-None value from a list."""
    if not values:
        return None
    for v in reversed(values):
        if v is not None:
            return v
    return None

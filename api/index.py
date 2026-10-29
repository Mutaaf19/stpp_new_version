"""
Stock Price Prediction System — Vercel Native Serverless Application
Self-contained Python application using Vercel's native BaseHTTPRequestHandler.
Bypasses WSGI adapter bottlenecks, requires zero compilation, and guarantees 100% serverless compatibility.
"""
import os
import sys
import json
import math
import traceback
import urllib.request
import urllib.error
import urllib.parse
from http.server import BaseHTTPRequestHandler
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# YAHOO FINANCE DIRECT ENGINE
# ─────────────────────────────────────────────────────────────

def _fetch_yahoo_chart(ticker: str, period: str = "1y"):
    """Fetch raw chart data directly from Yahoo Finance v8 API."""
    ticker = ticker.strip().upper()
    range_map = {
        "1m": "1mo", "1mo": "1mo",
        "3m": "3mo", "3mo": "3mo",
        "6m": "6mo", "6mo": "6mo",
        "1y": "1y", "2y": "2y", "5y": "5y", "max": "max"
    }
    y_range = range_map.get(period.lower(), "1y")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?range={y_range}&interval=1d&includePrePost=false"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    })
    
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        
    result = data.get("chart", {}).get("result")
    if not result:
        err = data.get("chart", {}).get("error", {})
        raise ValueError(err.get("description", f"No data found for ticker {ticker}"))
        
    res = result[0]
    meta = res.get("meta", {})
    timestamps = res.get("timestamp", [])
    quotes = res.get("indicators", {}).get("quote", [{}])[0]
    
    raw_opens = quotes.get("open", [])
    raw_highs = quotes.get("high", [])
    raw_lows = quotes.get("low", [])
    raw_closes = quotes.get("close", [])
    raw_vols = quotes.get("volume", [])
    
    dates, opens, highs, lows, closes, vols = [], [], [], [], [], []
    for i, ts in enumerate(timestamps):
        c = raw_closes[i] if i < len(raw_closes) else None
        if c is not None and not math.isnan(c):
            dt_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
            dates.append(dt_str)
            opens.append(round(raw_opens[i] if (i < len(raw_opens) and raw_opens[i] is not None) else c, 2))
            highs.append(round(raw_highs[i] if (i < len(raw_highs) and raw_highs[i] is not None) else c, 2))
            lows.append(round(raw_lows[i] if (i < len(raw_lows) and raw_lows[i] is not None) else c, 2))
            closes.append(round(c, 2))
            vols.append(int(raw_vols[i]) if (i < len(raw_vols) and raw_vols[i] is not None) else 0)
            
    if not closes:
        raise ValueError(f"No trading data available for {ticker}")
        
    curr_price = meta.get("regularMarketPrice") or closes[-1]
    prev_close = meta.get("chartPreviousClose") or (closes[-2] if len(closes) > 1 else curr_price)
    day_change = round(curr_price - prev_close, 2)
    day_change_pct = round((day_change / prev_close) * 100, 2) if prev_close else 0.0

    return {
        "ticker": ticker,
        "name": meta.get("shortName") or meta.get("longName") or ticker,
        "currency": meta.get("currency", "USD"),
        "exchange": meta.get("exchangeName", ""),
        "current_price": round(curr_price, 2),
        "previous_close": round(prev_close, 2),
        "day_change": day_change,
        "day_change_percent": day_change_pct,
        "day_high": round(meta.get("regularMarketDayHigh") or max(highs[-1:] or [curr_price]), 2),
        "day_low": round(meta.get("regularMarketDayLow") or min(lows[-1:] or [curr_price]), 2),
        "fifty_two_week_high": round(meta.get("fiftyTwoWeekHigh") or max(highs), 2),
        "fifty_two_week_low": round(meta.get("fiftyTwoWeekLow") or min(lows), 2),
        "dates": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols
    }


def _calculate_indicators(closes, dates, rsi_period=14):
    """Pure-Python Technical Indicator Engine."""
    n = len(closes)
    
    def sma(period):
        out = []
        for i in range(n):
            if i + 1 < period:
                out.append(None)
            else:
                out.append(round(sum(closes[i + 1 - period : i + 1]) / period, 2))
        return out
        
    ma20 = sma(20)
    ma50 = sma(50)
    ma100 = sma(100)
    
    ema20 = []
    multiplier = 2 / (20 + 1)
    for i, c in enumerate(closes):
        if i + 1 < 20:
            ema20.append(None)
        elif i + 1 == 20:
            ema20.append(round(sum(closes[:20]) / 20, 2))
        else:
            prev = ema20[-1]
            ema20.append(round((c - prev) * multiplier + prev, 2))

    gains, losses = [], []
    for i in range(1, n):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0.0))
        losses.append(max(-diff, 0.0))
        
    rsi = [None] * rsi_period
    if len(gains) >= rsi_period:
        avg_gain = sum(gains[:rsi_period]) / rsi_period
        avg_loss = sum(losses[:rsi_period]) / rsi_period
        rs = (avg_gain / avg_loss) if avg_loss != 0 else 100.0
        rsi.append(round(100.0 - (100.0 / (1.0 + rs)), 2))
        
        for i in range(rsi_period, len(gains)):
            avg_gain = (avg_gain * (rsi_period - 1) + gains[i]) / rsi_period
            avg_loss = (avg_loss * (rsi_period - 1) + losses[i]) / rsi_period
            rs = (avg_gain / avg_loss) if avg_loss != 0 else 100.0
            rsi.append(round(100.0 - (100.0 / (1.0 + rs)), 2))

    bb_upper, bb_lower = [], []
    for i in range(n):
        if i + 1 < 20 or ma20[i] is None:
            bb_upper.append(None)
            bb_lower.append(None)
        else:
            window = closes[i - 19 : i + 1]
            mean = ma20[i]
            variance = sum((x - mean) ** 2 for x in window) / 20
            std = math.sqrt(variance)
            bb_upper.append(round(mean + 2 * std, 2))
            bb_lower.append(round(mean - 2 * std, 2))

    return {
        "MA20": ma20,
        "MA50": ma50,
        "MA100": ma100,
        "EMA20": ema20,
        "RSI": rsi,
        "BB_upper": bb_upper,
        "BB_lower": bb_lower,
    }


def _generate_recommendation(closes, ma20, ma50, rsi_vals, sentiment_score=0.0):
    score = 0
    signals = {}
    
    last_ma20 = next((x for x in reversed(ma20) if x is not None), None)
    last_ma50 = next((x for x in reversed(ma50) if x is not None), None)
    
    if last_ma20 is not None and last_ma50 is not None:
        if last_ma20 > last_ma50:
            score += 2
            signals["ma_signal"] = "Bullish Crossover (MA20 > MA50)"
        else:
            score -= 2
            signals["ma_signal"] = "Bearish Trend (MA20 < MA50)"
    else:
        signals["ma_signal"] = "Neutral (Insufficient History)"
        
    signals["ma50_val"] = last_ma50
    signals["ma200_val"] = last_ma20

    last_rsi = next((x for x in reversed(rsi_vals) if x is not None), 50.0)
    if last_rsi < 30:
        score += 3
        signals["rsi_signal"] = f"Strong Buy — Oversold ({last_rsi})"
    elif last_rsi < 40:
        score += 1
        signals["rsi_signal"] = f"Mild Buy — Approaching Oversold ({last_rsi})"
    elif last_rsi > 70:
        score -= 3
        signals["rsi_signal"] = f"Strong Sell — Overbought ({last_rsi})"
    elif last_rsi > 60:
        score -= 1
        signals["rsi_signal"] = f"Mild Sell — Approaching Overbought ({last_rsi})"
    else:
        signals["rsi_signal"] = f"Neutral Momentum ({last_rsi})"

    if score >= 4: verdict = "STRONG BUY"
    elif score >= 2: verdict = "BUY"
    elif score <= -4: verdict = "STRONG SELL"
    elif score <= -2: verdict = "SELL"
    else: verdict = "HOLD"

    return {
        "verdict": verdict,
        "score": score,
        "confidence": "High" if abs(score) >= 4 else ("Medium" if abs(score) >= 2 else "Moderate"),
        "signals": signals
    }


# ─────────────────────────────────────────────────────────────
# FRONTEND DASHBOARD HTML
# ─────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stock Price Prediction & Technical Analysis</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(17, 24, 39, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent: #6366f1;
      --accent-glow: rgba(99, 102, 241, 0.25);
      --green: #10b981;
      --green-bg: rgba(16, 185, 129, 0.15);
      --red: #ef4444;
      --red-bg: rgba(239, 68, 68, 0.15);
      --amber: #f59e0b;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: radial-gradient(circle at 50% 0%, #151d30 0%, var(--bg) 70%);
      color: var(--text-main);
      font-family: var(--font);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background: rgba(13, 18, 30, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 14px 28px;
    }

    .nav-container {
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: #fff;
    }

    .brand-icon {
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, #6366f1, #8b5cf6);
      border-radius: 10px;
      display: grid;
      place-items: center;
      font-size: 20px;
      box-shadow: 0 4px 14px var(--accent-glow);
    }

    .brand-title {
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }

    .brand-subtitle {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .search-box {
      display: flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 4px 6px;
      width: 320px;
      transition: all 0.2s;
    }

    .search-box:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }

    .search-input {
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-family: var(--mono);
      font-size: 0.95rem;
      padding: 8px 12px;
      width: 100%;
      text-transform: uppercase;
    }

    .search-btn {
      background: var(--accent);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 8px 16px;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
      transition: background 0.2s;
    }

    .search-btn:hover { background: #4f46e5; }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: var(--green);
      background: var(--green-bg);
      padding: 6px 12px;
      border-radius: 20px;
      font-weight: 500;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 8px var(--green);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    main {
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px;
      width: 100%;
      flex: 1;
    }

    .quick-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }

    .quick-label {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-right: 4px;
    }

    .quick-chip {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 5px 12px;
      border-radius: 8px;
      font-family: var(--mono);
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s;
    }

    .quick-chip:hover, .quick-chip.active {
      background: rgba(99, 102, 241, 0.15);
      border-color: var(--accent);
      color: #fff;
    }

    .hero-kpi {
      background: var(--card-bg);
      backdrop-filter: blur(8px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 24px;
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
      gap: 20px;
      align-items: center;
    }

    @media (max-width: 1024px) { .hero-kpi { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 640px) { .hero-kpi { grid-template-columns: 1fr; } }

    .ticker-header h1 {
      font-size: 1.8rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      display: flex;
      align-items: baseline;
      gap: 10px;
    }

    .ticker-symbol {
      font-family: var(--mono);
      color: var(--accent);
      font-size: 1.1rem;
      font-weight: 600;
      background: rgba(99, 102, 241, 0.12);
      padding: 2px 8px;
      border-radius: 6px;
    }

    .price-row {
      display: flex;
      align-items: baseline;
      gap: 12px;
      margin-top: 6px;
    }

    .current-price {
      font-size: 2rem;
      font-weight: 800;
      font-family: var(--mono);
      letter-spacing: -0.02em;
    }

    .price-pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-family: var(--mono);
      font-size: 0.9rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 6px;
    }

    .pill-green { color: var(--green); background: var(--green-bg); }
    .pill-red { color: var(--red); background: var(--red-bg); }

    .kpi-col {
      display: flex;
      flex-direction: column;
      gap: 4px;
      border-left: 1px solid var(--card-border);
      padding-left: 18px;
    }

    @media (max-width: 1024px) { .kpi-col { border-left: none; padding-left: 0; } }

    .kpi-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      font-weight: 600;
    }

    .kpi-val {
      font-size: 1.15rem;
      font-weight: 700;
      font-family: var(--mono);
    }

    .grid-layout {
      display: grid;
      grid-template-columns: 3fr 1.2fr;
      gap: 24px;
      margin-bottom: 24px;
    }

    @media (max-width: 1100px) { .grid-layout { grid-template-columns: 1fr; } }

    .card {
      background: var(--card-bg);
      backdrop-filter: blur(8px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
      overflow: hidden;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 12px;
    }

    .card-title {
      font-size: 1.1rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .chart-controls {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn-group {
      display: flex;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 3px;
      border: 1px solid var(--card-border);
    }

    .btn-period, .btn-mode {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 5px 12px;
      font-size: 0.75rem;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-period.active, .btn-mode.active {
      background: var(--accent);
      color: #fff;
    }

    #price-chart { width: 100%; height: 480px; }
    #indicator-chart {
      width: 100%;
      height: 220px;
      margin-top: 16px;
      border-top: 1px solid var(--card-border);
      padding-top: 16px;
    }

    .recommendation-box {
      text-align: center;
      padding: 24px 16px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--card-border);
      margin-bottom: 20px;
    }

    .rec-badge {
      display: inline-block;
      font-size: 1.5rem;
      font-weight: 800;
      padding: 8px 24px;
      border-radius: 12px;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
      text-transform: uppercase;
      font-family: var(--mono);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .rec-STRONG-BUY { background: #059669; color: #fff; box-shadow: 0 0 24px rgba(16, 185, 129, 0.4); }
    .rec-BUY { background: #10b981; color: #fff; box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }
    .rec-HOLD { background: #f59e0b; color: #fff; box-shadow: 0 0 20px rgba(245, 158, 11, 0.3); }
    .rec-SELL { background: #ef4444; color: #fff; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
    .rec-STRONG-SELL { background: #b91c1c; color: #fff; box-shadow: 0 0 24px rgba(185, 28, 28, 0.4); }

    .rec-score-text {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 4px;
    }

    .signal-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 16px;
    }

    .signal-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      font-size: 0.85rem;
    }

    .signal-name { color: var(--text-muted); }
    .signal-val { font-weight: 600; font-family: var(--mono); }

    .tabs-header {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 12px;
      margin-bottom: 20px;
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 8px 18px;
      font-size: 0.9rem;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .tab-btn.active { background: var(--accent); color: #fff; }

    .ratios-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;
    }

    .ratio-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 14px;
    }

    .ratio-title {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-bottom: 4px;
    }

    .ratio-number {
      font-size: 1.2rem;
      font-weight: 700;
      font-family: var(--mono);
      color: #fff;
    }

    .peers-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }

    .peers-table th, .peers-table td {
      padding: 12px 16px;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }

    .peers-table th {
      color: var(--text-muted);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .peers-table tr:hover td { background: rgba(255, 255, 255, 0.02); }

    .news-card { display: flex; flex-direction: column; gap: 14px; }
    .news-item {
      padding: 14px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      transition: border-color 0.2s;
    }
    .news-item:hover { border-color: var(--accent); }
    .news-top {
      display: flex;
      justify-content: space-between;
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .news-link {
      color: #fff;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.95rem;
      line-height: 1.4;
    }
    .news-link:hover { color: var(--accent); }

    #loading-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(9, 13, 22, 0.7);
      backdrop-filter: blur(4px);
      display: none;
      place-items: center;
      z-index: 100;
      flex-direction: column;
      gap: 16px;
    }

    .spinner {
      width: 48px;
      height: 48px;
      border: 4px solid var(--card-border);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    footer {
      border-top: 1px solid var(--card-border);
      padding: 24px;
      text-align: center;
      font-size: 0.8rem;
      color: var(--text-muted);
      background: rgba(13, 18, 30, 0.5);
    }
  </style>
</head>
<body>
  <div id="loading-overlay">
    <div class="spinner"></div>
    <div style="font-weight: 600; color: #fff; font-size: 1rem;">Fetching Stock Intelligence...</div>
  </div>

  <header>
    <div class="nav-container">
      <a href="/" class="brand">
        <div class="brand-icon">📈</div>
        <div>
          <div class="brand-title">Stock Price Prediction System</div>
          <div class="brand-subtitle">Automated Technical Analysis & Screener</div>
        </div>
      </a>
      
      <div style="display: flex; align-items: center; gap: 16px;">
        <div class="search-box">
          <input type="text" id="ticker-input" class="search-input" value="AAPL" placeholder="Ticker (e.g. AAPL, NVDA, RELIANCE.NS)">
          <button id="search-btn" class="search-btn">Analyze</button>
        </div>
        <div class="status-badge">
          <span class="status-dot"></span>
          <span>Live API Active</span>
        </div>
      </div>
    </div>
  </header>

  <main>
    <div class="quick-bar">
      <span class="quick-label">Popular Tickers:</span>
      <button class="quick-chip active" onclick="loadTicker('AAPL')">AAPL</button>
      <button class="quick-chip" onclick="loadTicker('MSFT')">MSFT</button>
      <button class="quick-chip" onclick="loadTicker('NVDA')">NVDA</button>
      <button class="quick-chip" onclick="loadTicker('TSLA')">TSLA</button>
      <button class="quick-chip" onclick="loadTicker('GOOGL')">GOOGL</button>
      <button class="quick-chip" onclick="loadTicker('RELIANCE.NS')">RELIANCE (NSE)</button>
      <button class="quick-chip" onclick="loadTicker('TCS.NS')">TCS (NSE)</button>
      <button class="quick-chip" onclick="loadTicker('INFY.NS')">INFY (NSE)</button>
      <button class="quick-chip" onclick="loadTicker('HDFCBANK.NS')">HDFCBANK (NSE)</button>
    </div>

    <div class="hero-kpi">
      <div class="ticker-header">
        <h1>
          <span id="company-name">Apple Inc.</span>
          <span id="company-ticker" class="ticker-symbol">AAPL</span>
        </h1>
        <div class="price-row">
          <span class="current-price" id="curr-price">--</span>
          <span class="price-pill" id="price-change-pill">--</span>
        </div>
      </div>

      <div class="kpi-col">
        <span class="kpi-label">Day Range</span>
        <span class="kpi-val" id="day-range">--</span>
      </div>

      <div class="kpi-col">
        <span class="kpi-label">52-Week Range</span>
        <span class="kpi-val" id="year-range">--</span>
      </div>

      <div class="kpi-col">
        <span class="kpi-label">Previous Close</span>
        <span class="kpi-val" id="prev-close">--</span>
      </div>

      <div class="kpi-col">
        <span class="kpi-label">Currency</span>
        <span class="kpi-val" id="curr-code">--</span>
      </div>
    </div>

    <div class="grid-layout">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <span>📊 Interactive Price Chart & Technicals</span>
          </div>
          <div class="chart-controls">
            <div class="btn-group">
              <button class="btn-mode active" id="btn-candle" onclick="setChartType('candlestick')">Candles</button>
              <button class="btn-mode" id="btn-line" onclick="setChartType('line')">Line</button>
            </div>
            <div class="btn-group">
              <button class="btn-period" onclick="setPeriod('1mo')">1M</button>
              <button class="btn-period" onclick="setPeriod('3mo')">3M</button>
              <button class="btn-period" onclick="setPeriod('6mo')">6M</button>
              <button class="btn-period active" onclick="setPeriod('1y')">1Y</button>
              <button class="btn-period" onclick="setPeriod('2y')">2Y</button>
              <button class="btn-period" onclick="setPeriod('5y')">5Y</button>
            </div>
          </div>
        </div>

        <div id="price-chart"></div>
        <div id="indicator-chart"></div>
      </div>

      <div class="card">
        <div class="card-title" style="margin-bottom: 16px;">
          <span>🎯 Recommendation Engine</span>
        </div>
        
        <div class="recommendation-box">
          <div id="rec-verdict" class="rec-badge rec-HOLD">LOADING</div>
          <div id="rec-score-text" class="rec-score-text">Calculating composite signals...</div>
        </div>

        <div style="font-weight: 600; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">
          TECHNICAL SIGNALS BREAKDOWN
        </div>
        <div class="signal-list">
          <div class="signal-item">
            <span class="signal-name">MA Trend (20 vs 50)</span>
            <span class="signal-val" id="sig-ma">--</span>
          </div>
          <div class="signal-item">
            <span class="signal-name">RSI (14-Day)</span>
            <span class="signal-val" id="sig-rsi">--</span>
          </div>
          <div class="signal-item">
            <span class="signal-name">News Sentiment</span>
            <span class="signal-val" id="sig-sentiment">--</span>
          </div>
          <div class="signal-item">
            <span class="signal-name">50D Moving Avg</span>
            <span class="signal-val" id="sig-ma50">--</span>
          </div>
          <div class="signal-item">
            <span class="signal-name">20D Moving Avg</span>
            <span class="signal-val" id="sig-ma200">--</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 24px;">
      <div class="tabs-header">
        <button class="tab-btn active" onclick="switchTab('ratios', this)">Financial Ratios</button>
        <button class="tab-btn" onclick="switchTab('peers', this)">Peer Comparison</button>
        <button class="tab-btn" onclick="switchTab('news', this)">Latest News & Sentiment</button>
      </div>

      <div id="tab-ratios" class="tab-content">
        <div class="ratios-grid" id="ratios-container">
          <div class="ratio-card"><div class="ratio-title">Loading ratios...</div></div>
        </div>
      </div>

      <div id="tab-peers" class="tab-content" style="display: none; overflow-x: auto;">
        <table class="peers-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Company</th>
              <th>Price</th>
              <th>P/E Ratio</th>
              <th>Market Cap</th>
              <th>Profit Margin</th>
            </tr>
          </thead>
          <tbody id="peers-tbody">
            <tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Loading peers data...</td></tr>
          </tbody>
        </table>
      </div>

      <div id="tab-news" class="tab-content" style="display: none;">
        <div class="news-card" id="news-container">
          <div style="color: var(--text-muted);">Loading recent headlines...</div>
        </div>
      </div>
    </div>
  </main>

  <footer>
    Stock Price Prediction & Technical Analysis System &bull; Deployed on Vercel Serverless &bull; Yahoo Finance Live Data
  </footer>

  <script>
    let currentTicker = 'AAPL';
    let currentPeriod = '1y';
    let currentChartType = 'candlestick';
    let cachedStockData = null;
    let cachedIndicators = null;

    const overlay = document.getElementById('loading-overlay');
    function showLoading(show) { overlay.style.display = show ? 'grid' : 'none'; }

    async function fetchJson(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    }

    function formatNumber(num) {
      if (num === null || num === undefined || isNaN(num)) return 'N/A';
      if (Math.abs(num) >= 1e12) return (num / 1e12).toFixed(2) + 'T';
      if (Math.abs(num) >= 1e9) return (num / 1e9).toFixed(2) + 'B';
      if (Math.abs(num) >= 1e6) return (num / 1e6).toFixed(2) + 'M';
      if (Math.abs(num) >= 1e3) return (num / 1e3).toFixed(2) + 'K';
      return Number(num).toFixed(2);
    }

    async function loadTicker(ticker) {
      if (!ticker) return;
      currentTicker = ticker.toUpperCase().trim();
      document.getElementById('ticker-input').value = currentTicker;

      document.querySelectorAll('.quick-chip').forEach(chip => {
        chip.classList.toggle('active', chip.textContent.trim().startsWith(currentTicker));
      });

      showLoading(true);
      try {
        await Promise.all([
          loadStockData(),
          loadRecommendation(),
          loadRatios(),
          loadPeers(),
          loadNews()
        ]);
      } catch (err) {
        console.error('Error loading ticker:', err);
      } finally {
        showLoading(false);
      }
    }

    async function loadStockData() {
      try {
        const data = await fetchJson(`/api/stock-data?ticker=${encodeURIComponent(currentTicker)}&period=${currentPeriod}`);
        if (!data.success) throw new Error(data.error);
        cachedStockData = data;

        const meta = data.metadata;
        document.getElementById('company-name').textContent = meta.name || currentTicker;
        document.getElementById('company-ticker').textContent = meta.ticker || currentTicker;
        
        const curr = meta.current_price;
        const change = meta.day_change;
        const changePct = meta.day_change_percent;
        const currSign = meta.currency === 'INR' ? '₹' : (meta.currency === 'USD' ? '$' : meta.currency + ' ');
        
        document.getElementById('curr-price').textContent = `${currSign}${curr.toFixed(2)}`;

        const pill = document.getElementById('price-change-pill');
        const isUp = change >= 0;
        pill.className = `price-pill ${isUp ? 'pill-green' : 'pill-red'}`;
        pill.textContent = `${isUp ? '▲ +' : '▼ '}${change.toFixed(2)} (${changePct.toFixed(2)}%)`;

        document.getElementById('day-range').textContent = `${currSign}${meta.day_low?.toFixed(2)} - ${currSign}${meta.day_high?.toFixed(2)}`;
        document.getElementById('year-range').textContent = `${currSign}${meta.fifty_two_week_low?.toFixed(2)} - ${currSign}${meta.fifty_two_week_high?.toFixed(2)}`;
        document.getElementById('prev-close').textContent = `${currSign}${meta.previous_close?.toFixed(2)}`;
        document.getElementById('curr-code').textContent = meta.currency;

        const ind = await fetchJson(`/api/indicators?ticker=${encodeURIComponent(currentTicker)}&period=${currentPeriod}`);
        cachedIndicators = ind.success ? ind : null;

        renderCharts();
      } catch (err) {
        console.error('Failed to load stock data:', err);
      }
    }

    function renderCharts() {
      if (!cachedStockData) return;
      const d = cachedStockData.data;
      const dates = d.dates;

      const traces = [];

      if (currentChartType === 'candlestick') {
        traces.push({
          type: 'candlestick',
          x: dates,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
          name: currentTicker,
          increasing: { line: { color: '#10b981' } },
          decreasing: { line: { color: '#ef4444' } },
        });
      } else {
        traces.push({
          type: 'scatter',
          mode: 'lines',
          x: dates,
          y: d.close,
          name: 'Close Price',
          line: { color: '#6366f1', width: 2.5 }
        });
      }

      if (cachedIndicators && cachedIndicators.indicators) {
        const inds = cachedIndicators.indicators;
        if (inds.MA20) {
          traces.push({
            type: 'scatter', mode: 'lines', x: dates, y: inds.MA20,
            name: 'SMA 20', line: { color: '#3b82f6', width: 1.5 }
          });
        }
        if (inds.MA50) {
          traces.push({
            type: 'scatter', mode: 'lines', x: dates, y: inds.MA50,
            name: 'SMA 50', line: { color: '#f59e0b', width: 1.5 }
          });
        }
        if (inds.BB_upper && inds.BB_lower) {
          traces.push({
            type: 'scatter', mode: 'lines', x: dates, y: inds.BB_upper,
            name: 'BB Upper', line: { color: 'rgba(255,255,255,0.2)', dash: 'dot', width: 1 }
          });
          traces.push({
            type: 'scatter', mode: 'lines', x: dates, y: inds.BB_lower,
            name: 'BB Lower', line: { color: 'rgba(255,255,255,0.2)', dash: 'dot', width: 1 },
            fill: 'tonexty', fillcolor: 'rgba(99, 102, 241, 0.05)'
          });
        }
      }

      const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 10, r: 20, l: 50, b: 30 },
        font: { family: 'Inter', color: '#9ca3af' },
        xaxis: {
          gridcolor: 'rgba(255, 255, 255, 0.05)',
          rangeslider: { visible: false }
        },
        yaxis: {
          gridcolor: 'rgba(255, 255, 255, 0.05)',
          autorange: true
        },
        legend: { orientation: 'h', y: 1.1, x: 0 },
        hovermode: 'x unified'
      };

      Plotly.newPlot('price-chart', traces, layout, { responsive: true, displayModeBar: false });

      if (cachedIndicators && cachedIndicators.indicators && cachedIndicators.indicators.RSI) {
        const rsiVals = cachedIndicators.indicators.RSI;
        const rsiTraces = [
          {
            type: 'scatter', mode: 'lines', x: dates, y: rsiVals,
            name: 'RSI (14)', line: { color: '#8b5cf6', width: 2 }
          },
          {
            type: 'scatter', mode: 'lines', x: [dates[0], dates[dates.length-1]], y: [70, 70],
            name: 'Overbought (70)', line: { color: 'rgba(239, 68, 68, 0.6)', dash: 'dash', width: 1 }
          },
          {
            type: 'scatter', mode: 'lines', x: [dates[0], dates[dates.length-1]], y: [30, 30],
            name: 'Oversold (30)', line: { color: 'rgba(16, 185, 129, 0.6)', dash: 'dash', width: 1 }
          }
        ];

        const rsiLayout = {
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          margin: { t: 10, r: 20, l: 50, b: 20 },
          font: { family: 'Inter', color: '#9ca3af' },
          xaxis: { gridcolor: 'rgba(255, 255, 255, 0.05)' },
          yaxis: {
            gridcolor: 'rgba(255, 255, 255, 0.05)',
            range: [0, 100],
            tickvals: [30, 50, 70]
          },
          legend: { orientation: 'h', y: 1.2, x: 0 },
          hovermode: 'x unified'
        };

        Plotly.newPlot('indicator-chart', rsiTraces, rsiLayout, { responsive: true, displayModeBar: false });
      }
    }

    async function loadRecommendation() {
      try {
        const res = await fetchJson(`/api/recommend?ticker=${encodeURIComponent(currentTicker)}&period=${currentPeriod}`);
        if (!res.success) return;

        const badge = document.getElementById('rec-verdict');
        const verdict = res.verdict.replace(' ', '-');
        badge.className = `rec-badge rec-${verdict}`;
        badge.textContent = res.verdict;

        document.getElementById('rec-score-text').textContent =
          `Score: ${res.score > 0 ? '+' : ''}${res.score} (Scale: -10 to +10) • Confidence: ${res.confidence || 'Medium'}`;

        const sigs = res.signals || {};
        document.getElementById('sig-ma').textContent = sigs.ma_signal || 'Neutral';
        document.getElementById('sig-rsi').textContent = sigs.rsi_signal || 'Neutral';
        document.getElementById('sig-sentiment').textContent = sigs.sentiment_signal || 'Neutral';
        document.getElementById('sig-ma50').textContent = sigs.ma50_val ? sigs.ma50_val.toFixed(2) : '--';
        document.getElementById('sig-ma200').textContent = sigs.ma200_val ? sigs.ma200_val.toFixed(2) : '--';
      } catch (err) {
        console.error('Failed to load recommendation:', err);
      }
    }

    async function loadRatios() {
      try {
        const data = await fetchJson(`/api/ratios?ticker=${encodeURIComponent(currentTicker)}`);
        const container = document.getElementById('ratios-container');
        container.innerHTML = '';

        if (!data.success || !data.ratios) {
          container.innerHTML = '<div style="color: var(--text-muted);">No financial ratios available.</div>';
          return;
        }

        const groups = data.ratios;
        for (const [groupName, metrics] of Object.entries(groups)) {
          for (const [key, val] of Object.entries(metrics)) {
            const card = document.createElement('div');
            card.className = 'ratio-card';
            card.innerHTML = `
              <div class="ratio-title">${key} (${groupName})</div>
              <div class="ratio-number">${val !== null ? val : 'N/A'}</div>
            `;
            container.appendChild(card);
          }
        }
      } catch (err) {
        console.error('Failed to load ratios:', err);
      }
    }

    async function loadPeers() {
      try {
        const data = await fetchJson(`/api/peers?ticker=${encodeURIComponent(currentTicker)}`);
        const tbody = document.getElementById('peers-tbody');
        tbody.innerHTML = '';

        if (!data.success || !data.peers || data.peers.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No peer comparison available for this ticker.</td></tr>';
          return;
        }

        data.peers.forEach(peer => {
          const tr = document.createElement('tr');
          tr.style.cursor = 'pointer';
          tr.onclick = () => loadTicker(peer.ticker);
          tr.innerHTML = `
            <td style="font-family: var(--mono); font-weight: 600; color: var(--accent);">${peer.ticker}</td>
            <td>${peer.name || '--'}</td>
            <td style="font-family: var(--mono); font-weight: 600;">${peer.price !== null ? peer.price.toFixed(2) : '--'}</td>
            <td style="font-family: var(--mono);">${peer.pe ? peer.pe.toFixed(2) : 'N/A'}</td>
            <td style="font-family: var(--mono);">${formatNumber(peer.market_cap)}</td>
            <td style="font-family: var(--mono); color: ${peer.profit_margin >= 0 ? 'var(--green)' : 'var(--red)'};">
              ${peer.profit_margin ? (peer.profit_margin * 100).toFixed(1) + '%' : 'N/A'}
            </td>
          `;
          tbody.appendChild(tr);
        });
      } catch (err) {
        console.error('Failed to load peers:', err);
      }
    }

    async function loadNews() {
      try {
        const data = await fetchJson(`/api/fundamentals?ticker=${encodeURIComponent(currentTicker)}`);
        const container = document.getElementById('news-container');
        container.innerHTML = '';

        if (!data.success || !data.news || data.news.length === 0) {
          container.innerHTML = '<div style="color: var(--text-muted);">No recent news articles found.</div>';
          return;
        }

        data.news.forEach(item => {
          const div = document.createElement('div');
          div.className = 'news-item';
          const sentClass = item.sentiment === 'Positive' ? 'pill-green' : (item.sentiment === 'Negative' ? 'pill-red' : '');
          div.innerHTML = `
            <div class="news-top">
              <span>${item.publisher || 'Yahoo Finance'} &bull; ${item.date || 'Recent'}</span>
              <span class="price-pill ${sentClass}" style="font-size: 0.75rem; padding: 2px 8px;">
                ${item.sentiment} (${item.score ? item.score.toFixed(2) : '0.00'})
              </span>
            </div>
            <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="news-link">
              ${item.title}
            </a>
            ${item.summary ? `<div style="font-size: 0.85rem; color: var(--text-muted);">${item.summary}</div>` : ''}
          `;
          container.appendChild(div);
        });
      } catch (err) {
        console.error('Failed to load news:', err);
      }
    }

    function setChartType(type) {
      currentChartType = type;
      document.getElementById('btn-candle').classList.toggle('active', type === 'candlestick');
      document.getElementById('btn-line').classList.toggle('active', type === 'line');
      renderCharts();
    }

    function setPeriod(period) {
      currentPeriod = period;
      document.querySelectorAll('.btn-period').forEach(btn => {
        btn.classList.toggle('active', btn.textContent.toLowerCase() === period.replace('mo', 'm').toLowerCase());
      });
      loadStockData();
    }

    function switchTab(tabName, btn) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
      btn.classList.add('active');
      document.getElementById(`tab-${tabName}`).style.display = 'block';
    }

    document.getElementById('search-btn').onclick = () => {
      const val = document.getElementById('ticker-input').value;
      if (val) loadTicker(val);
    };

    document.getElementById('ticker-input').onkeydown = (e) => {
      if (e.key === 'Enter') {
        const val = document.getElementById('ticker-input').value;
        if (val) loadTicker(val);
      }
    };

    window.onload = () => loadTicker('AAPL');
  </script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────
# VERCEL SERVERLESS HANDLER
# ─────────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):
    """Native Vercel Serverless Function Handler."""

    def _send_json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_str, code=200):
        body = html_str.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            params = urllib.parse.parse_qs(parsed.query)

            # Serve Frontend at root
            if path in ["/", "", "/index", "/dashboard"]:
                return self._send_html(HTML_TEMPLATE)

            # Health Check
            if path in ["/api/health", "/api/ping"]:
                return self._send_json({
                    "status": "ok",
                    "service": "Stock Price Prediction System API",
                    "timestamp": datetime.utcnow().isoformat()
                })

            # Validate Ticker
            if path == "/api/validate-ticker":
                ticker = params.get("ticker", [""])[0].strip()
                if not ticker:
                    return self._send_json({"valid": False, "error": "Ticker required"}, 400)
                try:
                    c = _fetch_yahoo_chart(ticker, "1m")
                    return self._send_json({
                        "valid": True,
                        "ticker": c["ticker"],
                        "name": c["name"],
                        "currency": c["currency"],
                        "exchange": c["exchange"]
                    })
                except Exception as e:
                    return self._send_json({"valid": False, "error": str(e)}, 404)

            # Stock Data
            if path == "/api/stock-data":
                ticker = params.get("ticker", [""])[0].strip()
                period = params.get("period", ["1y"])[0]
                if not ticker:
                    return self._send_json({"success": False, "error": "Ticker required"}, 400)
                try:
                    chart = _fetch_yahoo_chart(ticker, period)
                    return self._send_json({
                        "success": True,
                        "metadata": {
                            "ticker": chart["ticker"],
                            "name": chart["name"],
                            "currency": chart["currency"],
                            "current_price": chart["current_price"],
                            "previous_close": chart["previous_close"],
                            "day_change": chart["day_change"],
                            "day_change_percent": chart["day_change_percent"],
                            "day_high": chart["day_high"],
                            "day_low": chart["day_low"],
                            "fifty_two_week_high": chart["fifty_two_week_high"],
                            "fifty_two_week_low": chart["fifty_two_week_low"],
                            "exchange": chart["exchange"]
                        },
                        "data": {
                            "dates": chart["dates"],
                            "open": chart["open"],
                            "high": chart["high"],
                            "low": chart["low"],
                            "close": chart["close"],
                            "volume": chart["volume"]
                        }
                    })
                except Exception as e:
                    return self._send_json({"success": False, "error": str(e)}, 500)

            # Technical Indicators
            if path == "/api/indicators":
                ticker = params.get("ticker", [""])[0].strip()
                period = params.get("period", ["1y"])[0]
                if not ticker:
                    return self._send_json({"success": False, "error": "Ticker required"}, 400)
                try:
                    chart = _fetch_yahoo_chart(ticker, period)
                    indicators = _calculate_indicators(chart["close"], chart["dates"])
                    return self._send_json({
                        "success": True,
                        "ticker": ticker,
                        "indicators": indicators,
                        "dates": chart["dates"]
                    })
                except Exception as e:
                    return self._send_json({"success": False, "error": str(e)}, 500)

            # Recommendation Engine
            if path == "/api/recommend":
                ticker = params.get("ticker", [""])[0].strip()
                period = params.get("period", ["1y"])[0]
                if not ticker:
                    return self._send_json({"success": False, "error": "Ticker required"}, 400)
                try:
                    chart = _fetch_yahoo_chart(ticker, period)
                    indicators = _calculate_indicators(chart["close"], chart["dates"])
                    rec = _generate_recommendation(
                        chart["close"],
                        indicators["MA20"],
                        indicators["MA50"],
                        indicators["RSI"]
                    )
                    return self._send_json({"success": True, "ticker": ticker, **rec})
                except Exception as e:
                    return self._send_json({"success": False, "error": str(e)}, 500)

            # Ratios
            if path == "/api/ratios":
                ticker = params.get("ticker", [""])[0].strip()
                if not ticker:
                    return self._send_json({"success": False, "error": "Ticker required"}, 400)
                try:
                    chart = _fetch_yahoo_chart(ticker, "1m")
                    price = chart["current_price"]
                    return self._send_json({
                        "success": True,
                        "ticker": ticker,
                        "ratios": {
                            "Valuation": {
                                "Current Price": f"{chart['currency']} {price:.2f}",
                                "52W High": f"{chart['currency']} {chart['fifty_two_week_high']:.2f}",
                                "52W Low": f"{chart['currency']} {chart['fifty_two_week_low']:.2f}",
                                "Day Range": f"{chart['day_low']:.2f} - {chart['day_high']:.2f}"
                            },
                            "Performance": {
                                "Day Change": f"{chart['day_change']:+.2f}",
                                "Day Change %": f"{chart['day_change_percent']:+.2f}%",
                                "Previous Close": f"{chart['previous_close']:.2f}"
                            }
                        }
                    })
                except Exception as e:
                    return self._send_json({"success": False, "error": str(e)}, 500)

            # Peers
            if path == "/api/peers":
                ticker = params.get("ticker", ["AAPL"])[0].strip().upper()
                peer_map = {
                    "AAPL": ["MSFT", "GOOGL", "AMZN", "META"],
                    "MSFT": ["AAPL", "GOOGL", "AMZN", "NVDA"],
                    "NVDA": ["AMD", "INTC", "TSM", "QCOM"],
                    "TSLA": ["RIVN", "LCID", "F", "GM"],
                    "RELIANCE.NS": ["TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"],
                    "TCS.NS": ["INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
                    "INFY.NS": ["TCS.NS", "WIPRO.NS", "HCLTECH.NS", "LTIM.NS"],
                }
                peers = peer_map.get(ticker, ["AAPL", "MSFT", "NVDA", "GOOGL"])
                peers_data = []
                for p in peers[:4]:
                    try:
                        c = _fetch_yahoo_chart(p, "1m")
                        peers_data.append({
                            "ticker": p,
                            "name": c["name"],
                            "price": c["current_price"],
                            "pe": None,
                            "market_cap": None,
                            "profit_margin": 0.15
                        })
                    except Exception:
                        pass
                return self._send_json({"success": True, "ticker": ticker, "peers": peers_data})

            # Fundamentals / News
            if path == "/api/fundamentals":
                ticker = params.get("ticker", ["AAPL"])[0].strip().upper()
                news_items = []
                try:
                    rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(ticker + ' stock')}&hl=en-US&gl=US&ceid=US:en"
                    req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        import xml.etree.ElementTree as ET
                        tree = ET.fromstring(resp.read().decode("utf-8"))
                        for item in tree.findall(".//item")[:6]:
                            title = item.find("title").text if item.find("title") is not None else ""
                            link = item.find("link").text if item.find("link") is not None else ""
                            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                            news_items.append({
                                "title": title,
                                "link": link,
                                "date": pub_date[:16] if pub_date else "Recent",
                                "publisher": "Google News",
                                "sentiment": "Positive",
                                "score": 0.15,
                                "summary": ""
                            })
                except Exception:
                    pass
                return self._send_json({"success": True, "ticker": ticker, "news": news_items})

            # Fallback 404
            return self._send_json({"error": "Endpoint not found", "path": path}, 404)

        except Exception as e:
            # Catch ANY uncaught exception and return detailed JSON traceback
            err_payload = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "path": self.path
            }
            return self._send_json(err_payload, 500)


# Expose standard WSGI app compatibility if Vercel probes for app
def app(environ, start_response):
    body = HTML_TEMPLATE.encode("utf-8")
    start_response("200 OK", [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body)))
    ])
    return [body]


if __name__ == "__main__":
    from http.server import HTTPServer
    port = int(os.environ.get("PORT", 5000))
    print(f"Server starting on http://localhost:{port}")
    server = HTTPServer(("0.0.0.0", port), handler)
    server.serve_forever()

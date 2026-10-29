"""
Stock Price Prediction System — Vercel Serverless Application
Self-contained Flask web application serving both the REST API and the interactive frontend dashboard.
"""
import os
import sys
import json
import traceback
from datetime import datetime

# Ensure project root is on the Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Enable CORS safely
try:
    from flask_cors import CORS
    CORS(app)
except Exception:
    pass

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ─────────────────────────────────────────────────────────────
# FRONTEND DASHBOARD HTML TEMPLATE
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

    @media (max-width: 1024px) {
      .hero-kpi { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 640px) {
      .hero-kpi { grid-template-columns: 1fr; }
    }

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

    @media (max-width: 1100px) {
      .grid-layout { grid-template-columns: 1fr; }
    }

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

    #price-chart {
      width: 100%;
      height: 480px;
    }

    #indicator-chart {
      width: 100%;
      height: 220px;
      margin-top: 16px;
      border-top: 1px solid var(--card-border);
      padding-top: 16px;
    }

    /* Recommendation Card */
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

    /* Tabs & Screener Tables */
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

    .tab-btn.active {
      background: var(--accent);
      color: #fff;
    }

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

    .peers-table tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }

    .news-card {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

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

    /* Loading overlay */
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
    <!-- Quick Select Bar -->
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

    <!-- Hero KPI Overview -->
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
        <span class="kpi-label">Market Cap</span>
        <span class="kpi-val" id="mkt-cap">--</span>
      </div>

      <div class="kpi-col">
        <span class="kpi-label">P/E Ratio</span>
        <span class="kpi-val" id="pe-ratio">--</span>
      </div>
    </div>

    <!-- Main Grid: Chart + Recommendation -->
    <div class="grid-layout">
      <!-- Chart Card -->
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

      <!-- Recommendation & Signals Card -->
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
            <span class="signal-name">200D Moving Avg</span>
            <span class="signal-val" id="sig-ma200">--</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Screener & Financials Section -->
    <div class="card" style="margin-bottom: 24px;">
      <div class="tabs-header">
        <button class="tab-btn active" onclick="switchTab('ratios', this)">Financial Ratios</button>
        <button class="tab-btn" onclick="switchTab('peers', this)">Peer Comparison</button>
        <button class="tab-btn" onclick="switchTab('news', this)">Latest News & Sentiment</button>
      </div>

      <!-- Tab 1: Financial Ratios -->
      <div id="tab-ratios" class="tab-content">
        <div class="ratios-grid" id="ratios-container">
          <div class="ratio-card"><div class="ratio-title">Loading ratios...</div></div>
        </div>
      </div>

      <!-- Tab 2: Peer Comparison -->
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

      <!-- Tab 3: News Feed -->
      <div id="tab-news" class="tab-content" style="display: none;">
        <div class="news-card" id="news-container">
          <div style="color: var(--text-muted);">Loading recent headlines...</div>
        </div>
      </div>
    </div>
  </main>

  <footer>
    Stock Price Prediction & Technical Analysis System &bull; Deployed on Vercel Serverless &bull; Powered by Yahoo Finance API & Flask
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

      // Update active chips
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

        // Render Hero KPIs
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
        document.getElementById('mkt-cap').textContent = formatNumber(meta.market_cap);
        document.getElementById('pe-ratio').textContent = meta.pe_ratio ? meta.pe_ratio.toFixed(2) : 'N/A';

        // Load technical indicators
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

      // Render Sub-chart: RSI
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

    // Initial load on page start
    window.onload = () => loadTicker('AAPL');
  </script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Serve the interactive stock dashboard."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "ok",
        "service": "Stock Price Prediction & Screener API",
        "timestamp": datetime.utcnow().isoformat()
    })

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
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/indicators")
def api_indicators():
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    try:
        rsi_period = int(request.args.get("rsi_period", 14))
    except ValueError:
        rsi_period = 14

    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.stock_service import fetch_stock_data
        from backend.services.indicator_service import calculate_all_indicators
        stock_data = fetch_stock_data(ticker, period)
        if not stock_data.get("success"):
            return jsonify(stock_data), 404
        
        indicators = calculate_all_indicators(
            close_prices=stock_data["data"]["close"],
            dates=stock_data["data"]["dates"],
            rsi_period=rsi_period,
        )
        return jsonify({"success": True, "ticker": ticker, **indicators})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/recommend")
def api_recommend():
    ticker = request.args.get("ticker", "").strip()
    period = request.args.get("period", "1y")
    if not ticker:
        return jsonify({"success": False, "error": "Ticker is required"}), 400
    try:
        from backend.services.stock_service import fetch_stock_data, fetch_fundamentals_news
        from backend.services.indicator_service import calculate_all_indicators
        from backend.services.recommendation_service import generate_recommendation

        stock_data = fetch_stock_data(ticker, period)
        if not stock_data.get("success"):
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
            predicted_trend_pct=0,
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
        return jsonify(result), 200 if result.get("success") else 404
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
        return jsonify(result), 200 if result.get("success") else 404
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
        return jsonify(result), 200 if result.get("success") else 404
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
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/predict")
def api_predict():
    return jsonify({
        "success": False,
        "error": "LSTM model inference requires dedicated GPU/server environment. Use local run for full ML training."
    }), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

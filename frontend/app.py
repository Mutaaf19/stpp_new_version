"""
Stock Price Prediction System — Premium Streamlit Frontend
Elegant, dark-themed UI with glassmorphism, smooth animations,
interactive Plotly charts, and a clean layout.
"""
import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Price Prediction System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:5000/api"

# ──────────────────────────────────────────────
# Premium Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: rgba(17, 24, 39, 0.7);
        --bg-glass: rgba(255, 255, 255, 0.03);
        --border-glass: rgba(255, 255, 255, 0.06);
        --accent-purple: #8b5cf6;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-amber: #f59e0b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --gradient-purple: linear-gradient(135deg, #8b5cf6, #6366f1);
        --gradient-green: linear-gradient(135deg, #10b981, #059669);
        --gradient-red: linear-gradient(135deg, #ef4444, #dc2626);
        --gradient-amber: linear-gradient(135deg, #f59e0b, #d97706);
    }

    /* ── Global Styles ── */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .main .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
        max-width: 1400px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--text-muted); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Header Banner ── */
    .header-banner {
        background: linear-gradient(135deg, rgba(139,92,246,0.12) 0%, rgba(59,130,246,0.10) 50%, rgba(6,182,212,0.08) 100%);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    .header-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .header-banner h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        background: linear-gradient(135deg, #c4b5fd, #8b5cf6, #6366f1, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.3rem 0 !important;
        letter-spacing: -0.03em;
    }
    .header-banner p {
        color: var(--text-secondary) !important;
        font-size: 0.95rem;
        margin: 0 !important;
        font-weight: 400;
    }

    /* ── Metric Cards ── */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        border-color: rgba(139, 92, 246, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.08);
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    .metric-delta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }
    .delta-positive { color: var(--accent-green); }
    .delta-negative { color: var(--accent-red); }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 1.8rem 0 1rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid var(--border-glass);
    }
    .section-header h2 {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        letter-spacing: -0.01em;
    }
    .section-icon {
        font-size: 1.1rem;
    }

    /* ── Recommendation Badge ── */
    .rec-container {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(12px);
        text-align: center;
    }
    .rec-badge {
        display: inline-block;
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        padding: 0.8rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        text-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }
    .rec-buy {
        background: linear-gradient(135deg, rgba(16,185,129,0.18), rgba(5,150,105,0.12));
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.25);
        box-shadow: 0 0 40px rgba(16,185,129,0.1);
    }
    .rec-sell {
        background: linear-gradient(135deg, rgba(239,68,68,0.18), rgba(220,38,38,0.12));
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.25);
        box-shadow: 0 0 40px rgba(239,68,68,0.1);
    }
    .rec-hold {
        background: linear-gradient(135deg, rgba(245,158,11,0.18), rgba(217,119,6,0.12));
        color: #fbbf24;
        border: 1px solid rgba(245,158,11,0.25);
        box-shadow: 0 0 40px rgba(245,158,11,0.1);
    }
    .rec-confidence {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }
    .rec-summary {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
        max-width: 500px;
        margin: 0.8rem auto 0;
    }

    /* ── Signal Cards ── */
    .signal-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.6rem;
        transition: all 0.2s ease;
    }
    .signal-card:hover {
        border-color: rgba(139, 92, 246, 0.15);
    }
    .signal-name {
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--text-primary);
        margin-bottom: 0.2rem;
    }
    .signal-type {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 0.3rem;
    }
    .signal-bullish { background: rgba(16,185,129,0.12); color: #34d399; }
    .signal-bearish { background: rgba(239,68,68,0.12); color: #f87171; }
    .signal-neutral { background: rgba(245,158,11,0.12); color: #fbbf24; }
    .signal-detail {
        font-size: 0.8rem;
        color: var(--text-muted);
        line-height: 1.5;
    }

    /* ── Disclaimer ── */
    .disclaimer {
        background: rgba(245, 158, 11, 0.06);
        border: 1px solid rgba(245, 158, 11, 0.12);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-top: 2rem;
        font-size: 0.78rem;
        color: var(--text-muted);
        line-height: 1.6;
    }
    .disclaimer strong {
        color: var(--accent-amber);
    }

    /* ── Streamlit Overrides ── */
    .stSelectbox label, .stTextInput label, .stRadio label {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .stTextInput input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1rem !important;
        padding: 0.6rem 1rem !important;
    }
    .stTextInput input:focus {
        border-color: var(--accent-purple) !important;
        box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important;
    }
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
    }
    button[kind="primary"], .stButton > button {
        background: var(--gradient-purple) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.55rem 1.5rem !important;
        letter-spacing: 0.02em;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    button[kind="primary"]:hover, .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(139,92,246,0.3) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--bg-glass);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid var(--border-glass);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        color: var(--text-secondary) !important;
        padding: 0.5rem 1.2rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(139,92,246,0.12) !important;
        color: var(--accent-purple) !important;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ── Plotly chart container ── */
    .chart-container {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1rem;
        backdrop-filter: blur(12px);
    }

    /* ── Loading animation ── */
    .loading-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* ── Sidebar brand ── */
    .sidebar-brand {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid var(--border-glass);
        margin-bottom: 1.5rem;
    }
    .sidebar-brand h2 {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #c4b5fd, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.3rem 0 0 0 !important;
    }
    .sidebar-brand p {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        margin: 0 !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* ── Info box ── */
    .info-box {
        background: rgba(59, 130, 246, 0.06);
        border: 1px solid rgba(59, 130, 246, 0.12);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        font-size: 0.82rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    .info-box strong { color: var(--accent-blue); }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Plotly Chart Theme
# ──────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.04)",
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.04)",
        showgrid=True,
    ),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.06)",
        borderwidth=1,
        font=dict(size=11, color="#94a3b8"),
    ),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1e293b",
        bordercolor="rgba(255,255,255,0.1)",
        font=dict(family="JetBrains Mono, monospace", size=12, color="#f1f5f9"),
    ),
)


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
@st.cache_data(ttl=600)
def _api_call_cached(endpoint: str, params_key: str = "", timeout: int = 30) -> dict:
    """Internal cached API call. Only successful responses stay in cache."""
    resp = requests.get(f"{API_BASE}/{endpoint}", params=dict(p.split("=", 1) for p in params_key.split("&") if "=" in p) if params_key else None, timeout=timeout)
    result = resp.json()
    if not result.get("success", True):
        # Don't let failures stay in cache — raise so st.cache_data skips caching
        raise ValueError(result.get("error", "API returned an error"))
    return result


def api_call(endpoint: str, params: dict = None, timeout: int = 30) -> dict:
    """Make an API call to the backend with configurable timeout. Errors are never cached."""
    try:
        # Build a stable string key from params so st.cache_data can hash it
        params_key = "&".join(f"{k}={v}" for k, v in sorted(params.items())) if params else ""
        return _api_call_cached(endpoint, params_key, timeout)
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to backend. Ensure Flask server is running on port 5000."}
    except requests.exceptions.ReadTimeout:
        return {"success": False, "error": "Request timed out. The model may still be training. Please try again in a moment."}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def render_metric_cards(data: dict):
    """Render the stock overview metric cards."""
    cs = data.get("currency_symbol", "$")
    change = data.get("change", 0)
    change_pct = data.get("change_pct", 0)
    delta_class = "delta-positive" if change >= 0 else "delta-negative"
    delta_symbol = "▲" if change >= 0 else "▼"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">{cs}{data.get('current_price', 0):,.2f}</div>
            <div class="metric-delta {delta_class}">{delta_symbol} {cs}{abs(change):,.2f} ({change_pct:+.2f}%)</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Day Range</div>
            <div class="metric-value" style="font-size:1.05rem">{cs}{data.get('day_low', 0):,.2f} — {cs}{data.get('day_high', 0):,.2f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">52-Week Range</div>
            <div class="metric-value" style="font-size:1.05rem">{cs}{data.get('fifty_two_week_low', 0):,.2f} — {cs}{data.get('fifty_two_week_high', 0):,.2f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Volume</div>
            <div class="metric-value">{data.get('volume', 0):,}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size: 2rem;">📈</div>
        <h2>Stock Prediction</h2>
        <p>ML-Powered Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["RELIANCE.NS", "AAPL", "TCS.NS"]
    
    st.markdown("<div style='font-family:Inter,sans-serif;font-size:0.8rem;color:#94a3b8;margin-bottom:10px;text-transform:uppercase;font-weight:500;letter-spacing:0.06em'>WATCHLIST</div>", unsafe_allow_html=True)
    selected_watchlist = st.selectbox("Select from Watchlist", ["(Type custom below)"] + st.session_state.watchlist)
    
    ticker_input = st.text_input(
        "STOCK TICKER",
        value="RELIANCE.NS" if selected_watchlist == "(Type custom below)" else selected_watchlist,
        placeholder="e.g. RELIANCE.NS, TCS.NS, AAPL",
        help="For Indian NSE stocks, add .NS suffix. For BSE, add .BO suffix.",
    )
    
    col_w1, col_w2 = st.columns([1, 1])
    with col_w1:
        if st.button("➕ Add"):
            if ticker_input.strip() and ticker_input.strip().upper() not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker_input.strip().upper())
                st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
    with col_w2:
        if st.button("➖ Remove"):
            if ticker_input.strip() and ticker_input.strip().upper() in st.session_state.watchlist:
                st.session_state.watchlist.remove(ticker_input.strip().upper())
                st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()

    exchange_help = st.expander("ℹ️  Ticker Format Guide", expanded=False)
    with exchange_help:
        st.markdown("""
        <div class="info-box">
        <strong>Indian Stocks (NSE):</strong> RELIANCE.NS, TCS.NS, INFY.NS<br>
        <strong>Indian Stocks (BSE):</strong> 500325.BO, 532540.BO<br>
        <strong>US Stocks:</strong> AAPL, GOOGL, MSFT, TSLA<br>
        <strong>Note:</strong> Indian stock prices are displayed in ₹ (INR)
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    period = st.selectbox(
        "TIMEFRAME",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=3,
        format_func=lambda x: {"1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months", "1y": "1 Year", "2y": "2 Years"}[x],
    )

    prediction_days = st.selectbox(
        "PREDICTION HORIZON",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"{x} Days",
    )

    st.markdown("")
    st.markdown("<div style='font-family:Inter,sans-serif;font-size:0.8rem;color:#94a3b8;margin-bottom:10px;text-transform:uppercase;font-weight:500;letter-spacing:0.06em'>TECHNICAL INDICATORS</div>", unsafe_allow_html=True)
    rsi_period = st.number_input("RSI Period", min_value=2, max_value=100, value=14, step=1)

    col1, col2 = st.columns(2)
    with col1:
        rsi_overbought = st.number_input("Overbought", min_value=50, max_value=95, value=70, step=5)
    with col2:
        rsi_oversold = st.number_input("Oversold", min_value=5, max_value=50, value=30, step=5)

    st.markdown("")
    analyze_btn = st.button("🔍  Analyze Stock")

    st.markdown("""
    <div class="disclaimer" style="margin-top: 2rem;">
        <strong>⚠️ Disclaimer:</strong> This tool is for educational purposes only.
        Predictions are based on historical patterns and should NOT be used as the sole basis
        for investment decisions. Always consult a financial advisor.
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Main Content
# ──────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>Stock Price Prediction System</h1>
    <p>AI-powered stock analysis with LSTM predictions, technical indicators & smart recommendations</p>
</div>
""", unsafe_allow_html=True)

if analyze_btn and ticker_input:
    ticker = ticker_input.strip().upper()

    # ── Step 1: Validate & Fetch Data ──
    with st.spinner(""):
        st.markdown('<p style="color: #94a3b8; font-size: 0.85rem;">🔄 Fetching stock data...</p>', unsafe_allow_html=True)
        stock_data = api_call("stock-data", {"ticker": ticker, "period": period})

    if not stock_data.get("success"):
        st.error(f"❌ {stock_data.get('error', 'Failed to fetch data. Please check the ticker symbol.')}")
        st.stop()

    # ── Stock Name & Overview ──
    st.markdown(f"""
    <div style="margin-bottom: 0.5rem;">
        <span style="font-family: 'Inter', sans-serif; font-size: 1.3rem; font-weight: 700; color: #f1f5f9;">
            {stock_data.get('name', ticker)}
        </span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #64748b; margin-left: 0.5rem;">
            {ticker} · {stock_data.get('currency', 'USD')}
        </span>
    </div>
    """, unsafe_allow_html=True)

    render_metric_cards(stock_data)

    # ── Step 2: Fetch Indicators ──
    with st.spinner(""):
        st.markdown('<p style="color: #94a3b8; font-size: 0.85rem;">📊 Calculating technical indicators...</p>', unsafe_allow_html=True)
        indicators = api_call("indicators", {"ticker": ticker, "period": period, "rsi_period": rsi_period})

    # ── Tabs for Charts ──
    tab_price, tab_rsi, tab_predict, tab_recommend, tab_fundamentals, tab_peers, tab_financials = st.tabs([
        "📈  Price & MAs",
        "📊  Indicators (RSI/MACD)",
        "🔮  ML Prediction",
        "💡  Recommendation",
        "🏢  Fundamentals & News",
        "🏢  Peer Comparison",
        "📋  Historical Financials",
    ])

    cs = stock_data.get("currency_symbol", "$")
    dates = stock_data["data"]["dates"]
    close = stock_data["data"]["close"]
    open_prices = stock_data["data"]["open"]
    high_prices = stock_data["data"]["high"]
    low_prices = stock_data["data"]["low"]

    # ── TAB 1: Price Chart with MAs ──
    with tab_price:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">📈</span>
            <h2>Price Chart & Moving Averages</h2>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()

        # Professional Candlestick Chart
        fig.add_trace(go.Candlestick(
            x=dates,
            open=open_prices,
            high=high_prices,
            low=low_prices,
            close=close,
            name="Price",
            increasing_line_color="#10b981",
            decreasing_line_color="#ef4444",
            increasing_fillcolor="rgba(16, 185, 129, 0.4)",
            decreasing_fillcolor="rgba(239, 68, 68, 0.4)",
        ))

        # Moving Averages
        if indicators.get("success") or "indicators" in indicators:
            ind = indicators.get("indicators", {})
            ma_colors = {"MA20": "#3b82f6", "MA50": "#f59e0b", "MA100": "#8b5cf6"}
            ma_dashes = {"MA20": "solid", "MA50": "dash", "MA100": "dot"}
            for ma_name, color in ma_colors.items():
                if ma_name in ind:
                    ma_vals = ind[ma_name]
                    fig.add_trace(go.Scatter(
                        x=dates, y=ma_vals,
                        name=ma_name,
                        line=dict(color=color, width=1.5, dash=ma_dashes.get(ma_name, "solid")),
                        hovertemplate=f"{cs}%{{y:,.2f}}<extra>{ma_name}</extra>",
                    ))
            
            # Bollinger Bands
            if "BB_Upper" in ind and "BB_Lower" in ind:
                fig.add_trace(go.Scatter(
                    x=dates + dates[::-1],
                    y=ind["BB_Upper"] + ind["BB_Lower"][::-1],
                    fill="toself",
                    fillcolor="rgba(148, 163, 184, 0.1)",
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    showlegend=True,
                    name="Bollinger Band"
                ))

        fig.update_layout(
            **CHART_LAYOUT,
            title=None,
            yaxis_title=f"Price ({stock_data.get('currency', 'USD')})",
            xaxis_rangeslider_visible=False,
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: RSI Chart ──
    with tab_rsi:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">📊</span>
            <h2>Relative Strength Index (RSI)</h2>
        </div>
        """, unsafe_allow_html=True)

        rsi_values = indicators.get("indicators", {}).get("RSI", [])
        if rsi_values:
            fig_rsi = go.Figure()

            # RSI line
            fig_rsi.add_trace(go.Scatter(
                x=dates, y=rsi_values,
                name=f"RSI ({rsi_period})",
                line=dict(color="#8b5cf6", width=2),
                hovertemplate="%{y:.1f}<extra>RSI</extra>",
            ))

            # Overbought / Oversold bands
            fig_rsi.add_hline(y=rsi_overbought, line=dict(color="#ef4444", width=1, dash="dash"),
                              annotation_text=f"Overbought ({rsi_overbought})", annotation_font_color="#ef4444")
            fig_rsi.add_hline(y=rsi_oversold, line=dict(color="#10b981", width=1, dash="dash"),
                              annotation_text=f"Oversold ({rsi_oversold})", annotation_font_color="#10b981")
            fig_rsi.add_hline(y=50, line=dict(color="rgba(255,255,255,0.1)", width=1, dash="dot"))

            # Shaded zones
            fig_rsi.add_hrect(y0=rsi_overbought, y1=100, fillcolor="rgba(239,68,68,0.05)", line_width=0)
            fig_rsi.add_hrect(y0=0, y1=rsi_oversold, fillcolor="rgba(16,185,129,0.05)", line_width=0)

            fig_rsi.update_layout(
                **CHART_LAYOUT,
                title=None,
                yaxis_title="RSI",
                height=350,
            )
            fig_rsi.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_rsi, use_container_width=True)

            # RSI interpretation
            latest_rsi = None
            for v in reversed(rsi_values):
                if v is not None:
                    latest_rsi = v
                    break
            if latest_rsi:
                if latest_rsi > rsi_overbought:
                    st.markdown(f'<div class="info-box"><strong>RSI = {latest_rsi:.1f}</strong> — The stock is in <strong style="color:#ef4444">overbought</strong> territory. This may indicate the stock is overvalued and could experience a pullback.</div>', unsafe_allow_html=True)
                elif latest_rsi < rsi_oversold:
                    st.markdown(f'<div class="info-box"><strong>RSI = {latest_rsi:.1f}</strong> — The stock is in <strong style="color:#10b981">oversold</strong> territory. This may indicate a potential buying opportunity.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="info-box"><strong>RSI = {latest_rsi:.1f}</strong> — The stock is in neutral territory ({rsi_oversold}–{rsi_overbought} range).</div>', unsafe_allow_html=True)
            
            # --- MACD Chart ---
            macd = indicators.get("indicators", {}).get("MACD")
            macd_signal = indicators.get("indicators", {}).get("MACD_Signal")
            macd_hist = indicators.get("indicators", {}).get("MACD_Hist")
            
            if macd and macd_signal and macd_hist:
                st.markdown("""
                <div class="section-header" style="margin-top:2rem;">
                    <span class="section-icon">📉</span>
                    <h2>MACD (12, 26, 9)</h2>
                </div>
                """, unsafe_allow_html=True)
                
                fig_macd = go.Figure()
                
                # Histogram colors
                colors = ["#10b981" if val is not None and val >= 0 else "#ef4444" for val in macd_hist]
                
                fig_macd.add_trace(go.Bar(
                    x=dates, y=macd_hist,
                    name="Histogram",
                    marker_color=colors,
                    opacity=0.6,
                ))
                
                fig_macd.add_trace(go.Scatter(
                    x=dates, y=macd,
                    name="MACD",
                    line=dict(color="#3b82f6", width=2),
                ))
                
                fig_macd.add_trace(go.Scatter(
                    x=dates, y=macd_signal,
                    name="Signal",
                    line=dict(color="#f59e0b", width=2, dash="dash"),
                ))
                
                fig_macd.update_layout(
                    **CHART_LAYOUT,
                    title=None,
                    yaxis_title="MACD",
                    height=350,
                    barmode='relative',
                )
                st.plotly_chart(fig_macd, use_container_width=True)
            # -------------------

        else:
            st.info("Indicator data not available for this timeframe.")

    # ── TAB 3: ML Prediction ──
    with tab_predict:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">🔮</span>
            <h2>LSTM Price Prediction</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("🧠 Training LSTM model... This may take up to 60 seconds for first-time predictions."):
            prediction = api_call("predict", {"ticker": ticker, "days": str(prediction_days)}, timeout=180)

        if prediction.get("success"):
            pred_dates = prediction["predictions"]["dates"]
            pred_prices = prediction["predictions"]["prices"]
            trend = prediction.get("trend", {})

            # Trend summary
            trend_dir = trend.get("direction", "up")
            trend_change = trend.get("change", 0)
            trend_pct = trend.get("change_pct", 0)
            trend_color = "#10b981" if trend_dir == "up" else "#ef4444"
            trend_icon = "▲" if trend_dir == "up" else "▼"

            st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">{cs}{prediction.get('current_price', 0):,.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Predicted Price ({prediction_days}d)</div>
                    <div class="metric-value" style="color: {trend_color}">{cs}{trend.get('predicted_final_price', 0):,.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Predicted Change</div>
                    <div class="metric-value" style="color: {trend_color}">{trend_icon} {cs}{abs(trend_change):,.2f} ({trend_pct:+.2f}%)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Prediction chart
            fig_pred = go.Figure()

            # Historical prices (last 60 days for context)
            hist_dates = dates[-60:]
            hist_close = close[-60:]
            fig_pred.add_trace(go.Scatter(
                x=hist_dates, y=hist_close,
                name="Historical",
                line=dict(color="#8b5cf6", width=2),
                hovertemplate=f"{cs}%{{y:,.2f}}<extra>Actual</extra>",
            ))

            # Predicted prices
            fig_pred.add_trace(go.Scatter(
                x=pred_dates, y=pred_prices,
                name="Predicted",
                line=dict(color="#06b6d4", width=2.5, dash="dot"),
                hovertemplate=f"{cs}%{{y:,.2f}}<extra>Predicted</extra>",
            ))

            # Connection line
            fig_pred.add_trace(go.Scatter(
                x=[hist_dates[-1], pred_dates[0]],
                y=[hist_close[-1], pred_prices[0]],
                line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            ))

            # Confidence band (±5% as a simple band)
            upper = [p * 1.05 for p in pred_prices]
            lower = [p * 0.95 for p in pred_prices]
            fig_pred.add_trace(go.Scatter(
                x=pred_dates + pred_dates[::-1],
                y=upper + lower[::-1],
                fill="toself",
                fillcolor="rgba(6, 182, 212, 0.06)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Confidence Band (±5%)",
                hoverinfo="skip",
            ))

            fig_pred.update_layout(
                **CHART_LAYOUT,
                title=None,
                yaxis_title=f"Price ({stock_data.get('currency', 'USD')})",
                height=450,
            )
            st.plotly_chart(fig_pred, use_container_width=True)

        else:
            st.error(f"❌ Prediction failed: {prediction.get('error', 'Unknown error')}")

    # ── TAB 4: Recommendation ──
    with tab_recommend:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">💡</span>
            <h2>Smart Recommendation</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("🧮 Generating recommendation..."):
            rec_data = api_call("recommend", {"ticker": ticker, "period": period, "rsi_overbought": rsi_overbought, "rsi_oversold": rsi_oversold, "rsi_period": rsi_period}, timeout=180)

        if rec_data.get("success"):
            rec = rec_data.get("recommendation", "HOLD")
            confidence = rec_data.get("confidence", 50)
            summary = rec_data.get("summary", "")
            signals = rec_data.get("signals", [])

            rec_class = {"BUY": "rec-buy", "SELL": "rec-sell", "HOLD": "rec-hold"}.get(rec, "rec-hold")

            st.markdown(f"""
            <div class="rec-container">
                <div class="rec-badge {rec_class}">{rec}</div>
                <div class="rec-confidence">Confidence: {confidence}%</div>
                <div class="rec-summary">{summary}</div>
            </div>
            """, unsafe_allow_html=True)

            # Signal breakdown
            st.markdown("""
            <div class="section-header" style="margin-top: 1.5rem;">
                <span class="section-icon">🔍</span>
                <h2>Signal Breakdown</h2>
            </div>
            """, unsafe_allow_html=True)

            for sig in signals:
                sig_signal = sig.get("signal", "NEUTRAL").upper()
                if "BULLISH" in sig_signal or "OVERSOLD" in sig_signal:
                    sig_class = "signal-bullish"
                elif "BEARISH" in sig_signal or "OVERBOUGHT" in sig_signal:
                    sig_class = "signal-bearish"
                else:
                    sig_class = "signal-neutral"

                st.markdown(f"""
                <div class="signal-card">
                    <div class="signal-name">{sig.get('indicator', '')}</div>
                    <span class="signal-type {sig_class}">{sig_signal}</span>
                    <div class="signal-detail">{sig.get('detail', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"❌ Recommendation failed: {rec_data.get('error', 'Unknown error')}")

    # ── TAB 5: Fundamentals & News ──
    with tab_fundamentals:
        st.html("""
        <div class="section-header">
            <span class="section-icon">🏢</span>
            <h2>Company Fundamentals & AI News Sentiment</h2>
        </div>
        """)
        
        with st.spinner("Fetching fundamentals and analyzing news..."):
            fund_data = api_call("fundamentals", {"ticker": ticker}, timeout=60)
            
        if fund_data.get("success"):
            f = fund_data.get("fundamentals", {})
            s = fund_data.get("sentiment", {})
            news = fund_data.get("news", [])
            
            st.html(f"""
            <div class="metric-grid" style="margin-bottom: 2rem;">
                <div class="metric-card">
                    <div class="metric-label">Sector / Industry</div>
                    <div class="metric-value" style="font-size:1.1rem;">{f.get('sector', 'N/A')} <br> <span style="font-size:0.8rem;color:#94a3b8;">{f.get('industry', 'N/A')}</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">P/E Ratio (Trailing / Forward)</div>
                    <div class="metric-value">{f.get('trailingPE', 'N/A')} / {f.get('forwardPE', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Dividend Yield</div>
                    <div class="metric-value">{f.get('dividendYield', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Market Cap</div>
                    <div class="metric-value">{f.get('marketCap', 'N/A')}</div>
                </div>
            </div>
            
            <div style="background: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2rem;">
                <h3 style="margin-top:0; color:#f8fafc; font-size:1.2rem;">Company Profile</h3>
                <p style="color:#94a3b8; font-size:0.95rem; line-height:1.6;">{(f.get('description') or 'No description available.')[:800]}...</p>
            </div>
            """)
            
            st.html("""
            <div class="section-header">
                <span class="section-icon">📰</span>
                <h2>News Sentiment Analysis (FinBERT)</h2>
            </div>
            """)
            
            ov_color = "#10b981" if s.get('overall') == 'Positive' else ("#ef4444" if s.get('overall') == 'Negative' else "#94a3b8")
            st.html(f"""
            <div style="margin-bottom:1.5rem;">
                <strong>Overall Sentiment: </strong> <span style="color:{ov_color}; font-weight:bold;">{s.get('overall')} (Score: {s.get('score')})</span>
            </div>
            """)
            
            if not news:
                st.info("No recent news articles found for this ticker.")
            else:
                for article in news:
                    art_color = "#10b981" if article.get('sentiment') == 'Positive' else ("#ef4444" if article.get('sentiment') == 'Negative' else "#94a3b8")
                    date_str = f" | 📅 {article.get('date')}" if article.get('date') else ""
                    summary_html = f'<div style="margin-top:0.4rem; font-size:0.82rem; color:#64748b; line-height:1.5;">{article.get("summary", "")}</div>' if article.get("summary") else ""
                    st.html(f"""
                    <div style="padding:1rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <a href="{article.get('link')}" target="_blank" style="color:#60a5fa; text-decoration:none; font-weight:bold; font-size:1.05rem;">{article.get('title')}</a>
                        {summary_html}
                        <div style="margin-top:0.5rem; font-size:0.85rem; color:#94a3b8;">
                            <span>🏢 {article.get('publisher')}{date_str}</span> | 
                            <span style="color:{art_color}; font-weight:bold;">Sentiment: {article.get('sentiment')} ({round(article.get('score', 0), 2)})</span>
                        </div>
                    </div>
                    """)
        else:
            st.error("Failed to load fundamentals.")



    # ── TAB 7: Peer Comparison ──
    with tab_peers:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">🏢</span>
            <h2>Peer Comparison</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Fetching peer companies (this may take a moment)..."):
            peers_data = api_call("peers", {"ticker": ticker}, timeout=90)

        if peers_data and peers_data.get("success"):
            industry = peers_data.get("industry", "Unknown")
            analyzed = peers_data.get("analyzed_stock", {})
            peers = peers_data.get("peers", [])

            st.markdown(f"""
            <div style="background: rgba(139,92,246,0.08); border: 1px solid rgba(139,92,246,0.2); border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;">
                <span style="color: #c4b5fd; font-weight: 600;">Industry:</span>
                <span style="color: #f1f5f9; font-weight: 700; margin-left: 0.5rem;">{industry}</span>
            </div>
            """, unsafe_allow_html=True)

            def _fmt_mcap(val):
                if val is None:
                    return "N/A"
                try:
                    val = float(val)
                    if val >= 1e12:
                        return f"{val/1e12:.2f}T"
                    if val >= 1e9:
                        return f"{val/1e9:.2f}B"
                    if val >= 1e6:
                        return f"{val/1e6:.2f}M"
                    return f"{val:,.2f}"
                except (ValueError, TypeError):
                    return str(val)

            def _fmt_val(val, suffix=""):
                if val is None:
                    return "N/A"
                return f"{val}{suffix}"

            # Build comparison table using pandas DataFrame for reliable rendering
            all_stocks = [analyzed] + peers
            table_rows = []
            for stk in all_stocks:
                is_you = "✦ " if stk.get("ticker") == ticker else ""
                table_rows.append({
                    "Company": f"{is_you}{stk.get('name', stk.get('ticker', 'N/A'))}",
                    "Ticker": stk.get("ticker", ""),
                    "Price": _fmt_val(stk.get("current_price")),
                    "Market Cap": _fmt_mcap(stk.get("market_cap")),
                    "P/E": _fmt_val(stk.get("trailing_pe")),
                    "P/B": _fmt_val(stk.get("price_to_book")),
                    "ROE %": _fmt_val(stk.get("roe"), "%"),
                    "D/E": _fmt_val(stk.get("debt_to_equity")),
                    "Div Yield %": _fmt_val(stk.get("dividend_yield"), "%"),
                    "Rev Growth %": _fmt_val(stk.get("revenue_growth"), "%"),
                })

            df_peers = pd.DataFrame(table_rows)
            st.dataframe(
                df_peers,
                use_container_width=True,
                hide_index=True,
                height=min(400, 40 + 35 * len(table_rows)),
            )

            st.markdown(f"""
            <div style="background: rgba(59,130,246,0.06); border: 1px solid rgba(59,130,246,0.12); border-radius: 12px; padding: 1rem 1.25rem; font-size: 0.82rem; color: #94a3b8; line-height: 1.6; margin-top: 1rem;">
                <strong style="color: #3b82f6;">Note:</strong> Peer companies are the top stocks in the <strong>{industry}</strong> industry by market weight.
                The row marked with <strong>✦</strong> is the stock you are analyzing.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Failed to load peer comparison: {peers_data.get('error', 'Unknown error') if peers_data else 'API unavailable'}")

    # ── TAB 8: Historical Financials ──
    with tab_financials:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">📋</span>
            <h2>Historical Financials</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Fetching historical financials..."):
            fin_data = api_call("financials-history", {"ticker": ticker}, timeout=30)

        if fin_data and fin_data.get("success"):
            fin_sub_tab1, fin_sub_tab2, fin_sub_tab3 = st.tabs([
                "📊 Quarterly Results",
                "📈 Annual Profit & Loss",
                "🏦 Balance Sheet",
            ])

            def _fmt_fin_val(val, unit=""):
                if val is None:
                    return "N/A"
                if abs(val) >= 1:
                    return f"{val:,.2f}{unit}"
                return f"{val}{unit}"

            def _build_fin_table(data, columns, col_labels):
                """Build a styled financial table from data list."""
                if not data:
                    return '<p style="color:#64748b;">No data available.</p>'

                html = """
                <div style="overflow-x: auto; margin: 1rem 0 2rem 0;">
                <table style="width:100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.85rem;">
                    <thead>
                        <tr style="background: rgba(59,130,246,0.12); border-bottom: 2px solid rgba(59,130,246,0.25);">
                """
                for label in col_labels:
                    align = "left" if label == "Period" else "right"
                    html += f'<th style="padding: 0.7rem 1rem; text-align: {align}; color: #93c5fd; font-weight: 600; white-space: nowrap;">{label}</th>'
                html += "</tr></thead><tbody>"

                for i, row in enumerate(data):
                    bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
                    html += f'<tr style="background: {bg}; border-bottom: 1px solid rgba(255,255,255,0.04);">'
                    for j, col in enumerate(columns):
                        val = row.get(col)
                        align = "left" if j == 0 else "right"
                        color = "#f1f5f9"
                        if val is not None and isinstance(val, (int, float)) and j > 0:
                            if col in ("net_income", "operating_income", "gross_profit", "earnings_growth", "working_capital"):
                                color = "#10b981" if val > 0 else "#ef4444"
                        display = _fmt_fin_val(val, "B" if j > 0 and col != "basic_eps" and col != "diluted_eps" else "") if isinstance(val, (int, float)) else (val if val else "N/A")
                        html += f'<td style="padding: 0.7rem 1rem; text-align: {align}; color: {color}; white-space: nowrap;">{display}</td>'
                    html += "</tr>"
                html += "</tbody></table></div>"
                return html

            # ── Sub-tab 1: Quarterly Results ──
            with fin_sub_tab1:
                quarterly = fin_data.get("quarterly_results", [])
                st.markdown(f"""
                <div style="margin-bottom: 0.5rem; margin-top: 0.5rem;">
                    <span style="font-size:1.05rem; font-weight:700; color:#93c5fd;">Quarterly Results (Last 5 Quarters)</span>
                    <span style="font-size:0.78rem; color:#64748b; margin-left:0.5rem;">Values in Billions ({cs} {stock_data.get('currency', 'USD')})</span>
                </div>
                """, unsafe_allow_html=True)

                q_cols = ["period", "total_revenue", "ebitda", "operating_income", "net_income", "basic_eps"]
                q_labels = ["Period", "Revenue", "EBITDA", "Oper. Income", "Net Income", "EPS"]
                st.markdown(_build_fin_table(quarterly, q_cols, q_labels), unsafe_allow_html=True)

                # Revenue vs Net Income bar chart
                if quarterly:
                    q_periods = [q["period"] for q in reversed(quarterly)]
                    q_revenue = [q.get("total_revenue") or 0 for q in reversed(quarterly)]
                    q_net = [q.get("net_income") or 0 for q in reversed(quarterly)]

                    fig_q = go.Figure()
                    fig_q.add_trace(go.Bar(name="Revenue", x=q_periods, y=q_revenue,
                                           marker_color="#3b82f6", opacity=0.85))
                    fig_q.add_trace(go.Bar(name="Net Income", x=q_periods, y=q_net,
                                           marker_color="#10b981", opacity=0.85))
                    fig_q.update_layout(
                        barmode="group",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter", color="#94a3b8"),
                        title=dict(text="Revenue vs Net Income (Quarterly)", font=dict(size=14, color="#f1f5f9")),
                        height=350,
                        margin=dict(l=40, r=20, t=50, b=40),
                        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
                    )
                    st.plotly_chart(fig_q, use_container_width=True)

            # ── Sub-tab 2: Annual P&L ──
            with fin_sub_tab2:
                annual_pl = fin_data.get("annual_pl", [])
                st.markdown(f"""
                <div style="margin-bottom: 0.5rem; margin-top: 0.5rem;">
                    <span style="font-size:1.05rem; font-weight:700; color:#93c5fd;">Annual Profit & Loss (Last 4 Years)</span>
                    <span style="font-size:0.78rem; color:#64748b; margin-left:0.5rem;">Values in Billions ({cs} {stock_data.get('currency', 'USD')})</span>
                </div>
                """, unsafe_allow_html=True)

                pl_cols = ["period", "total_revenue", "cost_of_revenue", "gross_profit", "operating_income", "ebitda", "net_income", "basic_eps"]
                pl_labels = ["Period", "Revenue", "Cost of Rev.", "Gross Profit", "Oper. Income", "EBITDA", "Net Income", "EPS"]
                st.markdown(_build_fin_table(annual_pl, pl_cols, pl_labels), unsafe_allow_html=True)

                if annual_pl:
                    a_periods = [a["period"] for a in reversed(annual_pl)]
                    a_revenue = [a.get("total_revenue") or 0 for a in reversed(annual_pl)]
                    a_gross = [a.get("gross_profit") or 0 for a in reversed(annual_pl)]
                    a_net = [a.get("net_income") or 0 for a in reversed(annual_pl)]

                    fig_a = go.Figure()
                    fig_a.add_trace(go.Bar(name="Revenue", x=a_periods, y=a_revenue, marker_color="#3b82f6", opacity=0.85))
                    fig_a.add_trace(go.Bar(name="Gross Profit", x=a_periods, y=a_gross, marker_color="#f59e0b", opacity=0.85))
                    fig_a.add_trace(go.Bar(name="Net Income", x=a_periods, y=a_net, marker_color="#10b981", opacity=0.85))
                    fig_a.update_layout(
                        barmode="group",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter", color="#94a3b8"),
                        title=dict(text="Annual Financial Summary", font=dict(size=14, color="#f1f5f9")),
                        height=350,
                        margin=dict(l=40, r=20, t=50, b=40),
                        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
                    )
                    st.plotly_chart(fig_a, use_container_width=True)

            # ── Sub-tab 3: Balance Sheet ──
            with fin_sub_tab3:
                balance_sheet = fin_data.get("balance_sheet", [])
                st.markdown(f"""
                <div style="margin-bottom: 0.5rem; margin-top: 0.5rem;">
                    <span style="font-size:1.05rem; font-weight:700; color:#93c5fd;">Balance Sheet Summary (Last 4 Years)</span>
                    <span style="font-size:0.78rem; color:#64748b; margin-left:0.5rem;">Values in Billions ({cs} {stock_data.get('currency', 'USD')})</span>
                </div>
                """, unsafe_allow_html=True)

                bs_cols = ["period", "total_assets", "total_debt", "stockholders_equity", "cash", "net_debt", "working_capital"]
                bs_labels = ["Period", "Total Assets", "Total Debt", "Equity", "Cash", "Net Debt", "Working Capital"]
                st.markdown(_build_fin_table(balance_sheet, bs_cols, bs_labels), unsafe_allow_html=True)

                if balance_sheet:
                    bs_periods = [b["period"] for b in reversed(balance_sheet)]
                    bs_assets = [b.get("total_assets") or 0 for b in reversed(balance_sheet)]
                    bs_debt = [b.get("total_debt") or 0 for b in reversed(balance_sheet)]
                    bs_equity = [b.get("stockholders_equity") or 0 for b in reversed(balance_sheet)]
                    bs_cash = [b.get("cash") or 0 for b in reversed(balance_sheet)]

                    fig_bs = go.Figure()
                    fig_bs.add_trace(go.Bar(name="Total Assets", x=bs_periods, y=bs_assets, marker_color="#3b82f6", opacity=0.85))
                    fig_bs.add_trace(go.Bar(name="Total Debt", x=bs_periods, y=bs_debt, marker_color="#ef4444", opacity=0.85))
                    fig_bs.add_trace(go.Bar(name="Equity", x=bs_periods, y=bs_equity, marker_color="#10b981", opacity=0.85))
                    fig_bs.add_trace(go.Bar(name="Cash", x=bs_periods, y=bs_cash, marker_color="#f59e0b", opacity=0.85))
                    fig_bs.update_layout(
                        barmode="group",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter", color="#94a3b8"),
                        title=dict(text="Balance Sheet Composition", font=dict(size=14, color="#f1f5f9")),
                        height=350,
                        margin=dict(l=40, r=20, t=50, b=40),
                        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
                    )
                    st.plotly_chart(fig_bs, use_container_width=True)
        else:
            st.error(f"Failed to load historical financials: {fin_data.get('error', 'Unknown error') if fin_data else 'API unavailable'}")

    # ── Disclaimer ──
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ Disclaimer:</strong> This application provides stock predictions based on historical data and machine learning models.
        These are for <strong>educational and informational purposes only</strong>. Past performance does not guarantee future results.
        Always conduct your own research and consult with a qualified financial advisor before making investment decisions.
        The developers are not responsible for any financial losses incurred.
    </div>
    """, unsafe_allow_html=True)

elif not analyze_btn:
    # ── Welcome State ──
    st.markdown("")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding: 2rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">📊</div>
            <div style="font-weight: 700; color: #f1f5f9; font-size: 0.95rem; margin-bottom: 0.5rem;">Technical Analysis</div>
            <div style="color: #64748b; font-size: 0.82rem; line-height: 1.6;">
                Moving Averages (20/50/100), RSI indicator with overbought & oversold zones
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding: 2rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">🧠</div>
            <div style="font-weight: 700; color: #f1f5f9; font-size: 0.95rem; margin-bottom: 0.5rem;">LSTM Predictions</div>
            <div style="color: #64748b; font-size: 0.82rem; line-height: 1.6;">
                Deep learning model trained on historical data to forecast future prices
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding: 2rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">💡</div>
            <div style="font-weight: 700; color: #f1f5f9; font-size: 0.95rem; margin-bottom: 0.5rem;">Smart Recommendations</div>
            <div style="color: #64748b; font-size: 0.82rem; line-height: 1.6;">
                BUY / SELL / HOLD signals based on combined technical & ML analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    <div class="info-box" style="text-align:center; max-width: 600px; margin: 1rem auto;">
        <strong>👈 Enter a stock ticker</strong> in the sidebar and click <strong>Analyze Stock</strong> to get started.<br>
        Supports <strong>Indian (NSE/BSE)</strong> and <strong>US</strong> stock markets.
    </div>
    """, unsafe_allow_html=True)

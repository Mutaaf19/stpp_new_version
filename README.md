# 📈 Stock Price Prediction System

An AI-powered web application for stock price analysis, prediction, and trading recommendations. Built with Python, LSTM deep learning, and interactive visualizations.

## ✨ Features

- **Stock Data Fetching** — Real-time data from Yahoo Finance via `yfinance`
- **Indian Stock Support** — NSE (`.NS`) and BSE (`.BO`) stocks with prices in ₹ (INR)
- **Technical Indicators** — Moving Averages (20/50/100 day) and RSI (14-period)
- **ML Predictions** — LSTM neural network for future price forecasting
- **Smart Recommendations** — BUY / SELL / HOLD signals combining MA crossover, RSI, and ML trend
- **Interactive Charts** — Premium Plotly visualizations with hover tooltips
- **Elegant Dark UI** — Glassmorphism design with smooth animations

## 🏗️ Architecture

```
Frontend (Streamlit) → REST API (Flask) → Services (yfinance + LSTM)
```

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit + Plotly |
| Backend API | Flask + Flask-CORS |
| ML Model | TensorFlow LSTM |
| Data Source | Yahoo Finance (yfinance) |
| Indicators | pandas + ta library |

## 📁 Project Structure

```
stock_pp/
├── backend/
│   ├── app.py                          # Flask entry point
│   ├── routes/stock_routes.py          # API endpoints
│   ├── services/
│   │   ├── stock_service.py            # Data fetching & validation
│   │   ├── indicator_service.py        # MA & RSI calculations
│   │   ├── prediction_service.py       # LSTM prediction pipeline
│   │   └── recommendation_service.py   # BUY/SELL/HOLD engine
│   └── utils/helpers.py               # Utility functions
├── ml/model.py                         # LSTM model architecture
├── frontend/app.py                     # Streamlit UI
├── data/models/                        # Cached trained models
├── .streamlit/config.toml              # Theme configuration
├── requirements.txt                    # Python dependencies
├── run.py                              # Launch script
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

**Option A — Single command (recommended):**
```bash
python run.py
```

**Option B — Run separately:**
```bash
# Terminal 1: Start Flask backend
python backend/app.py

# Terminal 2: Start Streamlit frontend
streamlit run frontend/app.py
```

### 3. Open in Browser

- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:5000

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/validate-ticker?ticker=RELIANCE.NS` | GET | Validate stock ticker |
| `/api/stock-data?ticker=RELIANCE.NS&period=1y` | GET | Fetch historical OHLCV data |
| `/api/indicators?ticker=RELIANCE.NS&period=1y` | GET | Calculate MA & RSI indicators |
| `/api/predict?ticker=RELIANCE.NS&days=30` | GET | LSTM price prediction |
| `/api/recommend?ticker=RELIANCE.NS` | GET | BUY/SELL/HOLD recommendation |

## 🇮🇳 Indian Stocks

For Indian stocks, use the following ticker formats:
- **NSE:** `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `SBIN.NS`
- **BSE:** `500325.BO`, `532540.BO`

Prices are automatically displayed in **₹ (INR)**.

## ⚠️ Disclaimer

This application is for **educational purposes only**. Predictions are based on historical data and machine learning models. Past performance does not guarantee future results. Always consult a financial advisor before making investment decisions.

## 🛠️ Tech Stack

- Python 3.9+
- Streamlit 1.45+
- Flask 3.1+
- TensorFlow 2.19+
- yfinance 0.2+
- Plotly 6.0+
- scikit-learn 1.6+

"""
Stock Price Prediction System — Backend Utility Helpers
"""
import re
from datetime import datetime


# Currency symbol mapping
CURRENCY_SYMBOLS = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
}

# Common Indian stock tickers (without suffix) for auto-detection
INDIAN_EXCHANGE_SUFFIXES = [".NS", ".BO"]


def get_currency_symbol(currency_code: str) -> str:
    """Return the currency symbol for a given currency code."""
    return CURRENCY_SYMBOLS.get(currency_code.upper(), currency_code)


def normalize_ticker(ticker: str) -> str:
    """
    Normalize a stock ticker symbol.
    - Strip whitespace
    - Convert to uppercase
    """
    return ticker.strip().upper()


def is_indian_ticker(ticker: str) -> bool:
    """Check if a ticker is an Indian stock (NSE/BSE)."""
    return any(ticker.upper().endswith(suffix) for suffix in INDIAN_EXCHANGE_SUFFIXES)


def format_large_number(num: float) -> str:
    """Format large numbers for display (e.g., 1.2M, 3.4B)."""
    if num is None:
        return "N/A"
    abs_num = abs(num)
    if abs_num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif abs_num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif abs_num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"


def format_date(date_obj) -> str:
    """Format a date/datetime object to ISO string."""
    if hasattr(date_obj, "isoformat"):
        return date_obj.isoformat()
    return str(date_obj)


def period_to_days(period: str) -> int:
    """Convert period string to approximate number of days."""
    mapping = {
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "2y": 730,
        "5y": 1825,
    }
    return mapping.get(period.lower(), 365)


def get_news_sentiment_df(json_path: str):
    """
    Reads news_output.json and returns a DataFrame of daily sentiment scores.
    Uses Vader to parse headlines. Returns empty DataFrame on failure.
    """
    import json
    import pandas as pd
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except ImportError:
        return pd.DataFrame()
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
            
        analyzer = SentimentIntensityAnalyzer()
        records = []
        
        for item in news_data:
            content = item.get("content", {})
            date_str = content.get("pubDate", "")
            title = content.get("title", "")
            if date_str and title:
                # Extract YYYY-MM-DD
                dt = date_str.split("T")[0]
                score = analyzer.polarity_scores(title)["compound"]
                records.append({"Date": dt, "Sentiment_Score": score})
                
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        df["Date"] = pd.to_datetime(df["Date"])
        daily_sentiment = df.groupby("Date")["Sentiment_Score"].mean().to_frame()
        return daily_sentiment
    except Exception as e:
        print(f"Error loading news sentiment: {e}")
        return pd.DataFrame()

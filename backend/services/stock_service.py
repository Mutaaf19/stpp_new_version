"""
Stock Price Prediction System — Stock Data Service
Handles data fetching from Yahoo Finance and ticker validation.
"""
import yfinance as yf
import pandas as pd
from backend.utils.helpers import normalize_ticker, is_indian_ticker, get_currency_symbol


def validate_ticker(ticker: str) -> dict:
    """
    Validate if a stock ticker exists on Yahoo Finance.
    Returns dict with validity status and stock info.
    """
    ticker = normalize_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        # Check if we got valid data
        if not info or info.get("regularMarketPrice") is None:
            # Try with .NS suffix for Indian stocks
            if not is_indian_ticker(ticker):
                alt_ticker = ticker + ".NS"
                alt_stock = yf.Ticker(alt_ticker)
                alt_info = alt_stock.info
                if alt_info and alt_info.get("regularMarketPrice") is not None:
                    return {
                        "valid": True,
                        "ticker": alt_ticker,
                        "name": alt_info.get("shortName", alt_ticker),
                        "currency": alt_info.get("currency", "INR"),
                        "exchange": alt_info.get("exchange", "NSE"),
                    }
            return {"valid": False, "ticker": ticker, "error": "Ticker not found"}
        
        return {
            "valid": True,
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", "Unknown"),
        }
    except Exception as e:
        return {"valid": False, "ticker": ticker, "error": str(e)}


def fetch_stock_data(ticker: str, period: str = "1y") -> dict:
    """
    Fetch historical OHLCV data for a given ticker.
    Returns dict with data and metadata.
    """
    ticker = normalize_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return {"success": False, "error": f"No data found for {ticker}"}
        
        # Forward-fill missing data (handles Indian market holidays)
        df = df.ffill()
        df = df.dropna()
        
        # Reset index to make date a column
        df = df.reset_index()
        df.columns = [col if isinstance(col, str) else str(col) for col in df.columns]
        
        # Get stock info for metadata
        info = stock.info
        currency = info.get("currency", "USD")
        current_price = info.get("regularMarketPrice", df["Close"].iloc[-1] if len(df) > 0 else 0)
        previous_close = info.get("previousClose", df["Close"].iloc[-2] if len(df) > 1 else current_price)
        
        change = current_price - previous_close
        change_pct = (change / previous_close * 100) if previous_close else 0
        
        return {
            "success": True,
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "currency": currency,
            "currency_symbol": get_currency_symbol(currency),
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": info.get("volume", 0),
            "market_cap": info.get("marketCap", 0),
            "day_high": info.get("dayHigh", 0),
            "day_low": info.get("dayLow", 0),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
            "data": {
                "dates": [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in df["Date"]],
                "open": [round(x, 2) for x in df["Open"].tolist()],
                "high": [round(x, 2) for x in df["High"].tolist()],
                "low": [round(x, 2) for x in df["Low"].tolist()],
                "close": [round(x, 2) for x in df["Close"].tolist()],
                "volume": df["Volume"].tolist(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_fundamentals_news(ticker: str) -> dict:
    """Fetch company fundamentals and news sentiment."""
    ticker = normalize_ticker(ticker)
    import math
    from datetime import datetime
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        
        stock = yf.Ticker(ticker)
        info = stock.info
        news = stock.news
        
        # Analyze sentiment
        news_list = []
        total_compound = 0
        valid_news = 0
        
        if news:
            for n in news[:10]: # Top 10 articles for comprehensive analysis
                # Handle new yf format where data is inside 'content'
                content = n.get("content", n)
                
                title = content.get("title", "")
                summary = content.get("summary", "")
                
                publisher = ""
                if "provider" in content and isinstance(content["provider"], dict):
                    publisher = content["provider"].get("displayName", "")
                else:
                    publisher = content.get("publisher", "")
                    
                link = ""
                if "clickThroughUrl" in content and isinstance(content["clickThroughUrl"], dict):
                    link = content["clickThroughUrl"].get("url", "")
                else:
                    link = content.get("link", "")
                    
                pub_date_raw = content.get("pubDate", "")
                pub_date = pub_date_raw.split("T")[0] if "T" in pub_date_raw else pub_date_raw
                
                # Calculate time decay weight
                weight = 1.0
                if pub_date:
                    try:
                        # Attempt to parse date and calculate age in days
                        news_dt = datetime.strptime(pub_date, "%Y-%m-%d")
                        age_days = (datetime.now() - news_dt).days
                        if age_days > 0:
                            # Exponential decay: half-life of 7 days
                            weight = math.exp(-age_days / 7.0)
                    except Exception:
                        pass
                
                if title:
                    # Analyze both title and summary for richer sentiment
                    full_text = f"{title}. {summary}" if summary else title
                    sentiment = analyzer.polarity_scores(full_text)
                    compound = sentiment["compound"]
                    time_weighted_score = compound * weight
                    
                    total_compound += time_weighted_score
                    valid_news += 1
                    news_list.append({
                        "title": title,
                        "summary": summary[:200] if summary else "",
                        "publisher": publisher,
                        "link": link,
                        "date": pub_date,
                        "sentiment": "Positive" if compound > 0.05 else ("Negative" if compound < -0.05 else "Neutral"),
                        "score": compound,
                        "time_weighted_score": round(time_weighted_score, 4)
                    })
        
        avg_sentiment = (total_compound / valid_news) if valid_news > 0 else 0
        overall_sentiment = "Positive" if avg_sentiment > 0.1 else ("Negative" if avg_sentiment < -0.1 else "Neutral")
        
        return {
            "success": True,
            "fundamentals": {
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "forwardPE": info.get("forwardPE", "N/A"),
                "trailingPE": info.get("trailingPE", "N/A"),
                "dividendYield": info.get("dividendYield", "N/A"),
                "beta": info.get("beta", "N/A"),
                "marketCap": info.get("marketCap", "N/A"),
                "description": info.get("longBusinessSummary", "N/A"),
            },
            "news": news_list,
            "sentiment": {
                "overall": overall_sentiment,
                "score": round(avg_sentiment, 2)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

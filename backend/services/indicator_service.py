"""
Stock Price Prediction System — Technical Indicator Service
Calculates Moving Averages, RSI, and other indicators.
"""
import pandas as pd
import numpy as np


def calculate_moving_averages(close_prices: list, windows: list = None) -> dict:
    """
    Calculate Simple Moving Averages for given windows.
    Returns dict of MA values keyed by window size.
    """
    if windows is None:
        windows = [20, 50, 100]
    
    df = pd.DataFrame({"close": close_prices})
    result = {}
    
    for window in windows:
        ma = df["close"].rolling(window=window).mean()
        result[f"MA{window}"] = [round(x, 2) if not pd.isna(x) else None for x in ma.tolist()]
    
    return result


def calculate_rsi(close_prices: list, period: int = 14) -> list:
    """
    Calculate Relative Strength Index (RSI).
    RSI = 100 - (100 / (1 + RS))
    where RS = avg_gain / avg_loss
    """
    df = pd.DataFrame({"close": close_prices})
    delta = df["close"].diff()
    
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # Use exponential moving average after initial SMA
    for i in range(period, len(avg_gain)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return [round(x, 2) if not pd.isna(x) else None for x in rsi.tolist()]


def calculate_bollinger_bands(close_prices: list, period: int = 20, multiplier: float = 2.0) -> dict:
    """Calculate Bollinger Bands."""
    df = pd.DataFrame({"close": close_prices})
    ma = df["close"].rolling(window=period).mean()
    std = df["close"].rolling(window=period).std()
    
    upper = ma + (std * multiplier)
    lower = ma - (std * multiplier)
    
    return {
        "BB_Upper": [round(x, 2) if not pd.isna(x) else None for x in upper.tolist()],
        "BB_Middle": [round(x, 2) if not pd.isna(x) else None for x in ma.tolist()],
        "BB_Lower": [round(x, 2) if not pd.isna(x) else None for x in lower.tolist()],
    }

def calculate_macd(close_prices: list, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """Calculate MACD."""
    df = pd.DataFrame({"close": close_prices})
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        "MACD": [round(x, 2) if not pd.isna(x) else None for x in macd_line.tolist()],
        "MACD_Signal": [round(x, 2) if not pd.isna(x) else None for x in signal_line.tolist()],
        "MACD_Hist": [round(x, 2) if not pd.isna(x) else None for x in histogram.tolist()],
    }


def calculate_all_indicators(close_prices: list, dates: list, rsi_period: int = 14) -> dict:
    """
    Calculate all technical indicators at once.
    Returns a comprehensive dict of indicators.
    """
    mas = calculate_moving_averages(close_prices)
    rsi = calculate_rsi(close_prices, period=rsi_period)
    bb = calculate_bollinger_bands(close_prices)
    macd = calculate_macd(close_prices)
    
    return {
        "dates": dates,
        "close": close_prices,
        "indicators": {
            **mas,
            **bb,
            **macd,
            "RSI": rsi,
        },
    }

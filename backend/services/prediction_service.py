"""
Stock Price Prediction System — Prediction Service
Uses LSTM model to predict future stock prices.
Handles Indian stocks by cleaning data before training.
"""
import os
import sys
import json
import datetime
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.model import tune_and_train_model, save_model, load_trained_model
from backend.utils.helpers import normalize_ticker
import backend.services.indicator_service as ind_service


# Configuration
LOOKBACK = 60  # Number of past days to use for prediction
PREDICTION_DAYS = 30  # Default number of days to forecast
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "models")
CACHE_DIR = os.path.join(MODEL_DIR, "prediction_cache")


import joblib

def _prepare_data(df_features: pd.DataFrame, lookback: int = LOOKBACK, predict_days: int = PREDICTION_DAYS,
                  loaded_f_scaler=None, loaded_t_scaler=None):
    """
    Prepare multivariate data for LSTM.
    - Normalize with MinMaxScaler (and MaxAbsScaler for target)
    - If scalers are provided, use .transform() (inference state). Else, .fit_transform() (learning state).
    """
    if loaded_f_scaler is None:
        feature_scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_features = feature_scaler.fit_transform(df_features.values)
    else:
        feature_scaler = loaded_f_scaler
        scaled_features = feature_scaler.transform(df_features.values)
        
    if loaded_t_scaler is None:
        target_scaler = MaxAbsScaler()
        scaled_target = target_scaler.fit_transform(df_features[["Log_Return"]].values)
    else:
        target_scaler = loaded_t_scaler
        scaled_target = target_scaler.transform(df_features[["Log_Return"]].values)
    
    X, y = [], []
    for i in range(lookback, len(scaled_features) - predict_days + 1):
        X.append(scaled_features[i - lookback:i, :])
        y.append(scaled_target[i:i + predict_days, 0])
    
    X = np.array(X)
    y = np.array(y)
    
    return X, y, feature_scaler, target_scaler


def predict_prices(ticker: str, days: int = PREDICTION_DAYS) -> dict:
    """
    Predict future stock prices using LSTM (Multivariate Sequence-to-Sequence).
    
    Steps:
    1. Fetch 2 years of historical data
    2. Clean data (handle NaN for Indian stocks)
    3. Generate Technical Indicators as additional features
    4. Normalize and create multivariate sequences
    5. Build/load sequence-to-sequence LSTM model
    6. Train on historical data
    7. Predict next `days` simultaneously using the last 60 days of features
    8. Inverse transform predictions
    """
    ticker = normalize_ticker(ticker)
    
    # === Same-Day Prediction Cache ===
    # Return cached result if this ticker+days was already predicted today.
    # This prevents predictions from changing on repeated clicks when the market is closed.
    os.makedirs(CACHE_DIR, exist_ok=True)
    today_str = datetime.date.today().isoformat()
    cache_key = f"{ticker.replace('.', '_')}_{days}d"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cached = json.load(f)
            if cached.get("_cache_date") == today_str:
                # Remove internal cache metadata before returning
                cached.pop("_cache_date", None)
                return cached
        except Exception:
            pass  # Cache corrupted, proceed with fresh prediction
    
    try:
        # Fetch 2 years of data for training
        stock = yf.Ticker(ticker)
        df = stock.history(period="2y")
        
        if df.empty:
            return {"success": False, "error": f"No historical data for {ticker}"}
        
        # === INDIAN STOCK FIX ===
        # Forward-fill missing data (handles market holidays)
        df = df.ffill().dropna(subset=["Close", "Open", "High", "Low", "Volume"])
        
        # Compile features dataframe
        features_df = pd.DataFrame(index=df.index)
        
        # Keep Close temporarily for NaN alignment, will drop before ML prep
        features_df["Close"] = df["Close"]
        
        # Stationarity: Transform all absolute prices to relative percentages
        features_df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))
        features_df["Open_Ret"] = (df["Open"] - df["Close"].shift(1)) / df["Close"].shift(1)
        features_df["High_Ret"] = (df["High"] - df["Close"]) / df["Close"]
        features_df["Low_Ret"] = (df["Low"] - df["Close"]) / df["Close"]
        features_df["Volume_Chg"] = df["Volume"].pct_change()
        
        # === EXOGENOUS MACRO FETCH ===
        try:
            # Download broader market indicators for context
            macro_data = yf.download(["^GSPC", "^TNX", "^VIX"], period="2y", progress=False)["Close"]
            macro_data = macro_data.reindex(df.index, method="ffill")
            features_df["SP500_Ret"] = macro_data["^GSPC"].pct_change()
            features_df["TNX_Ret"] = macro_data["^TNX"].pct_change()
            features_df["VIX_Ret"] = macro_data["^VIX"].pct_change()
        except Exception as macro_err:
            print(f"Warning: Macro fetch failed: {macro_err}")
            features_df["SP500_Ret"] = 0.0
            features_df["TNX_Ret"] = 0.0
            features_df["VIX_Ret"] = 0.0

        # Incorporate Technical Indicators as Relative Distances
        close_prices = df["Close"].tolist()
        
        # Moving Averages (% distance from price)
        mas = ind_service.calculate_moving_averages(close_prices, windows=[20, 50])
        ma20_s = pd.Series(mas.get("MA20"), index=df.index)
        ma50_s = pd.Series(mas.get("MA50"), index=df.index)
        features_df["MA20_Dist"] = (df["Close"] - ma20_s) / ma20_s
        features_df["MA50_Dist"] = (df["Close"] - ma50_s) / ma50_s
        
        # RSI (Already stationary 0-100)
        features_df["RSI"] = ind_service.calculate_rsi(close_prices)
        
        # MACD (Scaled to percentage impact)
        macd = ind_service.calculate_macd(close_prices)
        macd_s = pd.Series(macd.get("MACD"), index=df.index)
        macd_sig_s = pd.Series(macd.get("MACD_Signal"), index=df.index)
        features_df["MACD"] = macd_s / df["Close"]
        features_df["MACD_Signal"] = macd_sig_s / df["Close"]
        
        # Bollinger Bands (% distance from price)
        bb = ind_service.calculate_bollinger_bands(close_prices)
        bb_upper_s = pd.Series(bb.get("BB_Upper"), index=df.index)
        bb_lower_s = pd.Series(bb.get("BB_Lower"), index=df.index)
        features_df["BB_Upper_Dist"] = (bb_upper_s - df["Close"]) / df["Close"]
        features_df["BB_Lower_Dist"] = (bb_lower_s - df["Close"]) / df["Close"]
        
        # Incorporate Live News Sentiment (per-ticker, real-time via yfinance)
        try:
            from backend.utils.sentiment import get_financial_sentiment
            
            live_news = stock.news  # yfinance fetches latest news for THIS ticker
            sentiment_by_date = {}
            if live_news:
                for article in live_news:
                    content = article.get("content", article)
                    title = content.get("title", "")
                    summary = content.get("summary", "")
                    pub_date_raw = content.get("pubDate", content.get("providerPublishTime", ""))
                    
                    if isinstance(pub_date_raw, (int, float)):
                        pub_date = datetime.datetime.fromtimestamp(pub_date_raw).strftime("%Y-%m-%d")
                    elif isinstance(pub_date_raw, str) and pub_date_raw:
                        pub_date = pub_date_raw.split("T")[0]
                    else:
                        continue
                    
                    # Score both title and summary for richer sentiment
                    text = f"{title}. {summary}" if summary else title
                    if text.strip():
                        score = get_financial_sentiment(text)
                        if pub_date in sentiment_by_date:
                            sentiment_by_date[pub_date].append(score)
                        else:
                            sentiment_by_date[pub_date] = [score]
            
            # Average scores per date
            avg_sentiment = {d: np.mean(scores) for d, scores in sentiment_by_date.items()}
            
            features_df["Sentiment_Score"] = [
                avg_sentiment.get(pd.Timestamp(d).strftime("%Y-%m-%d"), 0.0)
                for d in features_df.index
            ]
        except Exception as sent_err:
            print(f"Live sentiment integration skipped: {sent_err}")
            features_df["Sentiment_Score"] = 0.0
            
        # Drop rows with NaN values resulting from indicator and log return calculations
        features_df = features_df.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Detach raw prices for pure stationary ML
        close_series = features_df["Close"].copy()
        features_df = features_df.drop(columns=["Close"])
        
        if len(features_df) < LOOKBACK + days + 10:
            return {"success": False, "error": f"Insufficient data for {ticker}. Need more history after indicator padding."}
        
        num_features = len(features_df.columns)
        
        # Paths for caching
        model_path = os.path.join(MODEL_DIR, f"{ticker.replace('.', '_')}_lstm_multi.h5")
        scaler_path = os.path.join(MODEL_DIR, f"{ticker.replace('.', '_')}_scalers.pkl")
        
        # Load compiled h5 architecture
        model = load_trained_model(model_path)
        
        needs_retrain = (model is None or model.input_shape[2] != num_features or model.output_shape[1] != days)
        
        if not needs_retrain and os.path.exists(scaler_path):
            try:
                scalers = joblib.load(scaler_path)
                # INFERENCE MODE: Load exact training bounds to freeze dynamic output stability
                X, y, feature_scaler, target_scaler = _prepare_data(
                    features_df, LOOKBACK, days,
                    loaded_f_scaler=scalers["feature_scaler"], 
                    loaded_t_scaler=scalers["target_scaler"]
                )
            except Exception as e:
                print(f"Warning: unable to load scalers, falling back to retrain: {e}")
                needs_retrain = True
        else:
            needs_retrain = True
            
        if needs_retrain:
            # TRAINING MODE: Let it fit uniquely to this period's maximum bounds
            X, y, feature_scaler, target_scaler = _prepare_data(features_df, LOOKBACK, days)
            
            # Use 80% for training
            split = int(len(X) * 0.8)
            if split == 0:
                return {"success": False, "error": "Insufficient data to create a split."}
                
            X_train, y_train = X[:split], y[:split]
            X_test, y_test = X[split:], y[split:]
            
            model = tune_and_train_model(X_train, y_train, output_steps=days, fast_mode=True)
            try:
                save_model(model, model_path)
                joblib.dump({"feature_scaler": feature_scaler, "target_scaler": target_scaler}, scaler_path)
            except Exception as e:
                print(f"Warning: unable to save model/scaler cache: {e}")
        else:
            # Extract test slice for accuracy validation rendering
            split = int(len(X) * 0.8)
            X_test, y_test = X[split:], y[split:]
        
        # Test predictions (extract day-1 prediction for chart validation)
        if len(X_test) > 0:
            test_predictions = model.predict(X_test, verbose=0)
            test_pred_1day_returns = target_scaler.inverse_transform(test_predictions[:, 0].reshape(-1, 1)).flatten()
            actual_test_1day_returns = target_scaler.inverse_transform(y_test[:, 0].reshape(-1, 1)).flatten()
            
            # Reconstruct prices from returns
            # For test set, previous day price is at index (split + LOOKBACK - 1 + i)
            start_idx = split + LOOKBACK - 1
            last_known_test_prices = close_series.values[start_idx : start_idx + len(X_test)]
            test_pred_1day = last_known_test_prices * np.exp(test_pred_1day_returns)
            actual_test_1day = last_known_test_prices * np.exp(actual_test_1day_returns)
        else:
            test_pred_1day = np.array([])
            actual_test_1day = np.array([])
        
        # === Future Predictions ===
        # Use the last LOOKBACK days to predict the entire sequential future array
        last_sequence = feature_scaler.transform(features_df.iloc[-LOOKBACK:].values)
        last_sequence = last_sequence.reshape(1, LOOKBACK, num_features)
        
        future_seq = model.predict(last_sequence, verbose=0)
        future_returns = target_scaler.inverse_transform(future_seq.reshape(-1, 1)).flatten()
        
        # Reconstruct future prices using cumulative product of exp(returns)
        current_price = float(close_series.iloc[-1])
        future_predictions = []
        sim_price = current_price
        for ret in future_returns:
            sim_price = sim_price * np.exp(ret)
            future_predictions.append(sim_price)
        
        # Generate future dates (business days only)
        last_date = features_df.index[-1]
        future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=days)
        
        # Calculate trend metrics
        current_price = float(close_series.iloc[-1])
        predicted_final = float(future_predictions[-1])
        predicted_change = predicted_final - current_price
        predicted_change_pct = (predicted_change / current_price) * 100
        
        result = {
            "success": True,
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "predictions": {
                "dates": [d.strftime("%Y-%m-%d") for d in future_dates],
                "prices": [round(float(p), 2) for p in future_predictions],
            },
            "test_results": {
                "actual": [round(float(a), 2) for a in actual_test_1day.flatten()[-30:]] if len(actual_test_1day) > 0 else [],
                "predicted": [round(float(p), 2) for p in test_pred_1day.flatten()[-30:]] if len(test_pred_1day) > 0 else [],
            },
            "trend": {
                "predicted_final_price": round(predicted_final, 2),
                "change": round(predicted_change, 2),
                "change_pct": round(predicted_change_pct, 2),
                "direction": "up" if predicted_change > 0 else "down",
            },
        }
        
        # === Cache result for same-day stability ===
        try:
            cache_data = result.copy()
            cache_data["_cache_date"] = today_str
            with open(cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception:
            pass  # Non-critical: cache write failure doesn't affect prediction
        
        return result
    
    except Exception as e:
        return {"success": False, "error": str(e)}

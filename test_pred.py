import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.services.prediction_service import predict_prices
import yfinance as yf

# Run prediction twice
res1 = predict_prices("AAPL")
res2 = predict_prices("AAPL")

print("Prediction 1:", res1.get("trend", {}).get("predicted_final_price"))
print("Prediction 2:", res2.get("trend", {}).get("predicted_final_price"))

print("Prices 1:", res1.get("predictions", {}).get("prices")[:3])
print("Prices 2:", res2.get("predictions", {}).get("prices")[:3])

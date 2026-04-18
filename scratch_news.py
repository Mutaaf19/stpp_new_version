import yfinance as yf
import json

ticker = yf.Ticker("RELIANCE.NS")
with open("news_output.json", "w", encoding="utf-8") as f:
    json.dump(ticker.news, f, indent=4)

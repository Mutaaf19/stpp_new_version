"""
Stock Price Prediction System — Screener Service
Provides Screener-like features: Financial Ratios, Peer Comparison, Historical Financials.
All data sourced from yfinance.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from backend.utils.helpers import normalize_ticker


def fetch_financial_ratios(ticker: str) -> dict:
    """
    Fetch comprehensive financial ratios for a stock.
    Returns grouped ratios similar to Screener.in.
    """
    ticker = normalize_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        def _safe(key, fmt="number", multiplier=1):
            """Safely extract and format a value from info dict."""
            val = info.get(key)
            if val is None or val == "N/A":
                return None
            try:
                val = float(val) * multiplier
                if fmt == "percent":
                    return round(val * 100, 2)
                return round(val, 2)
            except (ValueError, TypeError):
                return None

        ratios = {
            "valuation": {
                "Trailing P/E": _safe("trailingPE"),
                "Forward P/E": _safe("forwardPE"),
                "Price to Book": _safe("priceToBook"),
                "PEG Ratio": _safe("pegRatio"),
                "EV / Revenue": _safe("enterpriseToRevenue"),
                "EV / EBITDA": _safe("enterpriseToEbitda"),
            },
            "profitability": {
                "Return on Equity (ROE)": _safe("returnOnEquity", "percent"),
                "Return on Assets (ROA)": _safe("returnOnAssets", "percent"),
                "Gross Margin": _safe("grossMargins", "percent"),
                "Operating Margin": _safe("operatingMargins", "percent"),
                "Profit Margin": _safe("profitMargins", "percent"),
            },
            "financial_health": {
                "Debt to Equity": _safe("debtToEquity"),
                "Current Ratio": _safe("currentRatio"),
                "Quick Ratio": _safe("quickRatio"),
            },
            "growth": {
                "Earnings Growth": _safe("earningsGrowth", "percent"),
                "Revenue Growth": _safe("revenueGrowth", "percent"),
            },
            "dividends": {
                "Dividend Yield": _safe("dividendYield", "percent"),
                "Payout Ratio": _safe("payoutRatio", "percent"),
            },
            "per_share": {
                "Book Value": _safe("bookValue"),
                "EPS (Trailing)": _safe("trailingEps"),
                "EPS (Forward)": _safe("forwardEps"),
            },
        }

        return {"success": True, "ticker": ticker, "ratios": ratios}

    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_peer_comparison(ticker: str) -> dict:
    """
    Fetch peer companies in the same industry and compare key metrics.
    Uses yfinance Industry class to discover peers.
    """
    ticker = normalize_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        industry_key = info.get("industryKey")
        industry_name = info.get("industry", "Unknown")

        if not industry_key:
            return {"success": False, "error": "Industry information not available for this stock."}

        # Get top companies in the same industry
        industry = yf.Industry(industry_key)
        top_companies_df = industry.top_companies

        if top_companies_df is None or top_companies_df.empty:
            return {"success": False, "error": "No peer companies found for this industry."}

        # Get up to 8 peer tickers
        peer_tickers = top_companies_df.index.tolist()[:8]

        # Fetch key metrics for each peer
        peers = []
        for pt in peer_tickers:
            try:
                peer_stock = yf.Ticker(pt)
                peer_info = peer_stock.info
                peers.append({
                    "ticker": pt,
                    "name": peer_info.get("shortName", pt),
                    "market_cap": peer_info.get("marketCap"),
                    "trailing_pe": _round_safe(peer_info.get("trailingPE")),
                    "price_to_book": _round_safe(peer_info.get("priceToBook")),
                    "roe": _pct_safe(peer_info.get("returnOnEquity")),
                    "debt_to_equity": _round_safe(peer_info.get("debtToEquity")),
                    "dividend_yield": _pct_safe(peer_info.get("dividendYield")),
                    "revenue_growth": _pct_safe(peer_info.get("revenueGrowth")),
                    "current_price": _round_safe(peer_info.get("regularMarketPrice", peer_info.get("currentPrice"))),
                })
            except Exception:
                continue

        # Also include the analyzed stock itself for comparison
        analyzed = {
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "market_cap": info.get("marketCap"),
            "trailing_pe": _round_safe(info.get("trailingPE")),
            "price_to_book": _round_safe(info.get("priceToBook")),
            "roe": _pct_safe(info.get("returnOnEquity")),
            "debt_to_equity": _round_safe(info.get("debtToEquity")),
            "dividend_yield": _pct_safe(info.get("dividendYield")),
            "revenue_growth": _pct_safe(info.get("revenueGrowth")),
            "current_price": _round_safe(info.get("regularMarketPrice", info.get("currentPrice"))),
        }

        return {
            "success": True,
            "ticker": ticker,
            "industry": industry_name,
            "analyzed_stock": analyzed,
            "peers": peers,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_historical_financials(ticker: str) -> dict:
    """
    Fetch historical financial statements: Quarterly Results, Annual P&L, Balance Sheet.
    """
    ticker = normalize_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)

        # --- Quarterly Results ---
        qf = stock.quarterly_financials
        quarterly = []
        if qf is not None and not qf.empty:
            for col in qf.columns[:5]:  # Last 5 quarters
                quarter_data = {
                    "period": col.strftime("%b %Y"),
                    "total_revenue": _fmt_crore(qf.loc["Total Revenue", col]) if "Total Revenue" in qf.index else None,
                    "operating_income": _fmt_crore(qf.loc["Operating Income", col]) if "Operating Income" in qf.index else None,
                    "net_income": _fmt_crore(qf.loc["Net Income", col]) if "Net Income" in qf.index else None,
                    "ebitda": _fmt_crore(qf.loc["EBITDA", col]) if "EBITDA" in qf.index else None,
                    "basic_eps": _round_safe(qf.loc["Basic EPS", col]) if "Basic EPS" in qf.index else None,
                    "diluted_eps": _round_safe(qf.loc["Diluted EPS", col]) if "Diluted EPS" in qf.index else None,
                }
                quarterly.append(quarter_data)

        # --- Annual Profit & Loss ---
        af = stock.financials
        annual_pl = []
        if af is not None and not af.empty:
            for col in af.columns[:4]:  # Last 4 years
                annual_data = {
                    "period": col.strftime("%b %Y"),
                    "total_revenue": _fmt_crore(af.loc["Total Revenue", col]) if "Total Revenue" in af.index else None,
                    "cost_of_revenue": _fmt_crore(af.loc["Cost Of Revenue", col]) if "Cost Of Revenue" in af.index else None,
                    "gross_profit": _fmt_crore(af.loc["Gross Profit", col]) if "Gross Profit" in af.index else None,
                    "operating_income": _fmt_crore(af.loc["Operating Income", col]) if "Operating Income" in af.index else None,
                    "net_income": _fmt_crore(af.loc["Net Income", col]) if "Net Income" in af.index else None,
                    "ebitda": _fmt_crore(af.loc["EBITDA", col]) if "EBITDA" in af.index else None,
                    "basic_eps": _round_safe(af.loc["Basic EPS", col]) if "Basic EPS" in af.index else None,
                }
                annual_pl.append(annual_data)

        # --- Balance Sheet ---
        bs = stock.balance_sheet
        balance_sheet = []
        if bs is not None and not bs.empty:
            for col in bs.columns[:4]:  # Last 4 years
                bs_data = {
                    "period": col.strftime("%b %Y"),
                    "total_assets": _fmt_crore(bs.loc["Total Assets", col]) if "Total Assets" in bs.index else None,
                    "total_debt": _fmt_crore(bs.loc["Total Debt", col]) if "Total Debt" in bs.index else None,
                    "stockholders_equity": _fmt_crore(bs.loc["Stockholders Equity", col]) if "Stockholders Equity" in bs.index else None,
                    "cash": _fmt_crore(bs.loc["Cash And Cash Equivalents", col]) if "Cash And Cash Equivalents" in bs.index else None,
                    "net_debt": _fmt_crore(bs.loc["Net Debt", col]) if "Net Debt" in bs.index else None,
                    "working_capital": _fmt_crore(bs.loc["Working Capital", col]) if "Working Capital" in bs.index else None,
                }
                balance_sheet.append(bs_data)

        return {
            "success": True,
            "ticker": ticker,
            "quarterly_results": quarterly,
            "annual_pl": annual_pl,
            "balance_sheet": balance_sheet,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Helper Functions ──

def _round_safe(val, decimals=2):
    """Safely round a value."""
    if val is None or val == "N/A":
        return None
    try:
        return round(float(val), decimals)
    except (ValueError, TypeError):
        return None


def _pct_safe(val):
    """Convert a decimal to percentage and round."""
    if val is None or val == "N/A":
        return None
    try:
        return round(float(val) * 100, 2)
    except (ValueError, TypeError):
        return None


def _fmt_crore(val):
    """Format large numbers into readable format (Cr for Indian, M/B for others)."""
    if val is None or val == "N/A":
        return None
    try:
        val = float(val)
        if abs(val) >= 1e9:
            return round(val / 1e9, 2)
        elif abs(val) >= 1e6:
            return round(val / 1e6, 2)
        else:
            return round(val, 2)
    except (ValueError, TypeError):
        return None

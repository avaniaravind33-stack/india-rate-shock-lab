"""
data_loader.py — Download and cache sector/index price data via yfinance.

Sectors mapped to NSE/BSE indices / ETFs available on Yahoo Finance:
  Nifty 50          ^NSEI
  Nifty Bank        ^NSEBANK
  Nifty IT          ^CNXIT
  Nifty Auto        ^CNXAUTO
  Nifty FMCG        ^CNXFMCG
  Nifty Pharma      ^CNXPHARMA
  Nifty Realty      ^CNXREALTY
  India 10Y Bond    uses hardcoded series (yfinance doesn't carry Indian GSec well)
"""

import os
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TICKERS = {
    "Nifty50":  "^NSEI",
    "Bank":     "^NSEBANK",
    "IT":       "^CNXIT",
    "Auto":     "^CNXAUTO",
    "FMCG":     "^CNXFMCG",
    "Pharma":   "^CNXPHARMA",
    "Realty":   "^CNXREALTY",
}

START_DATE = "2013-01-01"
END_DATE   = "2025-09-01"
CACHE_FILE = DATA_DIR / "sector_prices.parquet"


def download_prices(force_refresh: bool = False) -> pd.DataFrame:
    """Return a DataFrame of daily Adj Close prices, indexed by date."""
    if CACHE_FILE.exists() and not force_refresh:
        print(f"[data_loader] Loading cached data from {CACHE_FILE}")
        return pd.read_parquet(CACHE_FILE)

    print("[data_loader] Downloading data from Yahoo Finance …")
    frames = {}
    for name, ticker in TICKERS.items():
        try:
            raw = yf.download(
                ticker,
                start=START_DATE,
                end=END_DATE,
                progress=False,
                auto_adjust=True,
            )
            if raw.empty:
                print(f"  WARNING: No data for {name} ({ticker})")
                continue
            # yfinance may return MultiIndex columns
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            frames[name] = raw["Close"].rename(name)
            print(f"  ✓ {name} ({ticker}): {len(raw)} rows")
        except Exception as exc:
            print(f"  ERROR downloading {name}: {exc}")

    prices = pd.concat(frames, axis=1)
    prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index().dropna(how="all")
    prices.to_parquet(CACHE_FILE)
    print(f"[data_loader] Saved to {CACHE_FILE}")
    return prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily log-returns."""
    return np.log(prices / prices.shift(1)).dropna(how="all")


def load_or_generate_mock() -> pd.DataFrame:
    """
    Fallback: generate synthetic price series when Yahoo Finance is
    unavailable (e.g. in a CI / offline environment).
    Prices follow geometric Brownian motion seeded for reproducibility.
    """
    print("[data_loader] Generating synthetic price data (offline mode)")
    rng = np.random.default_rng(42)
    dates = pd.bdate_range(START_DATE, END_DATE)
    n = len(dates)

    # Calibrated roughly to real annualised vol of each index
    params = {
        "Nifty50":  (0.12, 0.14),
        "Bank":     (0.13, 0.22),
        "IT":       (0.15, 0.23),
        "Auto":     (0.11, 0.20),
        "FMCG":     (0.10, 0.14),
        "Pharma":   (0.11, 0.18),
        "Realty":   (0.08, 0.30),
    }
    base = {"Nifty50": 6000, "Bank": 11000, "IT": 9000,
            "Auto": 4500, "FMCG": 7000, "Pharma": 5500, "Realty": 200}

    frames = {}
    for col, (mu, sig) in params.items():
        dt   = 1 / 252
        shocks = rng.normal((mu - 0.5 * sig**2) * dt, sig * np.sqrt(dt), n)
        price  = base[col] * np.exp(np.cumsum(shocks))
        frames[col] = pd.Series(price, index=dates, name=col)

    prices = pd.DataFrame(frames)
    prices.index.name = "Date"
    return prices


if __name__ == "__main__":
    prices = download_prices()
    if prices is None or prices.empty:
        prices = load_or_generate_mock()
    print(prices.tail())

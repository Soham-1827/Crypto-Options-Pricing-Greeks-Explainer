import requests
import pandas as pd
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
DEFILLAMA_YIELD_URL = "https://yields.llama.fi/pools"

def fetch_current_price(coin_id):
    """Fetches current price of a coin from CoinGecko."""
    url = f"{COINGECKO_API_URL}/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data[coin_id]["usd"]
    except Exception as e:
        print(f"Error fetching price for {coin_id}: {e}")
        return None

def fetch_historical_data(coin_id, days=365):
    """Fetches historical price data for volatility calculation."""
    url = f"{COINGECKO_API_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print(f"Error fetching historical data for {coin_id}: {e}")
        return None

def fetch_risk_free_rate():
    """Fetches a proxy for risk-free rate using stablecoin yields from DefiLlama."""
    # Using a stablecoin pool (e.g., USDC on Aave) as a proxy
    try:
        response = requests.get(DEFILLAMA_YIELD_URL)
        response.raise_for_status()
        data = response.json()
        # Filter for a stable, high-TVL pool (e.g., Aave V3 USDC on Ethereum)
        # This is a simplification; in a real app, we might average top stable pools.
        # For now, let's look for a specific known pool or just take a median of top stablecoin pools.
        
        # Simplified: Just return a fixed 5% if API fails or for now, 
        # but let's try to find a real value.
        # Searching for "USDC" and "Aave"
        pools = data.get("data", [])
        usdc_pools = [p for p in pools if p["symbol"] == "USDC" and p["chain"] == "Ethereum" and p["project"] == "aave-v3"]
        
        if usdc_pools:
            # Take the one with highest TVL
            best_pool = max(usdc_pools, key=lambda x: x["tvlUsd"])
            return best_pool["apy"] / 100.0 # Convert percentage to decimal
        
        return 0.04 # Fallback 4%
    except Exception as e:
        print(f"Error fetching risk-free rate: {e}")
        return 0.04

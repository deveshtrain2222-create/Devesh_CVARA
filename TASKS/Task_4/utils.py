import requests
import pandas as pd
import numpy as np
# Fetch crypto price data from CoinGecko
def fetch_crypto_data(coin="bitcoin", days=90):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {
    "vs_currency": "usd",
    "days": days
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[["date", "price"]]
    return df
# Calculate volatility and Sharpe ratio
def calculate_metrics(df):
    df["returns"] = np.log(df["price"] / df["price"].shift(1))
    annualized_volatility = df["returns"].std() * np.sqrt(365)
    sharpe_ratio = (df["returns"].mean() / df["returns"].std()) *np.sqrt(365)
    return annualized_volatility, sharpe_ratio

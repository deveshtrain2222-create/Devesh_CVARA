import pandas as pd
import numpy as np

# -------------------------------
# CREATE DATES
# -------------------------------
dates = pd.date_range(start="2024-01-01", periods=15)

# -------------------------------
# CREATE DATA FOR EACH CRYPTO
# -------------------------------
records = []

cryptos = {
    "Bitcoin": 42000,
    "Ethereum": 2200,
    "Solana": 90
}

for crypto, base_price in cryptos.items():
    prices = base_price + np.random.randn(len(dates)) * base_price * 0.02

    for i in range(len(dates)):
        records.append({
            "Date": dates[i],
            "Crypto": crypto,
            "Close": round(prices[i], 2)
        })

# -------------------------------
# CREATE DATAFRAME
# -------------------------------
df = pd.DataFrame(records)

# -------------------------------
# CALCULATE RETURNS
# -------------------------------
df["Returns"] = df.groupby("Crypto")["Close"].pct_change()

# -------------------------------
# CALCULATE VOLATILITY (Rolling)
# -------------------------------
df["Volatility"] = (
    df.groupby("Crypto")["Returns"]
      .rolling(window=3)
      .std()
      .reset_index(level=0, drop=True)
)

# -------------------------------
# CALCULATE SHARPE RATIO
# -------------------------------
df["Sharpe_Ratio"] = df["Returns"] / df["Volatility"]

# -------------------------------
# CLEAN DATA
# -------------------------------
df.dropna(inplace=True)

# -------------------------------
# SAVE CSV
# -------------------------------
df.to_csv("crypto_processed.csv", index=False)

print("✅ crypto_processed.csv created successfully")
print(df.head())

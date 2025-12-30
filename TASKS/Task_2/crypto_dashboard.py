# crypto_dashboard.py
import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime

# -------------------------
# CONFIG: coins (8 total)
# -------------------------
coins = [
    "bitcoin", "ethereum", "solana", "cardano",
    "dogecoin", "litecoin", "ripple", "polkadot"
]

# -------------------------
# 1) LIVE PRICE FETCH (CoinGecko simple/price)
# -------------------------
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": ",".join(coins),
    "vs_currencies": "usd",
    "include_24hr_vol": "true",
    "include_24hr_change": "true"
}

resp = requests.get(url, params=params)
resp.raise_for_status()
data = resp.json()

# -------------------------
# Helper: nice number format for volume
# -------------------------
def fmt_volume_usd(v):
    try:
        v = float(v)
    except Exception:
        return str(v)
    if v >= 1_000_000_000:
        return f"${v/1_000_000_000:.2f}B"
    if v >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v/1_000:.2f}K"
    return f"${v:.2f}"

# -------------------------
# 2) BUILD DATAFRAME (with emoji for 24h change)
# -------------------------
rows = []
for coin in coins:
    info = data.get(coin, {})
    price = info.get("usd", None)
    change = info.get("usd_24h_change", None)
    volume = info.get("usd_24h_vol", None)

    # format change with emoji
    if change is None:
        change_str = "N/A"
    else:
        sign = "📈" if change >= 0 else "📉"
        change_str = f"{sign} {change:.2f}%"

    rows.append({
        "Cryptocurrency": coin.title(),
        "Price (USD)": f"${price:,.2f}" if price is not None else "N/A",
        "24h Change": change_str,
        "Volume (24h)": fmt_volume_usd(volume) if volume is not None else "N/A",
        # keep raw numeric columns for plotting
        "_price_num": price,
        "_change_num": change,
        "_volume_num": volume
    })

df = pd.DataFrame(rows)

# print header info
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("🔵 Crypto Data Fetcher (Live)")
print("Last updated:", last_updated)
print(df[["Cryptocurrency", "Price (USD)", "24h Change", "Volume (24h)"]])

# -------------------------
# 3) 7-day trend data for BTC + ETH (and separate SOL chart)
# -------------------------
hist_url = "https://api.coingecko.com/api/v3/coins/{}/market_chart"
trend = {}
for coin in ["bitcoin", "ethereum"]:
    r = requests.get(hist_url.format(coin), params={"vs_currency": "usd", "days": 7})
    r.raise_for_status()
    dd = r.json()
    # dd["prices"] is list of [timestamp, price]
    trend[coin] = [p[1] for p in dd["prices"]]

# SOL 7-day data (Task 3)
r_sol = requests.get(hist_url.format("solana"), params={"vs_currency": "usd", "days": 7})
r_sol.raise_for_status()
dd_sol = r_sol.json()
sol_prices = [p[1] for p in dd_sol["prices"]]
sol_times = [datetime.fromtimestamp(p[0] / 1000) for p in dd_sol["prices"]]

# -------------------------
# 4) Main 7-day Plot (BTC + ETH) with last updated in title (Task 4)
# -------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(
    y=trend["bitcoin"],
    mode="lines+markers",
    name="BTC"
))
fig.add_trace(go.Scatter(
    y=trend["ethereum"],
    mode="lines+markers",
    name="ETH"
))

fig.update_layout(
    title=f"7-Day Price Trend (BTC & ETH) — Last updated: {last_updated}",
    xaxis_title="Observation # (last 7 days)",
    yaxis_title="Price (USD)",
    template="plotly_dark",
    height=420
)

# show the BTC/ETH figure
fig.show()

# -------------------------
# 5) Separate SOL 7-day line chart (Task 3)
# -------------------------
fig_sol = go.Figure()
fig_sol.add_trace(go.Scatter(
    x=sol_times,
    y=sol_prices,
    mode="lines+markers",
    name="SOL"
))
fig_sol.update_layout(
    title=f"7-Day Price Trend — Solana (SOL) — Last updated: {last_updated}",
    xaxis_title="Datetime (UTC)",
    yaxis_title="Price (USD)",
    template="plotly_dark",
    height=420
)
fig_sol.show()

# -------------------------
# BONUS: Bar chart comparing 24h volume of all 8 coins
# -------------------------
# Use numeric values from df['_volume_num']
volumes = df[["_volume_num", "Cryptocurrency"]].copy()
volumes["_volume_num"] = volumes["_volume_num"].astype(float)
volumes = volumes.sort_values("_volume_num", ascending=False)

fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(
    x=volumes["Cryptocurrency"],
    y=volumes["_volume_num"],
    name="24h Volume (USD)"
))
fig_vol.update_layout(
    title=f"24h Volume Comparison (All coins) — Last updated: {last_updated}",
    xaxis_title="Cryptocurrency",
    yaxis_title="Volume (USD)",
    template="plotly_dark",
    height=460
)
fig_vol.show()

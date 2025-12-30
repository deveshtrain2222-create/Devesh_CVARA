from flask import Flask, render_template, jsonify, request
from datetime import datetime
import pandas as pd
import requests
import time
from threading import Lock

app = Flask(__name__)

# =====================================================
# CONFIG
# =====================================================
API_KEY = "CG-j36Jb6fjM7XXadA6CDJPLLAU"

COINS = [
    "bitcoin", "ethereum", "solana", "cardano", "dogecoin",
    "ripple", "litecoin", "polkadot", "tron", "chainlink"
]

VS_CURRENCY = "usd"

# =====================================================
# CACHE + RATE LIMIT CONTROL
# =====================================================
CACHE = {
    "market": {"data": [], "time": 0},
    "history": {}
}

CACHE_TTL_MARKET = 90        # seconds
CACHE_TTL_HISTORY = 300     # seconds

api_lock = Lock()

# =====================================================
# FETCH LIVE MARKET DATA (10 COINS)
# =====================================================
def get_crypto_data():
    now = time.time()

    # ✅ Serve cached market data
    if CACHE["market"]["data"] and now - CACHE["market"]["time"] < CACHE_TTL_MARKET:
        return CACHE["market"]["data"]

    with api_lock:
        if CACHE["market"]["data"] and now - CACHE["market"]["time"] < CACHE_TTL_MARKET:
            return CACHE["market"]["data"]

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": VS_CURRENCY,
            "ids": ",".join(COINS),
            "order": "market_cap_desc",
            "per_page": len(COINS),
            "page": 1,
            "price_change_percentage": "24h"
        }

        headers = {
            "Accept": "application/json",
            "x-cg-demo-api-key": API_KEY
        }

        try:
            res = requests.get(url, params=params, headers=headers, timeout=15)

            if res.status_code == 429:
                print("⚠️ Rate limit hit (market) → serving cached data")
                return CACHE["market"]["data"]

            res.raise_for_status()
            data = res.json()

            records = []
            for c in data:
                records.append({
                    "name": c["name"],
                    "current_price": c["current_price"],
                    "price_change_percentage_24h": round(
                        c.get("price_change_percentage_24h", 0), 2
                    ),
                    "total_volume": c["total_volume"]
                })

            CACHE["market"] = {"data": records, "time": now}
            pd.DataFrame(records).to_csv("data.csv", index=False)

            return records

        except Exception as e:
            print("API ERROR (markets):", e)
            return CACHE["market"]["data"]

# =====================================================
# 7-DAY MULTI-COIN HISTORY (ALL SELECTED COINS)
# =====================================================
@app.route("/api/history")
def history():
    coin_param = request.args.get("coins")
    if not coin_param:
        return jsonify({"dates": [], "prices": {}})

    coins = coin_param.split(",")
    now = time.time()

    dates = []
    prices = {}

    for coin in coins:
        # ✅ Serve cached history
        if coin in CACHE["history"] and now - CACHE["history"][coin]["time"] < CACHE_TTL_HISTORY:
            prices[coin] = CACHE["history"][coin]["prices"]
            dates = CACHE["history"][coin]["dates"]
            continue

        try:
            res = requests.get(
                f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart",
                params={"vs_currency": VS_CURRENCY, "days": 7},
                headers={"x-cg-demo-api-key": API_KEY},
                timeout=15
            )

            if res.status_code == 429:
                print(f"⚠️ Rate limit hit (history) → {coin}")
                prices[coin] = CACHE["history"].get(coin, {}).get("prices", [])
                continue

            res.raise_for_status()
            raw = res.json().get("prices", [])

            dates = [
                datetime.fromtimestamp(p[0] / 1000).strftime("%d %b")
                for p in raw
            ]
            prices[coin] = [round(p[1], 2) for p in raw]

            CACHE["history"][coin] = {
                "dates": dates,
                "prices": prices[coin],
                "time": now
            }

        except Exception as e:
            print(f"History API error for {coin}:", e)
            prices[coin] = CACHE["history"].get(coin, {}).get("prices", [])

    return jsonify({"dates": dates, "prices": prices})

# =====================================================
# ROUTES
# =====================================================
@app.route("/")
def index():
    return render_template("Base.html", crypto_data=get_crypto_data())

@app.route("/milestone1")
def milestone1():
    return render_template("milestone1.html", crypto_data=get_crypto_data())
@app.route("/mil4")
def mil4():
    return render_template("mil4.html", crypto_data=get_crypto_data())    

@app.route("/api/crypto")
def refresh():
    return jsonify(get_crypto_data())

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)

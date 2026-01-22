from flask import Flask, render_template, jsonify, request, send_file
import requests
import pandas as pd
import numpy as np
import os


import time
from datetime import datetime



from mil3_dash import init_dash as init_dash_m3
from mil4_dash import init_dash as init_dash_m4



from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

from threading import Lock

from db import get_db
from db import create_tables

if not os.path.exists("crypto.db"):
    create_tables()


app = Flask(__name__)

#🟢 QUICK MEMORY TRICK

# Imports → CONFIG → Constants → Cache → Functions → Routes → app.run

# =====================================================
# CONFIG
# =====================================================
API_KEY = "CG-j36Jb6fjM7XXadA6CDJPLLAU"

COINS = [
    "bitcoin", "ethereum", "solana", "cardano", "dogecoin",
    "ripple", "litecoin", "polkadot", "tron", "chainlink"
]
SYMBOL_MAP = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "cardano": "ADA",
    "dogecoin": "DOGE",
    "ripple": "XRP",
    "litecoin": "LTC",
    "polkadot": "DOT",
    "tron": "TRX",
    "chainlink": "LINK"
}


VS_CURRENCY = "usd"

RISK_FREE_RATE = 0.04   # 4% yearly (used in Sharpe ratio)
TRADING_DAYS = 365
# DATA_DIR = "data"
# os.makedirs(DATA_DIR, exist_ok=True)


# =====================================================
# CACHE + RATE LIMIT CONTROL
# =====================================================
CACHE = {
    "market": {"data": [], "time": 0},
    "history": {},
    "risk": {"data": {}, "time": 0}
}




CACHE_TTL_MARKET = 90        # seconds-1.5 minutes
CACHE_TTL_HISTORY = 300     # seconds-5 minutes
CACHE_TTL_RISK = 300  # 5 minutes

api_lock = Lock()



# ---------------- MILESTONE 1 ----------------
# Generate & save historical price CSV (365 days base data)


@app.route("/api/crypto")
def get_crypto_data():
    records = []

    for coin in COINS[:10]:
        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": VS_CURRENCY,
                    "ids": coin,
                    "price_change_percentage": "24h"
                },
                headers={"x-cg-demo-api-key": API_KEY},
                timeout=10
            )
            data = r.json()[0]

            records.append({
                "id": data["id"],                # 👈 REQUIRED
                "name": data["name"],
                "symbol": data["symbol"],
                "current_price": data["current_price"],
                "price_change_percentage_24h": round(
                    data.get("price_change_percentage_24h", 0), 2
                ),
                "total_volume": data["total_volume"]
            })

        except:
            continue

    return jsonify(records)


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

            # ✅ TAKE 1 DATA POINT PER DAY (EVERY 24 HOURS)
            daily_prices = raw[::24][:7]

            
            dates = [f"Day{i+1}" for i in range(len(daily_prices))]

            prices[coin] = [round(p[1], 2) for p in daily_prices]
            


            CACHE["history"][coin] = {
                "dates": dates,
                "prices": prices[coin],
                "time": now
            }

        except Exception as e:
            print(f"History API error for {coin}:", e)
            prices[coin] = CACHE["history"].get(coin, {}).get("prices", [])

    return jsonify({"dates": dates, "prices": prices})
# ---------------- MILESTONE 1 ---------------- 
# Generate & save historical price CSV (365 days base data) 
# def generate_history_csv(coin, days):
#     url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
#     file_path = os.path.join(DATA_DIR, f"milestone1_{coin}_history.csv")

#     # 🛑 prevent re-fetch
#     if os.path.exists(file_path):
#         return True
         
#     params = {"vs_currency": "usd", "days": days} 
#     r = requests.get(
#                 url,
#                 params=params,
#                 headers={"x-cg-demo-api-key": API_KEY},
#                 timeout=15
#             )
 
#     if r.status_code != 200: return False
#     raw = r.json().get("prices", []) 
#     if not raw: return False 
#     df = pd.DataFrame(raw, columns=["time", "price"])
#     df["date"] = pd.to_datetime(df["time"], unit="ms") 
#     df = df[["date", "price"]]
#     df["coin"] = coin 
#     file_path = os.path.join(DATA_DIR, f"milestone1_{coin}_history.csv")
#     df.to_csv(file_path, index=False)
#     return True






def save_price_history(conn, coin, days=365):
    cur = conn.cursor()

    # coin master
    cur.execute("SELECT coin_id FROM coins WHERE coin_name=?", (coin,))
    row = cur.fetchone()

    if not row:
        cur.execute(
            "INSERT INTO coins (coin_name, symbol) VALUES (?,?)",
            (coin, coin[:3].upper())
        )
        coin_id = cur.lastrowid
    else:
        coin_id = row[0]

    r = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart",
        params={"vs_currency": "usd", "days": days},
        headers={"x-cg-demo-api-key": API_KEY},
        timeout=15
    )

    prices = r.json().get("prices", [])

    for p in prices:
        date = datetime.fromtimestamp(p[0]/1000).strftime("%Y-%m-%d")
        price = p[1]

        cur.execute("""
        SELECT 1 FROM price_history
        WHERE coin_id=? AND date=?
        """, (coin_id, date))

        if not cur.fetchone():
            cur.execute("""
            INSERT INTO price_history (coin_id, date, price)
            VALUES (?,?,?)
            """, (coin_id, date, price))



def init_database_data():
    conn = get_db()
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    for coin in COINS:
        save_price_history(conn, coin, days=365)

    conn.commit()
    conn.close()




# ---------------- MILESTONE 2 ----------------
# Load Milestone 1 data + apply day filter

# def load_milestone1_data(coin, days):
#     file_path = os.path.join(DATA_DIR, f"milestone1_{coin}_history.csv")

#     # Auto-generate if missing
#     if not os.path.exists(file_path):
#         generate_history_csv(coin, days=365)

#     df = pd.read_csv(file_path)
#     df["date"] = pd.to_datetime(df["date"])

#     # Apply 30 / 90 / 365 days logic
#     df = df.sort_values("date").tail(days)

#     df["returns"] = df["price"].pct_change()
#     return df.dropna()




def load_price_from_db(coin, days):
    from db import get_db
    
    conn = get_db()
    q = """
    SELECT date, price FROM price_history
    WHERE coin_id = (
        SELECT coin_id FROM coins WHERE coin_name=?
    )
    ORDER BY date DESC
    LIMIT ?
    """
    df = pd.read_sql(q, conn, params=(coin, days))
    conn.close()

    df["returns"] = df["price"].pct_change()
    return df.dropna()





@app.route("/api/risk-metrics")
def risk_metrics():
    try:
        days = int(request.args.get("days", 30))
        if days not in [30, 90, 365]:
            days = 30
    except:
        days = 30

    now = time.time()
    if days in CACHE["risk"]["data"] and now - CACHE["risk"]["time"] < CACHE_TTL_RISK:
        return jsonify(CACHE["risk"]["data"][days])
    btc_df = load_price_from_db("bitcoin", days)
    btc_returns = btc_df["returns"]

    metrics = {
        "labels": [],
        "volatility": [],
        "sharpe": [],
        "beta": [],
        "var": []
    }

    table = []

    for coin in COINS:
        # df = load_milestone1_data(coin, days)
        df = load_price_from_db(coin, days)
        if df.empty:
            continue

        returns = df["returns"]

        volatility = returns.std() * np.sqrt(365) * 100
        sharpe = (
            (returns.mean() * 365 - RISK_FREE_RATE) /
            (returns.std() * np.sqrt(365))
        ) if returns.std() else 0
         # ✅ BETA CALCULATION
        beta = (
            np.cov(returns, btc_returns)[0][1] /
            np.var(btc_returns)
        ) if np.var(btc_returns) else 0
        var95 = abs(np.percentile(returns, 5)) * 100

        symbol = SYMBOL_MAP.get(coin, coin.upper())


        metrics["labels"].append(symbol)
        metrics["volatility"].append(round(volatility, 2))
        metrics["sharpe"].append(round(sharpe, 2))
        metrics["beta"].append(round(beta,2))
        metrics["var"].append(round(var95, 2))

        table.append({
            "coin": symbol,
            "volatility": round(volatility, 2),
            "sharpe": round(sharpe, 2),
            "beta": round(beta,2),
            "var": round(var95, 2)
        })
    # ✅ PAYLOAD HERE
    payload = {
    "metrics": metrics,
    "table": table
    }
    CACHE["risk"]["data"][days] = payload
    CACHE["risk"]["time"] = now


    return jsonify(payload)




@app.route("/dashboard-metrics")
def dashboard_metrics():
    start = time.time()

    # Simulate or calculate metrics
    metrics = {
        "visualization": 4,    # number of graphs
        "ui": 8,               # UI quality score
        "interactivity": 3,    # dropdown + date picker + hover
        "risk": 3,             # volatility, returns, risk-return
        "performance": round(10 - (time.time() - start)*5, 1)
    }

    return jsonify(metrics)





# =====================================================
# ROUTES
# =====================================================
@app.route("/")
def index():
    return render_template("Base.html", )

# @app.route("/milestone1")
# def milestone1():
#     missing = []

#     for coin in COINS:
#         file_path = os.path.join(DATA_DIR, f"milestone1_{coin}_history.csv")

#         # ⚡ already exists → skip API
#         if not os.path.exists(file_path):
#             generate_history_csv(coin, days=365)
#             missing.append(coin)

#     print("Generated for:", missing)
#     return render_template("milestone1.html")


@app.route("/milestone1")
def milestone1():
    return render_template("milestone1.html")



@app.route("/milestone2")
def milestone2():
    return render_template("milestone2.html" )  

@app.route("/milestone3")
def milestone3():
    # Dash will render here
    return render_template("milestone3.html")

@app.route("/milestone4")
def milestone4():
    return render_template("milestone4.html")


# @app.route("/api/refresh-data")
# def refresh_data():
    
#     status = {}

#     for coin in COINS:
#         success = generate_history_csv(coin, days=365)
#         status[coin] = "ok" if success else "failed"

#     return jsonify(status)

def init_database_data():
    conn = get_db()
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    for coin in COINS:
        save_price_history(conn, coin, days=365)

    conn.commit()
    conn.close()





# ---------- INIT DASH ----------
  
init_dash_m3(app)   # url: /dash3/
init_dash_m4(app)   # url: /dash4/

# 🔥 CALL IT ONCE
init_database_data()


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
   app.run(debug=True)


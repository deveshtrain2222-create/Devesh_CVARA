import sqlite3
from datetime import datetime

DB_PATH = "database/cvara.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS coins (
        coin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin_name TEXT UNIQUE,
        symbol TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin_id INTEGER,
        date TEXT,
        price REAL,
        FOREIGN KEY (coin_id) REFERENCES coins(coin_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS risk_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin_id INTEGER,
        days INTEGER,
        volatility REAL,
        sharpe REAL,
        beta REAL,
        var REAL,
        risk_level TEXT,
        calculated_at TEXT
    )
    """)

    conn.commit()
    conn.close()

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "cvara.db")

def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    # COINS MASTER
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coins (
        coin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin_name TEXT UNIQUE,
        symbol TEXT
    )
    """)

    # PRICE HISTORY
    cur.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin_id INTEGER,
        date TEXT,
        price REAL,
        FOREIGN KEY (coin_id) REFERENCES coins (coin_id)
    )
    """)

    conn.commit()
    conn.close()

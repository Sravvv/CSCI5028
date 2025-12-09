import requests
from datetime import datetime
import components.database as db
from components.env import get_env

COINS = get_env("COINS", as_list=True)
CURRENCY = get_env("CURRENCY")

def fetch_current_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": CURRENCY,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_historical_prices(coin, days=1):
    url = url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {
        "vs_currency": CURRENCY,
        "days": days,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["prices"]  

def save_price(coin, price, timestamp=None):
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    if timestamp:
        cursor.execute(
            "INSERT INTO prices (coin, price, timestamp) VALUES (?, ?, ?)",
            (coin, price, timestamp),
        )
    else:
        cursor.execute(
            "INSERT INTO prices (coin, price) VALUES (?, ?)",
            (coin, price),
        )
    print(f"Stored {coin} price: {price} at {timestamp}")
    conn.commit()

def backfill(target_hours=24):

    print(f"Backfilling history for {target_hours}h")

    for coin in COINS:
        print(f"Fetching history for {coin}")

        history = fetch_historical_prices(coin, days=1)

        for timestamp_ms, price in history:
            ts = datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
            save_price(coin, price, ts)

        print(f"Stored {len(history)} historical points for {coin} in the database")
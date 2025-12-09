import components.database as db

import numpy as np
from datetime import datetime, timedelta

def load_prices(coin, limit=50):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT price, timestamp
        FROM prices
        WHERE coin = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (coin, limit))
    rows = cursor.fetchall()
    conn.close()

    prices = [r[0] for r in rows][::-1]
    timestamps_raw = [r[1] for r in rows][::-1]

    formatted_timestamps = []
    for ts in timestamps_raw:
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            formatted_timestamps.append(dt.strftime("%b %d, %I:%M %p"))
        except:
            formatted_timestamps.append(ts)

    return prices, formatted_timestamps

def percent_change(prices):
    if len(prices) < 2:
        return 0
        
    first = prices[0]
    last = prices[-1]
    
    return ((last - first) / first) * 100

def volatility(prices):
    if len(prices) < 2:
        return 0
    return float(np.std(prices))

def count_recent_data(hours=24):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM prices
        WHERE timestamp >= datetime('now', ?)
    """, (f"-{hours} hours",))
    count = cursor.fetchone()[0]
    conn.close()
    return count
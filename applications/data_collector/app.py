import time
import requests
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


from components.database import get_connection
from components.analyzer import count_recent_data
from components.collector import fetch_current_prices, save_price, backfill
from components.env import get_env

COLLECTION_INTERVAL = int(get_env("COLLECTION_INTERVAL"))

def run_collector(interval_seconds=COLLECTION_INTERVAL, target_hours=24):
    print("Collector service started.")
    existing = count_recent_data(target_hours)

    # if missing data, backfill
    if existing == 0:
      print("No recent data found, backfilling")
      backfill(target_hours)
      print("Backfilling complete")
    else:
      print("Recent data found, skipping backfill")
    
    currency = get_env("CURRENCY").lower()
    collection_count = 0
    while True:
        print("\n Running data collection cycle")
        prices = fetch_current_prices()
        for coin, price_data in prices.items():
            price_value = price_data[currency]
            save_price(coin, price_value)
        collection_count += 1
        print(f"Collection count: {collection_count}")
        print("Waiting for next collection cycle")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    run_collector()
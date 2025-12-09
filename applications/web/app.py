from flask import Flask, jsonify, render_template
import requests
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from components.analyzer import load_prices, percent_change, volatility
from components.env import get_env

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))
URL = get_env("ANALYZER_URL")

@app.route("/")
def home():
    coins = get_env("COINS", as_list=True)
    
    if not coins:
        return render_template("index.html", coins=[], coin_data={})
    
    coin_data = {coin: {} for coin in coins}
    analyzer_url_base = f"{URL}/crypto-stats"
    
    for coin in coins:
        try:
            response = requests.get(f"{analyzer_url_base}?coin={coin}", timeout=5)
            if response.status_code == 200:
                coin_data[coin] = response.json()
            else:
                print(f"Error fetching data for {coin} from analyzer service")
        except:
            print(f"Error fetching data for {coin} from analyzer service")

    return render_template("index.html", coins=coins, coin_data=coin_data)

@app.route("/api/prices/<coin>")
def api_prices(coin):
    prices, timestamps = load_prices(coin)
    return jsonify({
        "prices": prices,
        "timestamps": timestamps,
        "percent_change": percent_change(prices),
        "volatility": volatility(prices),
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
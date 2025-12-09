from fastapi import FastAPI, Query
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from components.analyzer import load_prices, percent_change, volatility
import uvicorn
from components.env import get_env


PORT = int(get_env("ANALYZER_PORT", "8001"))
HOST = get_env("ANALYZER_HOST", "127.0.0.1")

app = FastAPI(
    title="Crypto Analyzer Service",
    description="Independent service that computes crypto metrics",
    version="1.0.0",
)
app.request_count = 0

@app.get("/crypto-stats")
def get_metrics(
    coin: str = Query(..., description="Coin name: bitcoin, ethereum, solana"),
    limit: int = Query(50, description="How many latest entries to analyze")
):
    prices, timestamps = load_prices(coin, limit)
    app.request_count += 1
    print(f"Requests served: {app.request_count}")
    return {
        "coin": coin,
        "data_points": len(prices),
        "prices": prices,
        "timestamps": timestamps,
        "percent_change": percent_change(prices),
        "volatility": volatility(prices)
    }

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=False)
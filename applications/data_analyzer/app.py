from fastapi import FastAPI, Query
from components.analyzer import load_prices, percent_change, volatility
import uvicorn
from components.env import get_env

PORT = int(get_env("ANALYZER_PORT"))
URL = get_env("ANALYZER_URL")

app = FastAPI(
    title="Crypto Analyzer Service",
    description="Independent service that computes crypto metrics",
    version="1.0.0",
    request_count = 0
)

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
    uvicorn.run(app, host=URL, port=PORT, reload=False)
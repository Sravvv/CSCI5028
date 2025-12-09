import sqlite3
import pytest

from components.collector import save_price


@pytest.fixture
def mock_price_payload():
    return {
        "bitcoin": {"usd": 42000.75},
        "ethereum": {"usd": 3100.50},
        "solana": {"usd": 150.25}
    }


@pytest.fixture
def temp_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    import components.database
    monkeypatch.setattr(
        components.database, "get_connection",
        lambda: conn
    )

    return conn


def test_price_parsing_and_db_write(mock_price_payload, temp_db):
    parsed_prices = {coin: payload["usd"] for coin, payload in mock_price_payload.items()}

    for coin, price in parsed_prices.items():
        save_price(coin, price)

    cursor = temp_db.cursor()
    cursor.execute("SELECT coin, price FROM prices ORDER BY coin ASC")
    rows = cursor.fetchall()

    assert len(rows) == len(parsed_prices), "All price records should be inserted"

    for coin, price in parsed_prices.items():
        cursor.execute("SELECT price FROM prices WHERE coin = ?", (coin,))
        row = cursor.fetchone()
        assert row is not None, f"Expected entry for coin {coin}"
        assert row[0] == price, f"Price mismatch for {coin}"
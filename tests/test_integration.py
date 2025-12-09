import sqlite3
import pytest
from fastapi.testclient import TestClient

from applications.data_analyzer.app import app
from components.database import get_connection


@pytest.fixture
def setup_test_db(monkeypatch):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
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
        components.database,
        "get_connection",
        lambda: conn
    )

    return conn


def test_analyzer_endpoint_computes_percent_change(setup_test_db):
    conn = setup_test_db
    cur = conn.cursor()

    data = [
        ("bitcoin", 100.0, "2025-01-01 00:00:00"),
        ("bitcoin", 110.0, "2025-01-02 00:00:00")
    ]

    cur.executemany("INSERT INTO prices (coin, price, timestamp) VALUES (?, ?, ?)", data)
    conn.commit()

    client = TestClient(app)

    response = client.get("/crypto-stats?coin=bitcoin")
    assert response.status_code == 200

    payload = response.json()

    assert "percent_change" in payload, "Analyzer must return percent change"
    assert round(payload["percent_change"], 2) == 10.00, "Percent change should equal 10%"
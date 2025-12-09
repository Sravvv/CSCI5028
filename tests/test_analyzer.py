import pytest
from components.analyzer import percent_change, volatility


@pytest.fixture
def mock_price_series():
    return [100, 120, 140]


def test_percent_change_positive(mock_price_series):
    result = percent_change(mock_price_series)
    assert round(result, 2) == 40.00, "Percent change should be 40%"


@pytest.fixture
def flat_price_series():
    return [50, 50, 50]


def test_volatility_zero(flat_price_series):
    result = volatility(flat_price_series)
    assert result == 0, "Volatility should be zero"
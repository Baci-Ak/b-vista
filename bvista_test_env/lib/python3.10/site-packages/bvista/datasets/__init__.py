"""
bvista.datasets
===============

Built-in and live datasets for testing and exploration.

Available:
- ames_housing: Real estate dataset with 80+ features.
- titanic: Classic survival dataset from Kaggle.
- covid19_live: Live COVID-19 data from API Ninjas (requires API key).
- stock_prices: Live stock price data from Alpha Vantage (requires API key).
- energy_price: Live energy price data from U.S. EIA (requires API key).

Usage:
    from bvista.datasets import ames_housing, covid19_live, stock_prices, test

    # Load COVID data
    df = covid19_live.load(country="Nigeria", API_KEY="your_key")

    # Load stock prices
    df = stock_prices.load(symbol="AAPL", interval="daily", API_KEY="your_key")
"""

from . import ames_housing
from . import titanic
from . import covid19_live
from . import stock_prices
from . import testing_data


__all__ = ["ames_housing", "titanic", "covid19_live", "stock_prices", "testing_data"]

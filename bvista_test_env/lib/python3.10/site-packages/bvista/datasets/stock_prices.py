import os
import requests
import pandas as pd

def load(symbol=None, interval="daily", outputsize="compact", date=None, API_KEY=None):
    """
    Load live stock market prices from Alpha Vantage.

    Parameters:
        symbol (str | list): Required. Ticker symbol (e.g., 'AAPL') or list of symbols.
        interval (str): One of 'daily', 'weekly', or 'monthly'.
        outputsize (str): 'compact' (last 100 points) or 'full'.
        date (str | list): Optional. Year (e.g., '2022') or range ['YYYY-MM-DD', 'YYYY-MM-DD'].
        API_KEY (str): Required. Alpha Vantage API key.

    Returns:
        pd.DataFrame: Stock price data for one or more symbols.
    """
    if not symbol:
        raise ValueError("❌ 'symbol' is required (e.g., 'AAPL' or ['AAPL', 'MSFT']).")

    API_KEY = API_KEY or os.getenv("ALPHAVANTAGE_API_KEY")
    if not API_KEY:
        raise ValueError("❌ Missing API_KEY. Provide it directly or set 'ALPHAVANTAGE_API_KEY' in your environment.")

    function_map = {
        "daily": "TIME_SERIES_DAILY",
        "weekly": "TIME_SERIES_WEEKLY",
        "monthly": "TIME_SERIES_MONTHLY"
    }

    if interval not in function_map:
        raise ValueError("❌ Invalid interval. Use 'daily', 'weekly', or 'monthly'.")

    symbols = symbol if isinstance(symbol, list) else [symbol]
    all_dfs = []

    for sym in symbols:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": function_map[interval],
            "symbol": sym,
            "outputsize": outputsize,
            "apikey": API_KEY
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch {sym}: {response.status_code} - {response.text}")
            continue

        data = response.json()
        time_series_key = [k for k in data.keys() if "Time Series" in k]
        if not time_series_key:
            print(f"⚠️ No data found for {sym}. Response: {data}")
            continue

        series = data[time_series_key[0]]
        df = pd.DataFrame(series).T
        df.index.name = "date"
        df.columns = [col.split('. ')[1] for col in df.columns]
        df = df.astype(float).sort_index()
        df["symbol"] = sym.upper()

        # Filter by date
        if date:
            if isinstance(date, str) and len(date) == 4:
                df = df[df.index.str.startswith(date)]
            elif isinstance(date, list) and len(date) == 2:
                df = df[(df.index >= date[0]) & (df.index <= date[1])]

        all_dfs.append(df)

    if not all_dfs:
        print("⚠️ No data returned for any of the requested symbols.")
        return pd.DataFrame()

    return pd.concat(all_dfs).reset_index()

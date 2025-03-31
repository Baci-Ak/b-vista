---

### 📈 `stock_prices`: Live Stock Market Data

The `stock_prices` dataset allows you to fetch **live historical stock market prices** from [Alpha Vantage](https://www.alphavantage.co/). It's designed for real-time data science, financial modeling, and machine learning pipelines.

---

### ⚙️ Parameters

```python
stock_prices.load(
    symbol=None,            # str | list[str]: Ticker(s) e.g. 'AAPL' or ['AAPL', 'TSLA']
    interval="daily",       # str: 'daily', 'weekly', or 'monthly'
    outputsize="compact",   # str: 'compact' (100 data points) or 'full'
    date=None,              # str or list: year (e.g. '2022') or ['YYYY-MM-DD', 'YYYY-MM-DD']
    API_KEY=None            # str: Alpha Vantage API Key
)
```

---

### 🚀 Examples

#### ➤ Load a single stock (latest 100 daily records)
```python
from bvista.datasets import stock_prices

df = stock_prices.load(symbol="AAPL", API_KEY="YOUR_API_KEY")
print(df.head())
```

#### ➤ Load multiple stocks for a specific year
```python
df = stock_prices.load(
    symbol=["AAPL", "TSLA", "MSFT"],
    date="2023",
    interval="daily",
    outputsize="full",
    API_KEY="YOUR_API_KEY"
)
```

#### ➤ Load weekly data over a custom date range
```python
df = stock_prices.load(
    symbol="GOOG",
    interval="weekly",
    date=["2021-01-01", "2022-12-31"],
    API_KEY="YOUR_API_KEY"
)
```

---

### 📄 Output Format

| date       | open   | high   | low    | close  | volume   | symbol |
|------------|--------|--------|--------|--------|----------|--------|
| 2023-01-03 | 130.22 | 133.41 | 129.89 | 131.01 | 98120000 | AAPL   |
| 2023-01-04 | 131.01 | 134.25 | 130.00 | 132.55 | 104960000| AAPL   |
| ...        | ...    | ...    | ...    | ...    | ...      | TSLA   |

> Note: All values are `float`, and `symbol` is included for multi-stock requests.

---

### 📌 Notes

- 💡 Use `date="YYYY"` to filter by year, or a date range like `["2023-01-01", "2023-06-30"]`.
- 📉 You can set `interval="monthly"` to get long-term trends.
- ⚠️ If a symbol fails, a warning is printed, and others will still load.

---

### 🔐 API Key Setup

This dataset requires a free [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key).

You can pass it directly:

```python
stock_prices.load(symbol="AAPL", API_KEY="YOUR_KEY")
```

Or set it as an environment variable:
```bash
export ALPHAVANTAGE_API_KEY=YOUR_KEY
```

---
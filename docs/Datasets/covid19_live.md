---

## 🦠 `covid19_live`: Live COVID-19 Case Data (Powered by API Ninjas)

The `covid19_live` dataset fetches **up-to-date COVID-19 case data** by country (and optionally region) using the [API Ninjas COVID-19 API](https://api-ninjas.com/api/covid19). It's part of the `bvista.datasets` module and gives you a clean, pandas-friendly DataFrame.



---

### 🔑 API Key Required

To use this dataset, you need an **API key** from [API Ninjas](https://api-ninjas.com/register).

Once you get it, you can provide it in **two ways**:

#### ✅ Option 1: Pass it directly

```python
df = covid19_live.load(country="Us", API_KEY="your_api_key")
```

#### ✅ Option 2: Set it as an environment variable

```bash
export API_NINJAS_API_KEY="your_api_key"
```

Then just:

```python
df = covid19_live.load(country="Us")
```

---

### 🚀 Quick Start

```python
from bvista.datasets import covid19_live

df = covid19_live.load(
    country="Us",          # Required
    date="2023",           # Optional: "YYYY" or "YYYY-MM-DD"
    region=None,           # Optional: e.g. "Western Cape"
    API_KEY="your_api_key" # Optional if set via env
)

df.head()
```

---

### 📘 Parameters

| Parameter  | Type        | Description                                                                 |
|------------|-------------|-----------------------------------------------------------------------------|
| `country`  | `str`       | **Required.** Country name, e.g., `"Canada"`, `"US"`, `"South Africa"`      |
| `date`     | `str/int`   | Optional. `"YYYY"` or `"YYYY-MM-DD"` to filter results                     |
| `region`   | `str`       | Optional. Filters data by region/subdivision if available (e.g., `"Gauteng"`) |
| `API_KEY`  | `str`       | Optional if set as env var. Your [API Ninjas](https://api-ninjas.com) key  |

---

### 📊 Output Format

Returns a clean `pandas.DataFrame` with the following columns:

| Column     | Type    | Description                        |
|------------|---------|------------------------------------|
| `country`  | string  | Country name                       |
| `region`   | string  | Region (if applicable)             |
| `date`     | string  | Date in `YYYY-MM-DD` format        |
| `total`    | int     | Cumulative confirmed cases         |
| `new`      | int     | New cases reported on that date    |

---

### 🧠 Example: Filter by Region and Year

```python
df = covid19_live.load(
    country="South Africa",
    region="Western Cape",
    date="2022",
    API_KEY="your_api_key"
)
```

---

### ⚠️ Common Errors & Troubleshooting

- `❌ API Error: 400 - {"error": "Invalid parameters"}`  
  → You likely passed an unsupported country or incorrect date format.

- `❌ 'country' is required`  
  → You must always pass the `country` parameter — the API does **not** support continent-level queries (e.g., "Africa").

- `⚠️ No data found for the given parameters.`  
  → There’s no match for your filter. Try removing `region` or adjusting `date`.

---

### 🛡️ Best Practices

- Always pass a **specific country** — the API doesn't support "Africa", "Europe", etc.
- If you're unsure what regions are available, fetch data with `region=None` and inspect the `region` column.
- Cache results locally if you’re querying the same data frequently (to avoid API limits).

---

### 🤝 Credits

This dataset wrapper uses live data from:

**🔗 [API Ninjas COVID-19 API](https://api-ninjas.com/api/covid19)**  
Free API for real-time COVID-19 data.

---

### ❤️ Contributing

If you spot issues or want to improve the dataset loader (e.g., add caching, multi-country support, etc), feel free to open a PR or issue on the repo!

---
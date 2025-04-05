import os
import requests
import pandas as pd

def load(country=None, date=None, region=None, API_KEY=None):
    if not country:
        raise ValueError("❌ 'country' is required because the API does not support region-wide queries (e.g., Africa).")

    API_URL = 'https://api.api-ninjas.com/v1/covid19'
    API_KEY = API_KEY or os.getenv("API_NINJAS_API_KEY")
    if not API_KEY:
        raise ValueError("❌ Missing API_KEY. Provide via parameter or set 'API_NINJAS_API_KEY' env variable.")

    headers = {'X-Api-Key': API_KEY}
    params = {"country": country}

    if isinstance(date, (str, int)):
        params["date"] = str(date)

    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"❌ API Error: {response.status_code} - {response.text}")

    raw_data = response.json()
    flattened_rows = []

    for entry in raw_data:
        # Region filter happens here (after API call)
        if region and region.lower() not in entry.get("region", "").lower():
            continue

        base = {
            "country": entry.get("country"),
            "region": entry.get("region"),
        }

        cases_dict = entry.get("cases", {})
        for day, stats in cases_dict.items():
            flattened_rows.append({
                **base,
                "date": day,
                "total": stats.get("total"),
                "new": stats.get("new"),
            })

    df = pd.DataFrame(flattened_rows)

    if df.empty:
        print("⚠️ No data found for the given parameters.")
        return df

    if date and len(str(date)) == 4:
        df = df[df["date"].str.startswith(str(date))]

    return df

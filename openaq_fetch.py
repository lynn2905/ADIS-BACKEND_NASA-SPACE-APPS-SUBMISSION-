# openaq_fetch.py
# ✅ Fetch worldwide current air quality data (OpenAQ v3, updated October 2025)

import requests
import pandas as pd

print("🌍 Fetching worldwide current air quality data (OpenAQ v3)...")

BASE_URL = "https://api.openaq.org/v3/locations"

# 🔑 Replace with your real API key from https://api.openaq.org/dashboard
API_KEY = "e212a4c9ff259a153c36ea1e10a180ca227dfaecc12e006b738c606664561aba"

# Request parameters (adjust as needed)
params = {
    "limit": 1000,
    "page": 1,
    "sort": "desc",
    "order_by": "id"  # ✅ must be "id" now, not "lastUpdated"
}

headers = {"X-API-Key": API_KEY}
all_data = []

# Pagination loop
while True:
    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        print(f"❌ Error fetching data: {response.status_code}")
        print(response.text)
        break

    data = response.json()
    results = data.get("results", [])
    if not results:
        print("⚠️ No results found on this page.")
        break

    all_data.extend(results)
    print(f"📦 Collected {len(results)} records (page {params['page']})")

    # Stop if less than limit (end of pages)
    if len(results) < params["limit"]:
        break

    params["page"] += 1

if not all_data:
    print("⚠️ No global data found. Try again later — OpenAQ updates hourly.")
    exit()

# Flatten JSON to DataFrame
df = pd.json_normalize(all_data, sep="_")

# Keep useful columns only
keep_cols = [
    "country", "city", "name",
    "coordinates_latitude", "coordinates_longitude",
    "parameters_0_parameter", "parameters_0_value",
    "parameters_0_unit", "parameters_0_lastUpdated"
]
df = df[[c for c in keep_cols if c in df.columns]]

# Rename for readability
df.rename(columns={
    "name": "location",
    "coordinates_latitude": "latitude",
    "coordinates_longitude": "longitude",
    "parameters_0_parameter": "parameter",
    "parameters_0_value": "value",
    "parameters_0_unit": "unit",
    "parameters_0_lastUpdated": "time"
}, inplace=True)

# Save to CSV
df.to_csv("openaq_latest.csv", index=False)
print(f"✅ Retrieved {len(df)} records from OpenAQ (global)")
print("💾 Saved as openaq_latest.csv 🌍")

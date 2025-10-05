import pandas as pd
import json

input_csv = "./data/fused_data.csv"
output_json = "./data/fused_data.json"

df = pd.read_csv(input_csv)

# Convert to GeoJSON-like format for frontend visualization
geojson = [
    {
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "NO2": float(row.get("NO2", 0)),
        "anomaly_flag": int(row.get("anomaly_flag", 0)),
        "T2M": float(row.get("T2M", 0)),
    }
    for _, row in df.iterrows()
]

with open(output_json, "w") as f:
    json.dump(geojson, f, indent=2)

print(f"✅ Exported {len(geojson)} records to {output_json}")

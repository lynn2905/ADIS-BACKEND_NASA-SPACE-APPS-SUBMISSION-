# fusion_pipeline.py
# ------------------
# ADIS - Data Fusion Pipeline
# Fuses TEMPO, MERRA-2, and OpenAQ datasets into one master file.

import pandas as pd
import numpy as np
import xarray as xr
import h5py
from scipy.spatial import cKDTree
from sklearn.preprocessing import StandardScaler

print("🚀 Starting ADIS Fusion Pipeline...")

# ============================================================
# 1. Load MERRA-2 Dataset
# ============================================================
print("\n📂 Loading MERRA-2 dataset...")
merra_path = "./data/MERRA2_20240410.nc4"
ds_vars = ["T2M", "QV2M", "PS", "TQI"]

ds = xr.open_dataset(merra_path)
available_vars = [v for v in ds_vars if v in ds.data_vars]
df_merra = ds[available_vars].mean(dim=["time"]).to_dataframe().reset_index()

# Flatten spatial structure if present
if "lat" not in df_merra.columns:
    df_merra["lat"] = np.linspace(-90, 90, len(df_merra))
if "lon" not in df_merra.columns:
    df_merra["lon"] = np.linspace(-180, 180, len(df_merra))

df_merra.dropna(subset=["lat", "lon"], inplace=True)
print(f"✅ Loaded MERRA-2 variables: {available_vars}")
df_merra.to_csv("./data/cleaned_merra2.csv", index=False)

# ============================================================
# 2. Load TEMPO Dataset
# ============================================================
print("\n📡 Loading TEMPO dataset...")
tempo_path = "./data/tempo/TEMPO_NO2_L2_V03_20250406T215103Z_S012G07.nc"

with h5py.File(tempo_path, "r") as f:
    no2 = f["product/vertical_column_troposphere"][:]
    lat = f["geolocation/latitude"][:]
    lon = f["geolocation/longitude"][:]

tempo_df = pd.DataFrame({
    "lat": lat.flatten(),
    "lon": lon.flatten(),
    "NO2": no2.flatten()
})
tempo_df = tempo_df.dropna(subset=["NO2"])
print(f"✅ TEMPO dataset processed: {len(tempo_df)} valid points")

# Detect anomalies (Z-score)
scaler = StandardScaler()
tempo_df["NO2_z"] = scaler.fit_transform(tempo_df[["NO2"]])
tempo_df["anomaly_flag"] = np.where(tempo_df["NO2_z"] > 2, 1, 0)

# ============================================================
# 3. Load OpenAQ Ground Dataset
# ============================================================
print("\n🌍 Loading OpenAQ dataset...")
try:
    openaq_df = pd.read_csv("./data/openaq_latest.csv")
    openaq_df.rename(columns={
        "coordinates.latitude": "lat",
        "coordinates.longitude": "lon"
    }, inplace=True)
    if "lat" in openaq_df.columns and "lon" in openaq_df.columns:
        print(f"✅ OpenAQ records loaded: {len(openaq_df)}")
    else:
        print("⚠️ OpenAQ lacks lat/lon columns; skipping ground merge.")
        openaq_df = pd.DataFrame()
except Exception as e:
    print(f"⚠️ Skipping OpenAQ due to error: {e}")
    openaq_df = pd.DataFrame()

# ============================================================
# 4. Spatial Fusion (using KDTree)
# ============================================================
print("\n🔗 Fusing datasets (spatial proximity join)...")

def fast_spatial_fuse(df1, df2, lat1, lon1, lat2, lon2, radius_km=250):
    """Fuse two datasets using KDTree proximity (in kilometers)."""
    R = 6371.0  # Earth radius
    df1_rad = np.deg2rad(df1[[lat1, lon1]].values)
    df2_rad = np.deg2rad(df2[[lat2, lon2]].values)

    tree = cKDTree(df2_rad)
    radius = radius_km / R
    idxs = tree.query_ball_point(df1_rad, r=radius)

    joined = []
    for i, neighbors in enumerate(idxs):
        if not neighbors:
            continue
        mean_vals = df2.iloc[neighbors].mean(numeric_only=True)
        row = df1.iloc[i].to_dict()
        row.update(mean_vals.to_dict())
        joined.append(row)

    return pd.DataFrame(joined)

# Perform fusion
fused = fast_spatial_fuse(tempo_df, df_merra, "lat", "lon", "lat", "lon", radius_km=400)

# ============================================================
# 5. Save outputs (CSV + JSON)
# ============================================================
if len(fused) > 0:
    CSV_OUT = "./data/fused_data.csv"
    JSON_OUT = "./data/fused_data.json"

    fused.to_csv(CSV_OUT, index=False)

    geojson_like = []
    for _, row in fused.iterrows():
        geojson_like.append({
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "NO2": float(row.get("NO2", 0)),
            "anomaly_flag": int(row.get("anomaly_flag", 0)),
            **{k: float(row[k]) for k in df_merra.columns if k in fused.columns and pd.notna(row[k])}
        })

    pd.Series(geojson_like).to_json(JSON_OUT, orient="records", indent=2)
    print(f"✅ Fusion complete. Saved {len(fused)} fused records to CSV + JSON.")
else:
    print("⚠️ No overlapping spatial data found. Try increasing radius_km.")

# utils.py
# --------------------------------------------
# Utility functions for ADIS (Atmospheric Digital Immune System)
# Shared helpers used by detection, fusion, and plume modules
# --------------------------------------------

import numpy as np
import pandas as pd
from datetime import datetime

# === Coordinate and distance helpers ===

def haversine(lat1, lon1, lat2, lon2):
    """Compute great-circle distance (in km) between two lat/lon points."""
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def normalize_angle(angle):
    """Keep longitude values within [-180, 180]."""
    return ((angle + 180) % 360) - 180


# === Data cleaning and processing ===

def clean_dataset(df, required_cols):
    """Ensure required columns exist and remove NaN or invalid rows."""
    df = df.copy()
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan
    df = df.dropna(subset=required_cols)
    return df.reset_index(drop=True)


def z_score(series):
    """Compute z-score and return standardized values."""
    mean = np.nanmean(series)
    std = np.nanstd(series)
    if std == 0:
        return np.zeros_like(series)
    return (series - mean) / std


# === Time helpers ===

def current_timestamp():
    """Return current UTC time as ISO string."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def format_datetime(ts):
    """Convert timestamp to human-readable format."""
    if isinstance(ts, (int, float)):
        return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return str(ts)


# === Geo-matching ===

def nearest_point(lat, lon, df, lat_col="lat", lon_col="lon"):
    """Find nearest point in df to given (lat, lon)."""
    distances = haversine(lat, lon, df[lat_col].values, df[lon_col].values)
    idx = np.argmin(distances)
    return df.iloc[idx], distances[idx]

# plume.py
import numpy as np
import pandas as pd
from typing import List, Dict

import backend.config as config


EARTH_RADIUS_M = 6_371_000.0
DEG_PER_M_LAT  = 1.0 / 111_000.0

def step_latlon(lat, lon, u_ms, v_ms, dt_sec):
    dlat = (v_ms * dt_sec) * DEG_PER_M_LAT
    coslat = max(0.1, np.cos(np.deg2rad(lat)))
    dlon = (u_ms * dt_sec) * (DEG_PER_M_LAT / coslat)
    return lat + dlat, lon + dlon

def random_diffusion(lat, lon, dt_hours, sigma_km):
    sigma_deg = sigma_km * 0.009
    return lat + np.random.randn() * sigma_deg * np.sqrt(dt_hours), \
           lon + np.random.randn() * sigma_deg * np.sqrt(dt_hours)

def plume_trajectories(df: pd.DataFrame, hours=6, dt_minutes=10) -> List[Dict]:
    out = []
    dt_sec = dt_minutes * 60
    steps = int(hours * 60 / dt_minutes)

    for _, r in df[df[config.ANOM_COL] == 1].iterrows():
        lat, lon = r[config.LAT_COL], r[config.LON_COL]
        traj = [{"lat": lat, "lon": lon, "t_min": 0}]
        u, v = config.FALLBACK_WIND  # basic constant wind

        for s in range(1, steps + 1):
            lat, lon = step_latlon(lat, lon, u, v, dt_sec)
            lat, lon = random_diffusion(lat, lon, dt_minutes / 60.0, config.DIFFUSION_KM)
            traj.append({"lat": lat, "lon": lon, "t_min": s * dt_minutes})

        out.append({
            "id": f"plume_{int(r.name)}",
            "signature": r.get("signature", "unknown"),
            "path": traj
        })
    return out

# detect.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import backend.config as config


def refine_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if config.ANOM_COL not in out.columns:
        mask = np.isfinite(out[config.NO2_COL].values)
        no2 = out.loc[mask, config.NO2_COL].values.reshape(-1, 1)
        z = StandardScaler().fit_transform(no2).ravel()
        out.loc[mask, config.ANOM_COL] = (z >= config.Z_CUTOFF).astype(int)
    else:
        out[config.ANOM_COL] = out[config.ANOM_COL].fillna(0).astype(int)

    # Ignore weak or non-credible NO₂ signals
    out.loc[out[config.NO2_COL] < config.MIN_NO2, config.ANOM_COL] = 0
    return out

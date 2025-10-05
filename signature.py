# signature.py
import pandas as pd
import backend.config as config


def classify_signature(row: pd.Series) -> str:
    no2 = row.get(config.NO2_COL, 0)
    t2m = row.get(config.T2M_COL, None)
    qv  = row.get(config.QV2M_COL, None)
    ps  = row.get(config.PS_COL, None)

    if no2 >= 2e16 and t2m and t2m > 300:
        return "wildfire/biomass (hot & high NO₂)"
    if no2 >= 2e16 and ps and ps > 101500:
        return "industrial/urban plume"
    if no2 >= 1e16 and qv and qv > 0.012:
        return "stagnant/humid accumulation"
    if no2 >= 1e16:
        return "traffic/urban"
    return "background"

def attach_signatures(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["signature"] = df.apply(classify_signature, axis=1)
    return out

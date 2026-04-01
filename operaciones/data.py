from pathlib import Path

import pandas as pd

WEEK_COLS_METRICS = [f"L{i}W_ROLL" for i in range(8, -1, -1)]
WEEK_COLS_ORDERS = [f"L{i}W" for i in range(8, -1, -1)]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def metrics_path() -> Path:
    return project_root() / "docs" / "RAW_INPUT_METRICS.csv"


def orders_path() -> Path:
    return project_root() / "docs" / "RAW_ORDERS.csv"


def load_metrics() -> pd.DataFrame:
    df = pd.read_csv(metrics_path())
    for c in ["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "ZONE_PRIORITIZATION", "METRIC"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df


def load_orders() -> pd.DataFrame:
    df = pd.read_csv(orders_path())
    for c in ["COUNTRY", "CITY", "ZONE", "METRIC"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df


def inner_zone_keys(metrics: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    m = metrics[["COUNTRY", "CITY", "ZONE"]].drop_duplicates()
    o = orders[["COUNTRY", "CITY", "ZONE"]].drop_duplicates()
    return m.merge(o, on=["COUNTRY", "CITY", "ZONE"], how="inner")

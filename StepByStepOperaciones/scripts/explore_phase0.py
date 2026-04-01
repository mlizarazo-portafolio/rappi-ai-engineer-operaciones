"""
Fase 0 — Exploración de RAW_INPUT_METRICS y RAW_ORDERS.
Ejecutar desde la raíz del repo: python StepByStepOperaciones/scripts/explore_phase0.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
METRICS_PATH = DOCS / "RAW_INPUT_METRICS.csv"
ORDERS_PATH = DOCS / "RAW_ORDERS.csv"

WEEK_COLS_METRICS = [f"L{i}W_ROLL" for i in range(8, -1, -1)]
WEEK_COLS_ORDERS = [f"L{i}W" for i in range(8, -1, -1)]


def main() -> None:
    metrics = pd.read_csv(METRICS_PATH)
    orders = pd.read_csv(ORDERS_PATH)

    print("=== RAW_INPUT_METRICS ===")
    print(f"Filas: {len(metrics):,}")
    print(f"Columnas: {list(metrics.columns)}")
    print(f"Países (COUNTRY): {sorted(metrics['COUNTRY'].dropna().unique().tolist())}")
    print(f"N ciudades únicas: {metrics['CITY'].nunique()}")
    print(f"N zonas únicas (COUNTRY,CITY,ZONE): {metrics.groupby(['COUNTRY', 'CITY', 'ZONE']).ngroups}")
    print(f"ZONE_TYPE: {sorted(metrics['ZONE_TYPE'].dropna().unique().tolist())}")
    print(f"ZONE_PRIORITIZATION: {sorted(metrics['ZONE_PRIORITIZATION'].dropna().unique().tolist())}")
    print(f"N métricas distintas (METRIC): {metrics['METRIC'].nunique()}")
    print("\nMétricas (METRIC):")
    for m in sorted(metrics["METRIC"].dropna().unique()):
        print(f"  - {m}")

    print("\n=== RAW_ORDERS ===")
    print(f"Filas: {len(orders):,}")
    print(f"Columnas: {list(orders.columns)}")
    print(f"Países: {sorted(orders['COUNTRY'].dropna().unique().tolist())}")
    print(f"N zonas únicas (COUNTRY,CITY,ZONE): {orders.groupby(['COUNTRY', 'CITY', 'ZONE']).ngroups}")

    # Join keys
    m_keys = metrics[["COUNTRY", "CITY", "ZONE"]].drop_duplicates()
    o_keys = orders[["COUNTRY", "CITY", "ZONE"]].drop_duplicates()
    merged = o_keys.merge(m_keys, on=["COUNTRY", "CITY", "ZONE"], how="outer", indicator=True)
    only_orders = merged[merged["_merge"] == "left_only"]
    only_metrics = merged[merged["_merge"] == "right_only"]
    both = merged[merged["_merge"] == "both"]

    print("\n=== JOIN COUNTRY, CITY, ZONE ===")
    print(f"Claves solo en órdenes (sin fila de métricas agregada por zona): {len(only_orders)}")
    print(f"Claves solo en métricas (sin fila de órdenes): {len(only_metrics)}")
    print(f"Claves en ambos: {len(both)}")

    if len(only_orders) > 0:
        print("\nEjemplo claves solo órdenes (hasta 5):")
        print(only_orders.head().to_string(index=False))
    if len(only_metrics) > 0:
        print(f"\n... {len(only_metrics)} zonas con métricas pero sin fila en RAW_ORDERS (esperable: muchas zonas métricas vs top órdenes)")

    # Chapinero check for brief example
    chap = metrics[
        metrics["ZONE"].astype(str).str.contains("Chapinero", case=False, na=False)
    ]
    print("\n=== Zonas que contienen 'Chapinero' (métricas) ===")
    print(chap[["COUNTRY", "CITY", "ZONE"]].drop_duplicates().to_string(index=False) if len(chap) else "(ninguna)")

    # Nulls in week columns sample
    print("\n=== Valores nulos en semanas (métricas, % por columna) ===")
    for c in WEEK_COLS_METRICS:
        pct = 100 * metrics[c].isna().mean()
        print(f"  {c}: {pct:.2f}%")

    print("\n=== Valores nulos en semanas (órdenes) ===")
    for c in WEEK_COLS_ORDERS:
        pct = 100 * orders[c].isna().mean()
        print(f"  {c}: {pct:.2f}%")


if __name__ == "__main__":
    main()

"""Fusionar varios CSV de scrape (mismo esquema) priorizando filas con precio."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from competitive_intel.paths import default_scrape_csv
from competitive_intel.scrapers.schema import CSV_COLUMNS


def merge_scrape_csvs(paths: list[Path], output: Path | None = None) -> Path:
    """
    Por cada triple (platform, address_id, product_name) conserva una fila:
    prioridad a `item_price_mxn` no nulo; si empate, la `scraped_at` más reciente.
    """
    if not paths:
        raise ValueError("Se necesita al menos un CSV.")
    dfs = []
    for p in paths:
        p = p.resolve()
        if not p.is_file():
            raise FileNotFoundError(p)
        dfs.append(pd.read_csv(p, encoding="utf-8"))
    df = pd.concat(dfs, ignore_index=True)

    for col in CSV_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df["_has_price"] = df["item_price_mxn"].notna().astype(int)
    df["_ts"] = pd.to_datetime(df["scraped_at"], errors="coerce", utc=True)
    df = df.sort_values(
        ["platform", "address_id", "product_name", "_has_price", "_ts"],
        ascending=[True, True, True, False, False],
    )
    df = df.drop_duplicates(subset=["platform", "address_id", "product_name"], keep="first")
    df = df.drop(columns=["_has_price", "_ts"])
    df = df[CSV_COLUMNS]

    out = output or default_scrape_csv()
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    return out


def main_merge(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Fusiona CSVs de scrape (prioriza filas con precio)")
    p.add_argument("inputs", nargs="+", type=Path, help="CSV a fusionar (orden: se prioriza precio sobre todo)")
    p.add_argument("-o", "--output", type=Path, default=None, help="Salida (default: scrape_latest.csv)")
    args = p.parse_args(argv)
    try:
        out = merge_scrape_csvs(list(args.inputs), args.output)
        print(f"CSV fusionado: {out}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main_merge())

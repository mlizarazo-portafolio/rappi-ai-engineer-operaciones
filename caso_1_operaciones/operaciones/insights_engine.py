"""
Reglas de insights automáticos (Fase 2) — solo pandas, datos reales.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from operaciones.data import WEEK_COLS_METRICS, WEEK_COLS_ORDERS, inner_zone_keys, load_metrics, load_orders

# Métricas donde valores más altos suelen ser mejores (tendencia “preocupante” = cae 3 semanas seguidas)
METRICS_HIGHER_IS_BETTER = [
    "Lead Penetration",
    "Perfect Orders",
    "Gross Profit UE",
    "Non-Pro PTC > OP",
    "Pro Adoption (Last Week Status)",
]

KEY_METRIC_BENCHMARK = "Gross Profit UE"


@dataclass
class InsightsBundle:
    anomalies_metrics: pd.DataFrame
    anomalies_orders: pd.DataFrame
    trends: pd.DataFrame
    benchmarking: pd.DataFrame
    correlation: dict[str, Any]
    opportunities: pd.DataFrame


def _pct_change_l0_l1(row: pd.Series, l0: str, l1: str) -> float:
    a, b = row.get(l0), row.get(l1)
    if pd.isna(a) or pd.isna(b) or b == 0:
        return float("nan")
    return (a - b) / abs(b) * 100.0


def compute_anomalies_metrics(metrics: pd.DataFrame, threshold_pct: float = 10.0, top_n: int = 25) -> pd.DataFrame:
    """|Δ%| semana a semana L1→L0 por zona y métrica."""
    rows = []
    for _, r in metrics.iterrows():
        ch = _pct_change_l0_l1(r, "L0W_ROLL", "L1W_ROLL")
        if pd.isna(ch) or abs(ch) < threshold_pct:
            continue
        rows.append(
            {
                "COUNTRY": r["COUNTRY"],
                "CITY": r["CITY"],
                "ZONE": r["ZONE"],
                "ZONE_TYPE": r.get("ZONE_TYPE"),
                "METRIC": r["METRIC"],
                "L1W_ROLL": r["L1W_ROLL"],
                "L0W_ROLL": r["L0W_ROLL"],
                "pct_change_L1_to_L0": ch,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["abs_change"] = out["pct_change_L1_to_L0"].abs()
    return out.sort_values("abs_change", ascending=False).head(top_n).drop(columns=["abs_change"])


def compute_anomalies_orders(orders: pd.DataFrame, threshold_pct: float = 10.0, top_n: int = 20) -> pd.DataFrame:
    rows = []
    for _, r in orders.iterrows():
        ch = _pct_change_l0_l1(r, "L0W", "L1W")
        if pd.isna(ch) or abs(ch) < threshold_pct:
            continue
        rows.append(
            {
                "COUNTRY": r["COUNTRY"],
                "CITY": r["CITY"],
                "ZONE": r["ZONE"],
                "L1W": r["L1W"],
                "L0W": r["L0W"],
                "pct_change_L1_to_L0": ch,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["abs_change"] = out["pct_change_L1_to_L0"].abs()
    return out.sort_values("abs_change", ascending=False).head(top_n).drop(columns=["abs_change"])


def compute_trends_three_weeks(metrics: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Deterioro 3 semanas seguidas (L0 < L1 < L2) en métricas 'higher is better'.
    """
    rows = []
    sub = metrics[metrics["METRIC"].isin(METRICS_HIGHER_IS_BETTER)]
    for _, r in sub.iterrows():
        v0, v1, v2 = r.get("L0W_ROLL"), r.get("L1W_ROLL"), r.get("L2W_ROLL")
        if pd.isna(v0) or pd.isna(v1) or pd.isna(v2):
            continue
        if v0 < v1 < v2:
            rows.append(
                {
                    "COUNTRY": r["COUNTRY"],
                    "CITY": r["CITY"],
                    "ZONE": r["ZONE"],
                    "ZONE_TYPE": r.get("ZONE_TYPE"),
                    "METRIC": r["METRIC"],
                    "L2W_ROLL": v2,
                    "L1W_ROLL": v1,
                    "L0W_ROLL": v0,
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    # Priorizar caída total L2→L0
    out["drop_L2_to_L0"] = out["L2W_ROLL"] - out["L0W_ROLL"]
    return out.sort_values("drop_L2_to_L0", ascending=False).head(top_n).drop(columns=["drop_L2_to_L0"])


def compute_benchmarking(metrics: pd.DataFrame, metric_name: str = KEY_METRIC_BENCHMARK, top_pairs: int = 15) -> pd.DataFrame:
    """
    Dentro de cada (COUNTRY, ZONE_TYPE), par de zonas con mayor brecha en L0W_ROLL.
    """
    sub = metrics[metrics["METRIC"] == metric_name].dropna(subset=["L0W_ROLL"])
    if sub.empty:
        return pd.DataFrame()

    pairs = []
    for (country, zt), g in sub.groupby(["COUNTRY", "ZONE_TYPE"]):
        if len(g) < 2:
            continue
        g = g.sort_values("L0W_ROLL", ascending=False)
        best = g.iloc[0]
        worst = g.iloc[-1]
        spread = float(best["L0W_ROLL"] - worst["L0W_ROLL"])
        if spread <= 0:
            continue
        pairs.append(
            {
                "COUNTRY": country,
                "ZONE_TYPE": zt,
                "metric": metric_name,
                "high_zone": best["ZONE"],
                "high_city": best["CITY"],
                "high_value": best["L0W_ROLL"],
                "low_zone": worst["ZONE"],
                "low_city": worst["CITY"],
                "low_value": worst["L0W_ROLL"],
                "spread": spread,
            }
        )
    out = pd.DataFrame(pairs)
    if out.empty:
        return out
    return out.sort_values("spread", ascending=False).head(top_pairs)


def compute_correlation_lead_nonpro(metrics: pd.DataFrame) -> dict[str, Any]:
    """Correlación Spearman a nivel zona (advertencia: no implica causalidad)."""
    a = metrics[metrics["METRIC"] == "Lead Penetration"][["COUNTRY", "CITY", "ZONE", "L0W_ROLL"]].rename(
        columns={"L0W_ROLL": "lead"}
    )
    b = metrics[metrics["METRIC"] == "Non-Pro PTC > OP"][["COUNTRY", "CITY", "ZONE", "L0W_ROLL"]].rename(
        columns={"L0W_ROLL": "nonpro_cvr"}
    )
    m = a.merge(b, on=["COUNTRY", "CITY", "ZONE"], how="inner").dropna()
    if len(m) < 30:
        return {"n": len(m), "spearman": float("nan"), "note": "muestra pequeña"}
    rho = m[["lead", "nonpro_cvr"]].corr(method="spearman").iloc[0, 1]
    return {
        "n": len(m),
        "spearman": float(rho),
        "note": "Correlación observacional entre Lead Penetration y Non-Pro PTC > OP (L0W_ROLL); no implica causalidad.",
    }


def compute_opportunities(metrics: pd.DataFrame, orders: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Zonas priorizadas estratégicamente con volumen de órdenes alto y margen o calidad mejorable.
    """
    keys = inner_zone_keys(metrics, orders)
    pri = metrics[
        metrics["ZONE_PRIORITIZATION"].isin(["High Priority", "Prioritized"])
    ][["COUNTRY", "CITY", "ZONE"]].drop_duplicates()

    o = orders[["COUNTRY", "CITY", "ZONE", "L0W"]].dropna(subset=["L0W"])
    o = o.merge(keys, on=["COUNTRY", "CITY", "ZONE"], how="inner")
    o = o.merge(pri, on=["COUNTRY", "CITY", "ZONE"], how="inner")

    if o.empty:
        return pd.DataFrame()

    gp = metrics[metrics["METRIC"] == "Gross Profit UE"][["COUNTRY", "CITY", "ZONE", "L0W_ROLL"]].rename(
        columns={"L0W_ROLL": "gp_ue"}
    )
    po = metrics[metrics["METRIC"] == "Perfect Orders"][["COUNTRY", "CITY", "ZONE", "L0W_ROLL"]].rename(
        columns={"L0W_ROLL": "perfect_orders"}
    )
    x = o.merge(gp, on=["COUNTRY", "CITY", "ZONE"], how="left").merge(po, on=["COUNTRY", "CITY", "ZONE"], how="left")

    # Por país: órdenes altas (P75) y (GP bajo P40 o Perfect bajo P40)
    rows = []
    for country, g in x.groupby("COUNTRY"):
        if len(g) < 5:
            continue
        thr_o = g["L0W"].quantile(0.75)
        thr_gp = g["gp_ue"].quantile(0.40) if g["gp_ue"].notna().any() else None
        thr_po = g["perfect_orders"].quantile(0.40) if g["perfect_orders"].notna().any() else None
        for _, r in g.iterrows():
            if r["L0W"] < thr_o:
                continue
            weak_gp = thr_gp is not None and not pd.isna(r["gp_ue"]) and r["gp_ue"] <= thr_gp
            weak_po = thr_po is not None and not pd.isna(r["perfect_orders"]) and r["perfect_orders"] <= thr_po
            if weak_gp or weak_po:
                rows.append(
                    {
                        "COUNTRY": r["COUNTRY"],
                        "CITY": r["CITY"],
                        "ZONE": r["ZONE"],
                        "L0W_orders": r["L0W"],
                        "Gross_Profit_UE": r["gp_ue"],
                        "Perfect_Orders": r["perfect_orders"],
                        "flag": "bajo_gp" if weak_gp and not weak_po else ("bajo_perfect" if weak_po and not weak_gp else "ambos"),
                    }
                )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values("L0W_orders", ascending=False).head(top_n)


def run_all(
    metrics: pd.DataFrame | None = None,
    orders: pd.DataFrame | None = None,
) -> InsightsBundle:
    if metrics is None:
        metrics = load_metrics()
    if orders is None:
        orders = load_orders()
    # El CSV incluye filas duplicadas por (zona, métrica); una fila por clave para reglas de insights.
    metrics = metrics.drop_duplicates(subset=["COUNTRY", "CITY", "ZONE", "METRIC"], keep="first")
    orders = orders.drop_duplicates(subset=["COUNTRY", "CITY", "ZONE"], keep="first")
    return InsightsBundle(
        anomalies_metrics=compute_anomalies_metrics(metrics),
        anomalies_orders=compute_anomalies_orders(orders),
        trends=compute_trends_three_weeks(metrics),
        benchmarking=compute_benchmarking(metrics),
        correlation=compute_correlation_lead_nonpro(metrics),
        opportunities=compute_opportunities(metrics, orders),
    )

"""Herramientas pandas invocadas por el LLM (datos reales, sin inventar números)."""

from __future__ import annotations

from difflib import get_close_matches
from typing import Any

import pandas as pd

from operaciones.data import WEEK_COLS_METRICS, WEEK_COLS_ORDERS, inner_zone_keys

METRIC_ALIASES: dict[str, str] = {
    "perfect order": "Perfect Orders",
    "perfect orders": "Perfect Orders",
    "lead penetration": "Lead Penetration",
    "gross profit": "Gross Profit UE",
    "gross profit ue": "Gross Profit UE",
}

COUNTRY_ALIASES: dict[str, str] = {
    "mexico": "MX",
    "méxico": "MX",
    "colombia": "CO",
    "argentina": "AR",
    "brasil": "BR",
    "brazil": "BR",
    "chile": "CL",
    "peru": "PE",
    "perú": "PE",
    "ecuador": "EC",
    "uruguay": "UY",
    "costa rica": "CR",
}


def normalize_country(code_or_name: str | None) -> str | None:
    if code_or_name is None or str(code_or_name).strip() == "":
        return None
    s = str(code_or_name).strip().upper()
    if len(s) == 2 and s.isalpha():
        return s
    key = str(code_or_name).strip().lower()
    return COUNTRY_ALIASES.get(key, s if len(s) == 2 else None)


def resolve_metric(name: str, available: list[str]) -> str | None:
    if not name or not str(name).strip():
        return None
    opts = list(available)
    q = str(name).strip()
    ql = q.lower().replace("%", "").strip()
    if ql in METRIC_ALIASES:
        target = METRIC_ALIASES[ql]
        if target in opts:
            return target
    for o in opts:
        if o.lower() == ql:
            return o
    for o in opts:
        if ql in o.lower() or o.lower() in ql:
            return o
    m = get_close_matches(q, opts, n=1, cutoff=0.35)
    return m[0] if m else None


class ToolExecutor:
    def __init__(self, metrics: pd.DataFrame, orders: pd.DataFrame) -> None:
        self.metrics = metrics
        self.orders = orders
        self._keys_inner = inner_zone_keys(metrics, orders)
        self._metric_names = sorted(metrics["METRIC"].dropna().unique().tolist())

    def list_available_metrics(self) -> str:
        lines = ["Métricas disponibles en `data/operaciones/RAW_INPUT_METRICS`:"]
        lines += [f"- {m}" for m in self._metric_names]
        return "\n".join(lines)

    def top_zones_by_metric(
        self,
        metric_name: str,
        country_code: str | None = None,
        n: int = 5,
        week_column: str = "L0W_ROLL",
    ) -> str:
        m = resolve_metric(metric_name, self._metric_names)
        if not m:
            return f"No reconozco la métrica `{metric_name}`. Usa list_available_metrics."
        if week_column not in self.metrics.columns:
            return f"Columna de semana inválida: {week_column}"
        cc = normalize_country(country_code)
        sub = self.metrics[self.metrics["METRIC"] == m].copy()
        if cc:
            sub = sub[sub["COUNTRY"] == cc]
        sub = sub.dropna(subset=[week_column])
        sub = sub.sort_values(week_column, ascending=False).head(max(1, min(int(n), 50)))
        if sub.empty:
            return "Sin filas para esos filtros."
        cols = ["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", week_column]
        cols = [c for c in cols if c in sub.columns]
        return f"Top {len(sub)} zonas por **{m}** ({week_column})" + (
            f" en **{cc}**" if cc else ""
        ) + ":\n\n" + sub[cols].to_markdown(index=False)

    def compare_zone_types(
        self,
        metric_name: str,
        country_code: str,
        week_column: str = "L0W_ROLL",
    ) -> str:
        m = resolve_metric(metric_name, self._metric_names)
        if not m:
            return f"No reconozco la métrica `{metric_name}`."
        cc = normalize_country(country_code)
        if not cc:
            return "Indica un país (ej. MX, CO, México)."
        sub = self.metrics[(self.metrics["METRIC"] == m) & (self.metrics["COUNTRY"] == cc)]
        sub = sub.dropna(subset=[week_column])
        if sub.empty:
            return "Sin datos para ese país/métrica."
        g = sub.groupby("ZONE_TYPE", dropna=False)[week_column].agg(["mean", "count"])
        g = g.rename(columns={"mean": f"promedio_{week_column}", "count": "n_zonas"})
        return (
            f"Comparación **{m}** por `ZONE_TYPE` en **{cc}** ({week_column}):\n\n"
            + g.to_markdown()
        )

    def metric_trend_for_zone(
        self,
        metric_name: str,
        zone_search: str,
        country_code: str | None = None,
    ) -> str:
        m = resolve_metric(metric_name, self._metric_names)
        if not m:
            return f"No reconozco la métrica `{metric_name}`."
        zs = str(zone_search).strip()
        sub = self.metrics[self.metrics["METRIC"] == m]
        sub = sub[sub["ZONE"].str.contains(zs, case=False, na=False)]
        cc = normalize_country(country_code)
        if cc:
            sub = sub[sub["COUNTRY"] == cc]
        if sub.empty:
            return f"No hay filas para zona que contenga `{zs}` y métrica `{m}`."
        row = sub.iloc[0]
        cols_present = [c for c in WEEK_COLS_METRICS if c in row.index]
        series = row[cols_present]
        # Tabla larga para el modelo
        tbl = (
            pd.DataFrame({"semana": cols_present, "valor": series.values})
            .replace({float("nan"): None})
        )
        meta = f"{row['COUNTRY']} / {row['CITY']} / {row['ZONE']} ({row.get('ZONE_TYPE', '')})"
        return f"Evolución **{m}** — {meta}\n\n" + tbl.to_markdown(index=False)

    def average_metric_by_country(
        self,
        metric_name: str,
        week_column: str = "L0W_ROLL",
    ) -> str:
        m = resolve_metric(metric_name, self._metric_names)
        if not m:
            return f"No reconozco la métrica `{metric_name}`."
        sub = self.metrics[self.metrics["METRIC"] == m].dropna(subset=[week_column])
        g = sub.groupby("COUNTRY")[week_column].mean().sort_values(ascending=False)
        out = g.reset_index()
        out.columns = ["COUNTRY", f"promedio_{week_column}"]
        return f"Promedio de **{m}** por país ({week_column}):\n\n" + out.to_markdown(
            index=False
        )

    def zones_high_metric_low_metric(
        self,
        high_metric_name: str,
        low_metric_name: str,
        country_code: str | None = None,
        top_n: int = 15,
    ) -> str:
        hm = resolve_metric(high_metric_name, self._metric_names)
        lm = resolve_metric(low_metric_name, self._metric_names)
        if not hm or not lm:
            return "Revisa nombres de métricas (usa list_available_metrics)."
        cc = normalize_country(country_code)

        def col(mname: str) -> pd.DataFrame:
            d = self.metrics[self.metrics["METRIC"] == mname][
                ["COUNTRY", "CITY", "ZONE", "L0W_ROLL"]
            ].rename(columns={"L0W_ROLL": mname})
            if cc:
                d = d[d["COUNTRY"] == cc]
            return d

        a = col(hm)
        b = col(lm)
        merged = a.merge(b, on=["COUNTRY", "CITY", "ZONE"], how="inner")
        merged = merged.dropna(subset=[hm, lm])
        if merged.empty:
            return "Sin zonas con ambas métricas en el mismo periodo (L0W_ROLL)."
        hi_thr = merged[hm].quantile(0.75)
        lo_thr = merged[lm].quantile(0.25)
        sel = merged[(merged[hm] >= hi_thr) & (merged[lm] <= lo_thr)]
        sel = sel.sort_values(hm, ascending=False).head(max(1, min(int(top_n), 50)))
        country_note = f" en **{cc}**" if cc else " (todos los países, umbrales globales)"
        return (
            f"Zonas con **{hm}** alto (≥ P75={hi_thr:.4g}) y **{lm}** bajo (≤ P25={lo_thr:.4g})"
            + country_note
            + ":\n\n"
            + sel.to_markdown(index=False)
        )

    def top_growing_orders_zones(
        self,
        num_weeks: int = 5,
        top_n: int = 10,
        country_code: str | None = None,
    ) -> str:
        """Crecimiento aproximado: (L0W - L{n}W) / L{n}W con n=num_weeks."""
        n = max(1, min(int(num_weeks), 8))
        col_old = f"L{n}W"
        if col_old not in self.orders.columns or "L0W" not in self.orders.columns:
            return "Columnas de semanas no encontradas en órdenes."
        cc = normalize_country(country_code)
        o = self.orders.copy()
        if cc:
            o = o[o["COUNTRY"] == cc]
        o = o.dropna(subset=["L0W", col_old])
        o = o[o[col_old] > 0]
        o["growth_pct"] = (o["L0W"] - o[col_old]) / o[col_old] * 100.0
        top = o.sort_values("growth_pct", ascending=False).head(max(1, min(int(top_n), 30)))

        lines: list[str] = [
            f"Zonas con mayor crecimiento % de órdenes (L0W vs {col_old})"
            + (f" en **{cc}**" if cc else "")
            + ":\n"
        ]
        lines.append(top[["COUNTRY", "CITY", "ZONE", "L0W", col_old, "growth_pct"]].to_markdown(index=False))

        # Explicación factual: pegar algunas métricas L0 por zona (inner join)
        keys = top[["COUNTRY", "CITY", "ZONE"]]
        msub = self.metrics.merge(keys, on=["COUNTRY", "CITY", "ZONE"], how="inner")
        focus = [
            "Lead Penetration",
            "Perfect Orders",
            "Gross Profit UE",
            "Non-Pro PTC > OP",
        ]
        lines.append(
            "\n\n**Contexto operacional (L0W_ROLL, misma zona; no implica causalidad):**"
        )
        for _, z in keys.iterrows():
            slice_z = msub[
                (msub["COUNTRY"] == z["COUNTRY"])
                & (msub["CITY"] == z["CITY"])
                & (msub["ZONE"] == z["ZONE"])
            ]
            lines.append(
                f"\n- **{z['COUNTRY']} / {z['CITY']} / {z['ZONE']}**"
            )
            for fm in focus:
                row = slice_z[slice_z["METRIC"] == fm]
                if row.empty:
                    continue
                v = row.iloc[0].get("L0W_ROLL", float("nan"))
                lines.append(f"  - {fm}: {v}")
        return "\n".join(lines)

    def problematic_zones(
        self,
        metric_name: str | None = None,
        country_code: str | None = None,
        threshold_pct: float = 10.0,
        top_n: int = 10,
    ) -> str:
        """
        Zonas donde la métrica cayó > threshold_pct de L1W_ROLL a L0W_ROLL.
        Si no se pasa métrica, usa Gross Profit UE por defecto.
        """
        name = metric_name or "Gross Profit UE"
        m = resolve_metric(name, self._metric_names)
        if not m:
            return f"No reconozco la métrica `{name}`."
        cc = normalize_country(country_code)
        sub = self.metrics[self.metrics["METRIC"] == m].copy()
        if cc:
            sub = sub[sub["COUNTRY"] == cc]
        sub = sub.dropna(subset=["L0W_ROLL", "L1W_ROLL"])
        sub = sub[sub["L1W_ROLL"] != 0]
        sub["pct_change"] = (sub["L0W_ROLL"] - sub["L1W_ROLL"]) / sub["L1W_ROLL"].abs() * 100.0
        bad = sub[sub["pct_change"] < -abs(threshold_pct)].sort_values("pct_change").head(
            max(1, min(int(top_n), 30))
        )
        if bad.empty:
            return (
                f"No hay zonas con deterioro >{threshold_pct}% semana a semana para **{m}**"
                + (f" en {cc}" if cc else "")
                + "."
            )
        cols = [
            "COUNTRY",
            "CITY",
            "ZONE",
            "ZONE_TYPE",
            "L1W_ROLL",
            "L0W_ROLL",
            "pct_change",
        ]
        cols = [c for c in cols if c in bad.columns]
        return (
            f"Zonas **problemáticas** (caída >{threshold_pct}% L1→L0) en **{m}**:\n\n"
            + bad[cols].to_markdown(index=False)
        )

    def run(self, name: str, arguments: dict[str, Any]) -> str:
        args = arguments or {}
        if name == "list_available_metrics":
            return self.list_available_metrics()
        if name == "top_zones_by_metric":
            return self.top_zones_by_metric(
                metric_name=args.get("metric_name", ""),
                country_code=args.get("country_code"),
                n=int(args.get("n", 5)),
                week_column=str(args.get("week_column", "L0W_ROLL")),
            )
        if name == "compare_zone_types":
            return self.compare_zone_types(
                metric_name=args.get("metric_name", ""),
                country_code=args.get("country_code", ""),
                week_column=str(args.get("week_column", "L0W_ROLL")),
            )
        if name == "metric_trend_for_zone":
            return self.metric_trend_for_zone(
                metric_name=args.get("metric_name", ""),
                zone_search=args.get("zone_search", ""),
                country_code=args.get("country_code"),
            )
        if name == "average_metric_by_country":
            return self.average_metric_by_country(
                metric_name=args.get("metric_name", ""),
                week_column=str(args.get("week_column", "L0W_ROLL")),
            )
        if name == "zones_high_metric_low_metric":
            return self.zones_high_metric_low_metric(
                high_metric_name=args.get("high_metric_name", ""),
                low_metric_name=args.get("low_metric_name", ""),
                country_code=args.get("country_code"),
                top_n=int(args.get("top_n", 15)),
            )
        if name == "top_growing_orders_zones":
            return self.top_growing_orders_zones(
                num_weeks=int(args.get("num_weeks", 5)),
                top_n=int(args.get("top_n", 10)),
                country_code=args.get("country_code"),
            )
        if name == "problematic_zones":
            return self.problematic_zones(
                metric_name=args.get("metric_name"),
                country_code=args.get("country_code"),
                threshold_pct=float(args.get("threshold_pct", 10.0)),
                top_n=int(args.get("top_n", 10)),
            )
        return f"Herramienta desconocida: {name}"

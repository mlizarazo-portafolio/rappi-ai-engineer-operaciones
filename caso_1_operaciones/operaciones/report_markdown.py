"""
Arma el informe ejecutivo en Markdown a partir de InsightsBundle.
"""

from __future__ import annotations

import html
from datetime import datetime, timezone

import markdown
import pandas as pd

from operaciones.data_dictionary import load_data_dictionary_for_prompt
from operaciones.insights_engine import KEY_METRIC_BENCHMARK, InsightsBundle


def _md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df is None or df.empty:
        return "_Sin filas._\n"
    return df.head(max_rows).to_markdown(index=False) + "\n"


def _reco_anomaly(row: pd.Series) -> str:
    direction = "subió" if row["pct_change_L1_to_L0"] > 0 else "cayó"
    return (
        f"Revisar drivers en **{row['CITY']} / {row['ZONE']}** ({row['METRIC']}): "
        f"{direction} **{row['pct_change_L1_to_L0']:.1f}%** L1→L0; validar operación, surtido o incidentes puntuales."
    )


def _reco_trend(row: pd.Series) -> str:
    return (
        f"Investigar tendencia negativa sostenida en **{row['METRIC']}** "
        f"({row['COUNTRY']} — {row['ZONE']}): L2→L1→L0 en descenso."
    )


def _reco_benchmark(row: pd.Series) -> str:
    return (
        f"En **{row['COUNTRY']}** ({row['ZONE_TYPE']}), acotar buenas prácticas de **{row['high_zone']}** "
        f"({row['metric']}={row['high_value']:.3g}) vs **{row['low_zone']}** ({row['low_value']:.3g}); "
        f"brecha **{row['spread']:.3g}**."
    )


def _reco_opportunity(row: pd.Series) -> str:
    return (
        f"Zona prioritaria con volumen alto (**órdenes L0W**={row['L0W_orders']:.0f}): "
        f"plan de mejora en margen/calidad ({row['flag']}) en **{row['ZONE']}** ({row['CITY']})."
    )


def build_executive_summary(b: InsightsBundle) -> tuple[list[str], list[str]]:
    """Párrafos de resumen + lista de recomendaciones (5 o menos)."""
    bullets: list[str] = []
    recos: list[str] = []

    if not b.anomalies_metrics.empty:
        r = b.anomalies_metrics.iloc[0]
        bullets.append(
            f"**Anomalía destacada:** {r['METRIC']} en {r['COUNTRY']} / {r['ZONE']} "
            f"cambió **{r['pct_change_L1_to_L0']:+.1f}%** de L1 a L0."
        )
        recos.append(_reco_anomaly(r))

    if not b.anomalies_orders.empty:
        r = b.anomalies_orders.iloc[0]
        bullets.append(
            f"**Órdenes:** {r['ZONE']} ({r['COUNTRY']}) varió **{r['pct_change_L1_to_L0']:+.1f}%** en volumen semanal L1→L0."
        )

    if not b.trends.empty:
        r = b.trends.iloc[0]
        bullets.append(
            f"**Tendencia preocupante:** {r['METRIC']} cae 3 semanas seguidas en {r['ZONE']} ({r['COUNTRY']})."
        )
        recos.append(_reco_trend(r))

    if not b.benchmarking.empty:
        r = b.benchmarking.iloc[0]
        bullets.append(
            f"**Benchmarking:** mayor brecha de {r['metric']} en {r['COUNTRY']} ({r['ZONE_TYPE']}): "
            f"spread **{r['spread']:.3g}** entre mejor y peor zona."
        )
        recos.append(_reco_benchmark(r))

    corr = b.correlation
    if corr.get("n", 0) >= 30 and not pd.isna(corr.get("spearman")):
        rho = corr["spearman"]
        bullets.append(
            f"**Correlación (Spearman):** Lead Penetration vs Non-Pro PTC > OP → **ρ ≈ {rho:.2f}** (n={corr['n']} zonas)."
        )
        recos.append(
            "Explorar con SP&A si zonas con baja penetración de leads concentran también fricción en checkout No-Pro "
            "(correlación no implica causalidad)."
        )

    if not b.opportunities.empty:
        r = b.opportunities.iloc[0]
        bullets.append(
            f"**Oportunidad:** zona prioritaria **{r['ZONE']}** con alto volumen y palancas de mejora ({r['flag']})."
        )
        recos.append(_reco_opportunity(r))

    return bullets[:5], recos[:5]


def build_markdown_report(b: InsightsBundle) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary_bullets, recos = build_executive_summary(b)

    lines: list[str] = [
        "# Informe ejecutivo — insights operacionales (automático)",
        "",
        f"_Generado: {now}. Archivos: `data/caso_1_operaciones/RAW_INPUT_METRICS.csv`, `RAW_ORDERS.csv`, `RAW_SUMMARY.csv`._",
        "",
        "## Resumen ejecutivo (hallazgos críticos)",
        "",
    ]
    for s in summary_bullets:
        lines.append(f"- {s}")
    if not summary_bullets:
        lines.append("_No se generaron bullets automáticos (datasets vacíos o filtros muy estrictos)._")
    lines += ["", "## Recomendaciones accionables (priorizadas)", ""]
    for i, r in enumerate(recos, 1):
        lines.append(f"{i}. {r}")
    if not recos:
        lines.append("_Sin recomendaciones automáticas._")

    lines += [
        "",
        "---",
        "",
        "## 1. Anomalías (métricas, |Δ%| ≥ 10% L1→L0)",
        "",
        "Variaciones bruscas semana a semana por zona y métrica.",
        "",
        _md_table(b.anomalies_metrics),
        "",
        "## 2. Anomalías en volumen de órdenes",
        "",
        _md_table(b.anomalies_orders),
        "",
        "## 3. Tendencias preocupantes (3 semanas seguidas a la baja)",
        "",
        "Solo métricas donde más alto es mejor; patrón estricto L0 < L1 < L2.",
        "",
        _md_table(b.trends),
        "",
        "## 4. Benchmarking interno (misma geografía y tipo de zona)",
        "",
        f"Mayor brecha en **{KEY_METRIC_BENCHMARK}** (L0W_ROLL) entre mejor y peor zona por grupo.",
        "",
        _md_table(b.benchmarking),
        "",
        "## 5. Correlaciones (observacionales)",
        "",
    ]

    corr = b.correlation
    lines.append(corr.get("note", ""))
    lines.append("")
    lines.append(f"- **n** zonas con ambas métricas: {corr.get('n', 0)}")
    rho = corr.get("spearman")
    if rho is not None and not (isinstance(rho, float) and pd.isna(rho)):
        lines.append(f"- **Spearman (Lead Penetration vs Non-Pro PTC > OP):** {rho:.4f}")
    lines += [
        "",
        "## 6. Oportunidades",
        "",
        "Zonas **High Priority / Prioritized** con órdenes L0W altas (P75 por país) y margen o Perfect Orders en cuarto inferior.",
        "",
        _md_table(b.opportunities),
        "",
        "## Apéndice — Diccionario de columnas (RAW_SUMMARY.csv)",
        "",
        load_data_dictionary_for_prompt(max_chars=8000),
        "",
        "---",
        "",
        "_Fin del informe._",
        "",
    ]
    return "\n".join(lines)


_REPORT_CSS = """
:root {
  --text: #1c1c1c;
  --muted: #5c5c5c;
  --border: #d8d8d8;
  --head-bg: #f0f4f8;
  --accent: #0d6efd;
}
* { box-sizing: border-box; }
body {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  font-size: 11pt;
  line-height: 1.5;
  color: var(--text);
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
  background: #fff;
}
h1 {
  font-size: 1.65rem;
  font-weight: 700;
  margin: 0 0 0.35rem 0;
  color: #0f172a;
  border-bottom: 3px solid var(--accent);
  padding-bottom: 0.5rem;
}
h2 {
  font-size: 1.2rem;
  margin: 1.75rem 0 0.65rem 0;
  color: #0f172a;
}
h3 { font-size: 1.05rem; margin: 1.25rem 0 0.5rem; }
p { margin: 0.5rem 0; }
em { color: var(--muted); font-style: italic; }
hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.5rem 0;
}
ul { margin: 0.5rem 0 0.5rem 1.25rem; padding: 0; }
li { margin: 0.25rem 0; }
strong { font-weight: 600; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 9.5pt;
  margin: 0.75rem 0 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
thead th {
  background: var(--head-bg);
  font-weight: 600;
  text-align: left;
  padding: 0.45rem 0.5rem;
  border: 1px solid var(--border);
}
tbody td {
  padding: 0.4rem 0.5rem;
  border: 1px solid var(--border);
  vertical-align: top;
  word-break: break-word;
}
tbody tr:nth-child(even) { background: #fafbfc; }
code, pre {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 0.88em;
}
pre {
  background: #f6f8fa;
  padding: 0.75rem;
  border-radius: 6px;
  overflow-x: auto;
  border: 1px solid var(--border);
}
.doc-meta {
  color: var(--muted);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}
@media print {
  body { max-width: none; padding: 0; font-size: 10pt; }
  h1 { border-bottom-color: #333; }
  table { box-shadow: none; page-break-inside: avoid; }
  h2, h3 { page-break-after: avoid; }
  thead { display: table-header-group; }
}
"""


def markdown_to_report_html(md: str, title: str = "Informe insights") -> str:
    """Convierte Markdown a HTML con estilos (pantalla + impresión / Guardar como PDF)."""
    body_html = markdown.markdown(
        md,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    esc_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{esc_title}</title>
  <style>{_REPORT_CSS}</style>
</head>
<body>
<article class="report">
{body_html}
</article>
</body>
</html>
"""


def markdown_to_minimal_html(md: str, title: str = "Informe insights") -> str:
    """Alias: usa el HTML formateado (antes era solo `<pre>`)."""
    return markdown_to_report_html(md, title)

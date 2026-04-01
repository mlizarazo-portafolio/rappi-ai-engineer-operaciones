"""
Informe de insights + gráficos (matplotlib) a partir del CSV de scraping.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from competitive_intel.paths import default_scrape_csv, reports_dir


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in (
        "item_price_mxn",
        "delivery_fee_mxn",
        "service_fee_mxn",
        "total_checkout_mxn",
        "eta_minutes",
    ):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def _provenance_lines(df: pd.DataFrame) -> list[str]:
    lines = ["## Calidad y procedencia de datos", ""]
    if "data_source" in df.columns:
        vc = df["data_source"].astype(str).value_counts()
        lines.append("**Origen (`data_source`):** " + "; ".join(f"`{k}` ({v} filas)" for k, v in vc.items()))
        lines.append("")
        if df["data_source"].astype(str).str.contains("synthetic_demo").any():
            if df["data_source"].astype(str).eq("synthetic_demo").all():
                lines.append(
                    "- Todo el CSV es **demo sintético** (`synthetic_demo`): sirve para pipeline, no para decisiones de mercado."
                )
            else:
                lines.append(
                    "- **Mezcla** de filas sintéticas y scrape; revisar columna `data_source` fila a fila."
                )
        if df["data_source"].astype(str).str.contains("playwright").any():
            lines.append(
                "- Hay filas de **scrape web (Playwright)**. Los números dependen de la UI del momento; validar fees/precios que parezcan atípicos."
            )
    if "platform" in df.columns and "item_price_mxn" in df.columns:
        cov = df.groupby("platform")["item_price_mxn"].apply(lambda s: s.notna().mean())
        lines.append("")
        lines.append(
            "**Cobertura (% filas con precio de ítem):** "
            + ", ".join(f"`{p}` {cov[p]:.0%}" for p in sorted(cov.index))
        )
    lines.append("")
    return lines


def _fig_bar_means(df: pd.DataFrame, col: str, title: str, ylabel: str, out: Path) -> None:
    g = df.groupby("platform")[col].mean().sort_values()
    fig, ax = plt.subplots(figsize=(7, 4))
    g.plot(kind="barh", ax=ax, color=plt.cm.Set2(np.linspace(0, 1, len(g))))
    ax.set_title(title)
    ax.set_xlabel(ylabel)
    plt.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def build_report(csv_path: Path | None = None) -> Path:
    csv_path = csv_path or default_scrape_csv()
    if not csv_path.exists():
        raise FileNotFoundError(
            f"No existe {csv_path}. Desde caso_2_competitive_intelligence/: "
            "python -m competitive_intel demo | scrape | scrape --fallback-demo"
        )

    df = _coerce_numeric(pd.read_csv(csv_path))
    rdir = reports_dir()
    fig_dir = rdir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    _fig_bar_means(
        df,
        "total_checkout_mxn",
        "Ticket promedio estimado por plataforma (MXN)",
        "MXN",
        fig_dir / "fig1_total_by_platform.png",
    )
    fees = df.groupby("platform")[["delivery_fee_mxn", "service_fee_mxn"]].mean()
    fig, ax = plt.subplots(figsize=(7, 4))
    fees.plot(kind="bar", ax=ax, rot=0)
    ax.set_title("Fees promedio: delivery vs service")
    ax.set_ylabel("MXN")
    plt.legend(["Delivery", "Service"])
    plt.tight_layout()
    fig.savefig(fig_dir / "fig2_fees_by_platform.png", dpi=120)
    plt.close(fig)

    eta = df.groupby("platform")["eta_minutes"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(7, 4))
    eta.plot(kind="bar", ax=ax, color="steelblue")
    ax.set_title("ETA promedio declarado (minutos)")
    ax.set_ylabel("Minutos")
    plt.xticks(rotation=15)
    plt.tight_layout()
    fig.savefig(fig_dir / "fig3_eta_by_platform.png", dpi=120)
    plt.close(fig)

    # --- Top 5 insights (datos agregados) ---
    mean_total = df.groupby("platform")["total_checkout_mxn"].mean().dropna()
    mean_del = df.groupby("platform")["delivery_fee_mxn"].mean().dropna()
    mean_eta = df.groupby("platform")["eta_minutes"].mean().dropna()
    cheapest = mean_total.idxmin() if len(mean_total) else "N/D"
    priciest = mean_total.idxmax() if len(mean_total) else "N/D"
    low_fee = mean_del.idxmin() if len(mean_del) else "N/D"
    fastest = mean_eta.idxmin() if len(mean_eta) else "N/D"

    all_demo = "data_source" in df.columns and df["data_source"].astype(str).eq("synthetic_demo").all()
    any_pw = "data_source" in df.columns and df["data_source"].astype(str).str.contains("playwright").any()
    if len(mean_eta) == 0:
        eta_insight = "No hay ETA numérico suficiente para comparar plataformas en este CSV."
        footer = "_Completar scrape o revisar filas sin `eta_minutes`._"
    elif all_demo:
        eta_insight = f"`{fastest}` lidera ETA medio en el **CSV sintético (demo)**."
        footer = (
            "_Este informe se generó a partir de **datos demo**. Para el enunciado real, sustituir por `scrape` Playwright "
            "y validar cobertura por plataforma._"
        )
    elif any_pw:
        eta_insight = (
            f"`{fastest}` muestra el menor ETA medio **en este scrape web**; repetir corridas y contrastar con app "
            "por posibles diferencias de UI."
        )
        footer = (
            "_Datos obtenidos vía **navegador automatizado**; pueden faltar plataformas o filas. No usar como única "
            "fuente para pricing en producción sin validación humana y, si aplica, canales oficiales/partners._"
        )
    else:
        eta_insight = f"`{fastest}` lidera ETA medio en este dataset."
        footer = "_Revisar procedencia en columna `data_source` del CSV._"

    promo_rate = df.assign(
        has_promo=df["promotions_visible"].astype(str).str.lower().ne("ninguna visible")
    ).groupby("platform")["has_promo"].mean()

    # Variabilidad geográfica: std del total por ciudad entre plataformas
    city_spread = df.groupby(["city", "platform"])["total_checkout_mxn"].mean().unstack()
    city_std = city_spread.std(axis=1).sort_values(ascending=False)
    volatile_city = city_std.index[0] if len(city_std) else "N/D"

    if len(mean_total) >= 2:
        ticket_bullet = (
            f"- **Ticket medio más bajo:** `{cheapest}` (~{mean_total[cheapest]:.1f} MXN vs `{priciest}` "
            f"~{mean_total[priciest]:.1f} MXN)."
        )
    elif len(mean_total) == 1:
        only = mean_total.index[0]
        ticket_bullet = f"- **Solo una plataforma con ticket calculable:** `{only}` (~{mean_total[only]:.1f} MXN)."
    else:
        ticket_bullet = (
            "- **Ticket medio:** datos insuficientes (revisar NaN en `total_checkout_mxn` / cobertura por plataforma)."
        )
    eta_bullet = (
        f"- **Menor ETA medio:** `{fastest}` (~{mean_eta[fastest]:.0f} min)."
        if len(mean_eta)
        else "- **ETA:** sin datos numéricos suficientes."
    )

    lines = [
        "# Informe — Competitive Intelligence (México)",
        "",
        f"_Fuente CSV: `{csv_path.name}`. Filas: {len(df)}._",
        "",
        *_provenance_lines(df),
        "## Comparativo rápido",
        "",
        ticket_bullet,
        f"- **Delivery fee más bajo en promedio:** `{low_fee}`.",
        eta_bullet,
        f"- **Ciudad con mayor dispersión entre plataformas (ticket):** `{volatile_city}`.",
        f"- **Tasa filas con promoción visible (no 'Ninguna'):** "
        + ", ".join(f"`{p}` {promo_rate[p]:.0%}" for p in sorted(promo_rate.index)),
        "",
        "## Visualizaciones",
        "",
        "![Total por plataforma](figures/fig1_total_by_platform.png)",
        "",
        "![Fees](figures/fig2_fees_by_platform.png)",
        "",
        "![ETA](figures/fig3_eta_by_platform.png)",
        "",
        "## Top 5 insights accionables",
        "",
        *(
            [
                f"1. **Finding:** En este dataset, `{cheapest}` muestra ticket medio más bajo que `{priciest}`.  ",
                "   **Impacto:** Percepción de precio y conversión en carrito pueden verse afectadas en zonas sensibles al precio.  ",
                f"   **Recomendación:** Revisar bundle/promos en ciudades donde la brecha vs `{cheapest}` sea mayor al percentil 75.",
            ]
            if len(mean_total) >= 2
            else [
                "1. **Finding:** La comparación de ticket entre plataformas está **incompleta** (faltan precios o totales en una o más apps).  ",
                "   **Impacto:** Riesgo de conclusiones sesgadas si solo una plataforma tiene cobertura.  ",
                "   **Recomendación:** Priorizar scrape estable por plataforma o datos licenciados antes de presentar benchmarks.",
            ]
        ),
        "",
        f"2. **Finding:** `{low_fee}` concentra delivery fees medios más bajos.  ",
        "   **Impacto:** Competencia en costo de envío en zonas periféricas.  ",
        "   **Recomendación:** Simular subsidio parcial de envío en `zone_type=periphery` priorizado.",
        "",
        f"3. **Finding:** {eta_insight}  ",
        "   **Impacto:** Expectativa de tiempo en UX y retención.  ",
        "   **Recomendación:** Validar ETA con varias ventanas horarias y ubicación exacta (mismo punto en las tres apps).",
        "",
        "4. **Finding:** Mezcla de promos visibles difiere por plataforma en el CSV.  ",
        "   **Impacto:** Guerra promocional en adquisición.  ",
        "   **Recomendación:** Tablero semanal de tipo de promo por zona y vertical (extender scrape).",
        "",
        f"5. **Finding:** Alta variabilidad inter-plataforma en `{volatile_city}`.  ",
        "   **Impacto:** Pricing inconsistente percibido por usuario.  ",
        "   **Recomendación:** Deep-dive de fees + restaurante ancla (misma cadena cross-app) en esa ciudad.",
        "",
        "---",
        footer,
        "",
    ]
    out_md = rdir / "informe_competitive_intelligence.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return out_md

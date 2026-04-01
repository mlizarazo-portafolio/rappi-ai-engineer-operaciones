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

    df = pd.read_csv(csv_path)
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
    mean_total = df.groupby("platform")["total_checkout_mxn"].mean()
    cheapest = mean_total.idxmin()
    priciest = mean_total.idxmax()
    mean_del = df.groupby("platform")["delivery_fee_mxn"].mean()
    low_fee = mean_del.idxmin()
    mean_eta = df.groupby("platform")["eta_minutes"].mean()
    fastest = mean_eta.idxmin()

    promo_rate = df.assign(
        has_promo=df["promotions_visible"].astype(str).str.lower().ne("ninguna visible")
    ).groupby("platform")["has_promo"].mean()

    # Variabilidad geográfica: std del total por ciudad entre plataformas
    city_spread = df.groupby(["city", "platform"])["total_checkout_mxn"].mean().unstack()
    city_std = city_spread.std(axis=1).sort_values(ascending=False)
    volatile_city = city_std.index[0] if len(city_std) else "N/D"

    lines = [
        "# Informe — Competitive Intelligence (México)",
        "",
        f"_Fuente CSV: `{csv_path.name}`. Filas: {len(df)}._",
        "",
        "## Comparativo rápido",
        "",
        f"- **Ticket medio más bajo:** `{cheapest}` (~{mean_total[cheapest]:.1f} MXN vs `{priciest}` ~{mean_total[priciest]:.1f} MXN).",
        f"- **Delivery fee más bajo en promedio:** `{low_fee}`.",
        f"- **Menor ETA medio:** `{fastest}` (~{mean_eta[fastest]:.0f} min).",
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
        f"1. **Finding:** En este dataset, `{cheapest}` muestra ticket medio más bajo que `{priciest}`.  ",
        "   **Impacto:** Percepción de precio y conversión en carrito pueden verse afectadas en zonas sensibles al precio.  ",
        f"   **Recomendación:** Revisar bundle/promos en ciudades donde la brecha vs `{cheapest}` sea mayor al percentil 75.",
        "",
        f"2. **Finding:** `{low_fee}` concentra delivery fees medios más bajos.  ",
        "   **Impacto:** Competencia en costo de envío en zonas periféricas.  ",
        "   **Recomendación:** Simular subsidio parcial de envío en `zone_type=periphery` priorizado.",
        "",
        f"3. **Finding:** `{fastest}` lidera ETA medio en datos sintéticos/demo.  ",
        "   **Impacto:** Expectativa de tiempo en UX y retención.  ",
        "   **Recomendación:** Mapear zonas donde ETA Rappi supere competencia en scrape real y ajustar SLAs operativos.",
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
        "_Datos demo: reemplazar con scrape real para decisiones de producción._",
        "",
    ]
    out_md = rdir / "informe_competitive_intelligence.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return out_md

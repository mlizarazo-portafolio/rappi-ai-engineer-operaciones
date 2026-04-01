# Fase 2 — Insights automáticos + informe ejecutivo

**Fecha:** 2026-04-01  
**Plan:** `plan/plan_operaciones.md` § Fase 2

---

## Qué se implementó

| Componente | Archivo | Descripción |
|------------|---------|-------------|
| Motor de reglas | `operaciones/insights_engine.py` | Anomalías, tendencias, benchmarking, correlación Spearman, oportunidades |
| Informe | `operaciones/report_markdown.py` | Markdown + recomendaciones; HTML mínimo (pre escapado) |
| CLI | `operaciones/generate_report.py` | Escribe `reports/insights_executive_<timestamp>.md` y `.html` |

---

## Reglas (alineadas al brief)

1. **Anomalías (métricas):** |Δ%| ≥ 10% entre `L1W_ROLL` y `L0W_ROLL` por zona y métrica (top 25 por magnitud).
2. **Anomalías (órdenes):** mismo criterio con `L1W` / `L0W`.
3. **Tendencias preocupantes:** en métricas “más alto es mejor”, patrón estricto **L0 < L1 < L2** (tres semanas seguidas a la baja).
4. **Benchmarking:** por `(COUNTRY, ZONE_TYPE)`, mayor brecha en **Gross Profit UE** (`L0W_ROLL`) entre la mejor y la peor zona.
5. **Correlación:** Spearman entre **Lead Penetration** y **Non-Pro PTC > OP** a nivel zona (`L0W_ROLL`); texto explícito de que **no implica causalidad**.
6. **Oportunidades:** zonas **High Priority / Prioritized** con órdenes `L0W` en el cuartil alto del país y **Gross Profit UE** o **Perfect Orders** en el 40% inferior del país.

**Nota:** el CSV trae filas duplicadas por `(COUNTRY, CITY, ZONE, METRIC)`; `run_all()` deduplica con `keep="first"` antes de calcular insights.

---

## Cómo generar el informe

Desde la raíz del repo (venv activado):

```powershell
python -m operaciones.generate_report
```

Salida típica: `reports/insights_executive_YYYYMMDD_HHMMSS.md` y `.html`.

---

## Contenido del informe

- Resumen ejecutivo (hasta 5 bullets).
- Recomendaciones accionables numeradas (derivadas de esos hallazgos).
- Secciones 1–6 con tablas (markdown).

**PDF:** el `.html` convierte el Markdown a HTML real (tablas, títulos, listas) con CSS; en el navegador → **Imprimir → Guardar como PDF** para un PDF limpio. Pandoc sigue siendo opcional.

---

## Criterio de salida Fase 2

Cumplido: comando único que escribe el artefacto final (MD + HTML).

**Siguiente:** Fase 3 — pulir README global, lista de pruebas pre-demo, coste API estimado.

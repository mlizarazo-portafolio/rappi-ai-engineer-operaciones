# Rappi — pruebas técnicas AI Engineer

Monorepo con **dos casos** en carpetas separadas: datos bajo `data/`, briefs en `docs/briefs/`.

## Estructura

| Ruta | Caso |
|------|------|
| `data/operaciones/` | CSV del caso Operaciones (3 archivos) |
| `data/competitive_intelligence/output/` | CSV generado por el pipeline CI (no commitear corridas; ver `.gitignore`) |
| `operaciones/` | Código: bot Streamlit + insights + informe |
| `competitive_intel/` | Código: direcciones MX + demo scrape + informe + figuras |
| `docs/briefs/` | Enunciados en Markdown |

## Requisitos globales

- Python 3.11+
- `pip install -r requirements.txt`
- **Solo Operaciones:** variable `OPENAI_API_KEY` en `.env` (plantilla: `.env.example`)

---

## Caso 1 — Operaciones

```powershell
streamlit run operaciones/app.py
python -m operaciones.generate_report
```

- Datos: `data/operaciones/RAW_INPUT_METRICS.csv`, `RAW_ORDERS.csv`, `RAW_SUMMARY.csv`
- Informe operaciones: `reports/insights_executive_*.{md,html}`

---

## Caso 2 — Competitive Intelligence

Pipeline demo (CSV sintético reproducible + informe con 3 gráficos):

```powershell
python -m competitive_intel demo
python -m competitive_intel report
```

- Direcciones y justificación: `competitive_intel/addresses_mx.json` (20 zonas en México)
- CSV: `data/competitive_intelligence/output/scrape_latest.csv`
- Informe: `competitive_intel/reports/informe_competitive_intelligence.md` y `reports/figures/*.png`

`python -m competitive_intel scrape` hoy equivale a `demo` (stub). Para scrape real, ver `competitive_intel/scrapers/README.md`.

---

## Coste API (solo Operaciones)

Modelo `gpt-4o-mini`. Orden de magnitud **~USD 0.05–0.15** por ~10 preguntas; [precios OpenAI](https://platform.openai.com/pricing). El caso CI **no** usa API en este repo.

---

## Publicar en GitHub

```powershell
git remote add origin https://github.com/USUARIO/REPO.git
git push -u origin main
```

No subir `.env` ni `.venv`.

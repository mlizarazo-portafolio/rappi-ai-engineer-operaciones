# Rappi — pruebas técnicas AI Engineer

Dos carpetas de primer nivel, **una por caso**, para que quede claro qué código y enunciado va con cada entrega. Los datos compartidos siguen bajo `data/` con nombres alineados al caso.

## Estructura

| Carpeta | Contenido |
|---------|-----------|
| **`caso_1_operaciones/`** | Enunciado + código del bot Streamlit, insights e informe |
| **`caso_2_competitive_intelligence/`** | Enunciado + pipeline demo CI (CSV sintético + informe) |
| `data/caso_1_operaciones/` | Tres CSV del caso Operaciones |
| `data/caso_2_competitive_intelligence/output/` | CSV generado por `demo` (no commitear corridas; ver `.gitignore`) |
| `docs/` | Notas generales del repo (opcional) |

Cada carpeta de caso tiene su propio **`README.md`** con comandos exactos.

## Requisitos globales

- Python 3.11+
- `pip install -r requirements.txt` (desde la raíz del monorepo)
- **Solo caso 1:** variable `OPENAI_API_KEY` en `.env` en la **raíz** del repo (plantilla: `.env.example`)

---

## Caso 1 — Operaciones

```powershell
cd caso_1_operaciones
streamlit run operaciones/app.py
python -m operaciones.generate_report
```

También puedes lanzar Streamlit desde la raíz:

```powershell
streamlit run caso_1_operaciones/operaciones/app.py
```

- Datos: `data/caso_1_operaciones/RAW_INPUT_METRICS.csv`, `RAW_ORDERS.csv`, `RAW_SUMMARY.csv`
- Informe: `reports/insights_executive_*.{md,html}` (raíz del repo)

---

## Caso 2 — Competitive Intelligence

```powershell
cd caso_2_competitive_intelligence
python -m competitive_intel demo
python -m competitive_intel report
```

- Direcciones: `caso_2_competitive_intelligence/competitive_intel/addresses_mx.json`
- CSV demo: `data/caso_2_competitive_intelligence/output/scrape_latest.csv`
- Informe: `caso_2_competitive_intelligence/competitive_intel/reports/`

`python -m competitive_intel scrape` usa **Playwright** (webs públicas). Requiere `playwright install chromium`. Detalle y límites: `caso_2_competitive_intelligence/competitive_intel/scrapers/README.md`. Opción sin red: `demo`.

---

## Coste API (solo caso 1)

Modelo `gpt-4o-mini`. Orden de magnitud **~USD 0.05–0.15** por ~10 preguntas; [precios OpenAI](https://platform.openai.com/pricing). El caso 2 **no** usa API en este repo.

---

## Publicar en GitHub

```powershell
git remote add origin https://github.com/USUARIO/REPO.git
git push -u origin main
```

No subir `.env` ni `.venv`.

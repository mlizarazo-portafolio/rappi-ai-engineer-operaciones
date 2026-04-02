# Rappi — Pruebas técnicas AI Engineer

Monorepo con **dos casos** independientes (`caso_1_operaciones`, `caso_2_competitive_intelligence`), datos bajo `data/` y documentación por carpeta.

## Estructura

| Ruta | Contenido |
|------|-----------|
| [`caso_1_operaciones/`](caso_1_operaciones/) | Bot Streamlit, motor de insights, generación de informe ejecutivo |
| [`caso_2_competitive_intelligence/`](caso_2_competitive_intelligence/) | Pipeline de *competitive intelligence* (demo + scrape Playwright + informe) |
| [`data/caso_1_operaciones/`](data/caso_1_operaciones/) | CSV operativos del caso 1 |
| [`data/caso_2_competitive_intelligence/output/`](data/caso_2_competitive_intelligence/output/) | CSV de scrape; **`scrape_latest.csv`** es el dataset fusionado entregado (ver README del caso 2) |
| [`docs/`](docs/) | Notas opcionales |
| [`.env.example`](.env.example) | Plantilla de variables (API key, Playwright, proxy, etc.) |

Cada caso tiene su **`README.md`** con alcance, comandos y notas de entrega.

## Requisitos

- Python **3.11+**
- Desde la raíz: `pip install -r requirements.txt`
- **Caso 1:** `OPENAI_API_KEY` en `.env` (no subir `.env` a git)
- **Caso 2 (scrape real):** `playwright install firefox` (recomendado; Chromium a veces muestra Uber “coming soon”)

---

## Caso 1 — Operaciones

Resumen: asistente analítico sobre órdenes y métricas con Streamlit e informe Markdown/HTML.

```powershell
cd caso_1_operaciones
streamlit run operaciones/app.py
python -m operaciones.generate_report
```

Detalle: [`caso_1_operaciones/README.md`](caso_1_operaciones/README.md).

---

## Caso 2 — Competitive Intelligence

Resumen: CSV esquematizado (20 direcciones MX × plataformas × productos), informe con figuras, y scraper opcional sobre web pública (Rappi, Uber Eats, intento DiDi).

```powershell
cd caso_2_competitive_intelligence
python -m competitive_intel demo
python -m competitive_intel report
```

Scrape con Playwright (requiere red y navegador instalado):

```powershell
python -m competitive_intel scrape --browser firefox --platforms uber_eats,rappi
```

Dataset e informe de entrega, limitaciones y mitigaciones: [`caso_2_competitive_intelligence/README.md`](caso_2_competitive_intelligence/README.md).

---

## Entrega y repositorio

- No commitear: `.env`, `.venv/`, `didi_storage_state.json`, CSV intermedios en `output/` salvo lo indicado en `.gitignore`.
- **`scrape_latest.csv`** del caso 2 **sí** está pensado para versionarse como muestra del último merge de corridas.

```powershell
git add -A
git status
git commit -m "Entrega: READMEs, caso 2 documentado, scrape_latest.csv"
git push origin main
```

---

## Coste API

Solo **caso 1** usa OpenAI (`gpt-4o-mini`; orden de magnitud bajo por sesión). **Caso 2** no usa API en este repo.

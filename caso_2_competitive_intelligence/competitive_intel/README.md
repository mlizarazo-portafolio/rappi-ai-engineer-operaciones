# Competitive Intelligence (México)

Objetivo del brief: comparar **Rappi**, **Uber Eats** y **DiDi Food** en precios, fees, ETA y promos sobre ~20 direcciones.

## Archivos clave

| Archivo | Rol |
|---------|-----|
| `addresses_mx.json` | 20 ubicaciones + `zone_type` (justificación en campo `justification`) |
| `demo_scrape.py` | Genera CSV **sintético** con seed fija (pipeline + informe sin depender de anti-bot) |
| `report_ci.py` | Markdown + 3 PNG (ticket, fees, ETA) |
| `scrapers/` | Playwright: Rappi + Uber (+ intento DiDi); ver `scrapers/README.md` |

## Comandos

Ejecutar desde la carpeta **`caso_2_competitive_intelligence/`** (el padre de este paquete):

```bash
cd caso_2_competitive_intelligence
pip install -r ../requirements.txt   # desde raíz del monorepo, si aún no
playwright install chromium
python -m competitive_intel scrape --limit-addresses 2 --platforms rappi
python -m competitive_intel demo     # alternativa: CSV sintético
python -m competitive_intel report
```

Salida del informe en `competitive_intel/reports/` (ruta relativa a esta carpeta).

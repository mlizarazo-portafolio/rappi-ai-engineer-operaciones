# Competitive Intelligence (México)

Objetivo del brief: comparar **Rappi**, **Uber Eats** y **DiDi Food** en precios, fees, ETA y promos sobre ~20 direcciones.

## Archivos clave

| Archivo | Rol |
|---------|-----|
| `addresses_mx.json` | 20 ubicaciones + `zone_type` (justificación en campo `justification`) |
| `demo_scrape.py` | Genera CSV **sintético** con seed fija (pipeline + informe sin depender de anti-bot) |
| `report_ci.py` | Markdown + 3 PNG (ticket, fees, ETA) |
| `scrapers/README.md` | Cómo extender a Playwright real |

## Comandos

Ejecutar desde la carpeta **`caso_2_competitive_intelligence/`** (el padre de este paquete):

```bash
cd caso_2_competitive_intelligence
python -m competitive_intel demo
python -m competitive_intel report
```

Salida del informe en `competitive_intel/reports/` (ruta relativa a esta carpeta).

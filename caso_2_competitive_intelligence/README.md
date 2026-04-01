# Caso 2 — Competitive Intelligence

Aquí está **todo lo del segundo caso**: el enunciado y el paquete `competitive_intel/` (demo de datos + informe con gráficos).

| Archivo / carpeta | Qué es |
|-------------------|--------|
| `enunciado.md` | Brief del reclutador |
| `competitive_intel/` | Código (CLI, demo CSV, reporte, fixtures) |

El CSV generado por el demo va en **`../data/caso_2_competitive_intelligence/output/`** (raíz del monorepo).

## Comandos

Desde esta carpeta (`caso_2_competitive_intelligence/`):

```powershell
python -m competitive_intel demo
python -m competitive_intel report
```

Informe y figuras: `competitive_intel/reports/`.

Para un CSV fijo sin ejecutar `demo`, el informe puede leer `competitive_intel/fixtures/sample_scrape.csv`:

```powershell
python -m competitive_intel report -i competitive_intel/fixtures/sample_scrape.csv
```

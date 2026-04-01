# Caso 1 — Operaciones Rappi

Aquí está **todo lo del primer caso**: el enunciado original y el paquete Python `operaciones/` (bot + informe).

| Archivo / carpeta | Qué es |
|-------------------|--------|
| `enunciado.md` | Brief del reclutador |
| `operaciones/` | Código (Streamlit, tools, insights, `generate_report`) |

Los CSV están en la raíz del monorepo: **`data/caso_1_operaciones/`** (tres archivos). El `.env` con `OPENAI_API_KEY` va en la **raíz del monorepo**, no dentro de esta carpeta.

## Comandos

Desde esta carpeta (`caso_1_operaciones/`):

```powershell
streamlit run operaciones/app.py
python -m operaciones.generate_report
```

Los informes Markdown/HTML se escriben en **`../reports/`** (carpeta `reports` en la raíz del repo).

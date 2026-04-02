# Caso 1 — Operaciones Rappi

Entrega del **primer caso técnico**: enunciado, código del asistente analítico y generación de informe ejecutivo.

## Contenido de esta carpeta

| Ruta | Descripción |
|------|-------------|
| `enunciado.md` | Brief original del reclutador |
| `operaciones/` | Paquete Python: app Streamlit, *tools*, motor de insights, `generate_report` |

## Datos

Los CSV viven en la raíz del monorepo:

- `data/caso_1_operaciones/RAW_INPUT_METRICS.csv`
- `data/caso_1_operaciones/RAW_ORDERS.csv`
- `data/caso_1_operaciones/RAW_SUMMARY.csv`

## Configuración

Crea `.env` en la **raíz del monorepo** (no dentro de `caso_1_operaciones/`) con:

```env
OPENAI_API_KEY=tu_clave
```

Plantilla: `../.env.example` desde aquí, o `.env.example` en la raíz del repo.

## Comandos

Desde `caso_1_operaciones/`:

```powershell
streamlit run operaciones/app.py
python -m operaciones.generate_report
```

También puedes lanzar Streamlit desde la raíz del repo:

```powershell
streamlit run caso_1_operaciones/operaciones/app.py
```

## Salidas

- Informes generados: carpeta **`reports/`** en la raíz del monorepo (`insights_executive_*.{md,html}`).
- La carpeta `reports/` está en `.gitignore` salvo `.gitkeep`; regenera con `generate_report` si hace falta.

## Dependencias

Instalación global del monorepo (desde la raíz):

```powershell
pip install -r requirements.txt
```

# Rappi — caso Operaciones (AI Engineer)

Bot conversacional sobre métricas y órdenes (CSV) + generación automática de informe ejecutivo con insights (pandas).

## Estructura

| Ruta | Contenido |
|------|-----------|
| `docs/` | Datos (`RAW_*.csv`) y brief del caso |
| `operaciones/` | Código: Streamlit, herramientas de datos, motor de insights, informe |
| `reports/` | Salida al ejecutar `generate_report` (regenerable; carpeta vacía salvo `.gitkeep`) |

## Requisitos

- Python 3.11+
- Cuenta OpenAI con API key (solo para el bot)

## Configuración

1. Clona o descomprime el proyecto.
2. Crea el entorno e instala dependencias:

```powershell
cd RappiAIEngineer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Copia `.env.example` a `.env` y define `OPENAI_API_KEY`.

## Uso

**Bot (interfaz web):**

```powershell
streamlit run operaciones/app.py
```

**Informe de insights (Markdown + HTML):**

```powershell
python -m operaciones.generate_report
```

Los archivos aparecen en `reports/`. Para PDF: abre el `.html` en el navegador → Imprimir → Guardar como PDF.

## Coste API (orientativo)

Modelo: `gpt-4o-mini`. Precios oficiales en [OpenAI Pricing](https://platform.openai.com/pricing). Una sesión de ~10 preguntas suele ser **orden de USD 0.05–0.15** según longitud del historial; el informe **no** usa la API.

## Datos

Según el enunciado se usan **los tres archivos** en `docs/`:

- `RAW_INPUT_METRICS.csv` — métricas por zona y semana (`L0W_ROLL`…`L8W_ROLL`).
- `RAW_ORDERS.csv` — volumen de órdenes (`L0W`…`L8W`).
- `RAW_SUMMARY.csv` — diccionario de columnas; se inyecta en el contexto del bot y en el apéndice del informe.

**Ideas de preguntas para la demo:** top zonas por Lead Penetration en MX; comparar Perfect Orders Wealthy vs Non Wealthy en MX; tendencia de Gross Profit UE en Chapinero; promedio Lead Penetration por país; zonas con alto Lead Penetration y bajo Perfect Orders; crecimiento de órdenes últimas 5 semanas con contexto de métricas.

## Limitaciones

- Cambios porcentuales muy extremos cuando la semana base (L1) está cerca de cero.
- Sin gráficos en el bot ni export CSV desde la UI (bonus opcional del brief).

## Publicar en GitHub

Repo vacío en GitHub, luego:

```powershell
git remote add origin https://github.com/USUARIO/REPO.git
git push -u origin main
```

No subir `.env` ni `.venv` (están en `.gitignore`).

# RappiAIEngineer

Caso técnico **Operaciones** (Rappi AI Engineer): bot conversacional sobre CSV de métricas y órdenes + **informe ejecutivo automático** (insights con reglas en pandas).

## Estructura del repo

| Ruta | Contenido |
|------|-----------|
| `docs/` | CSV del caso + briefs; checklist de demo (`demo_checklist_operaciones.md`) |
| `operaciones/` | App Streamlit, motor de datos/tools, insights, generador de informe |
| `reports/` | Salida de `generate_report` (`.md`, `.html`) — regenerable |
| `plan/` | Plan de acción detallado |
| `StepByStepOperaciones/` | Notas fase por fase |

## Requisitos

- Python 3.11+ (probado con 3.13)
- Cuenta OpenAI con API key (solo para el bot, no para el informe de insights)

## Variables de entorno

| Variable | Obligatoria | Uso |
|----------|-------------|-----|
| `OPENAI_API_KEY` | Sí, para el bot | Modelo `gpt-4o-mini` + function calling |

Copia `.env.example` a `.env` en la **raíz del repo** y pega tu clave.

## Setup

```powershell
cd C:\Users\Malelizarazo\Desktop\RappiAIEngineer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si en Windows `pip install` falla con **WinError 32** (archivo en uso), cierra procesos que usen `.venv` o recrea el entorno virtual.

## Ejecutar el bot (Fase 1)

```powershell
streamlit run operaciones/app.py
```

El script ajusta `sys.path` para importar el paquete `operaciones` aunque Streamlit ejecute desde la subcarpeta.

## Generar informe de insights (Fase 2)

```powershell
python -m operaciones.generate_report
```

Salida en `reports/insights_executive_<timestamp>.md` y `.html`. El HTML renderiza Markdown (tablas, títulos). **PDF:** abre el `.html` en el navegador → **Imprimir → Guardar como PDF**.

## Coste estimado (OpenAI)

Modelo por defecto: **`gpt-4o-mini`** (`operaciones/chat.py`).

Precios de referencia (sujetos a cambio; confirma en [OpenAI Pricing](https://platform.openai.com/pricing)): del orden de **USD 0.15 / 1M tokens de entrada** y **USD 0.60 / 1M de salida**.

Orden de magnitud para esta app:

- Cada turno envía system prompt, definición de herramientas, historial y a veces **varias** rondas tool → salida. Típicamente **unos pocos miles de tokens de entrada** y **cientos de salida** por pregunta compleja.
- **Sesión de ~10 preguntas:** suele quedar **por debajo de USD 0.05–0.15** en muchos casos; si el historial crece mucho, sube. Revisa el **usage** en el dashboard de OpenAI tras ensayar la demo.

El informe `generate_report` **no llama a la API** (solo pandas).

## Datos

- `docs/RAW_INPUT_METRICS.csv`
- `docs/RAW_ORDERS.csv`

(Anonimizados/randomizados según el brief; no son cifras operativas reales.)

## Demo y presentación

Checklist pre-demo (preguntas sugeridas y guion): **`docs/demo_checklist_operaciones.md`**.

Resumen de fases: `StepByStepOperaciones/` y `plan/plan_operaciones.md`.

## Limitaciones conocidas

- Porcentajes de cambio semanal muy grandes cuando el denominador (L1) está cerca de cero.
- Sin gráficos automáticos en el bot ni export CSV desde la UI (bonus del brief).
- Sin despliegue en nube requerido; corre en `localhost`.

## Licencia / uso

Ejercicio de reclutamiento; datos y enfoque según brief Rappi en `docs/`.

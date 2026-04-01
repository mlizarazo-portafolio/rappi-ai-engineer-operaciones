# Fase 1 — Bot conversacional (implementación inicial)

**Fecha:** 2026-03-31  
**Plan:** `plan/plan_operaciones.md` § Fase 1

---

## Arquitectura elegida

**Opción B — Agente + herramientas (pandas):** el modelo (`gpt-4o-mini` por defecto) decide cuándo llamar funciones que ejecutan **solo** código sobre los CSV; los números no salen del “aire”.

- Definición de tools: `operaciones/tool_schemas.py`
- Implementación: `operaciones/tools.py` (`ToolExecutor`)
- Bucle OpenAI: `operaciones/chat.py` (`run_chat_turn` + `SYSTEM_PROMPT`)
- UI: `operaciones/app.py` (Streamlit, memoria vía `st.session_state.api_messages`)

---

## Archivos añadidos / raíz

| Ruta | Rol |
|------|-----|
| `requirements.txt` | pandas, streamlit, openai, python-dotenv, tabulate |
| `.env.example` | Plantilla `OPENAI_API_KEY` |
| `README.md` | Setup y comando Streamlit |
| `.gitignore` | `.venv/`, `.env` |

---

## Herramientas expuestas al LLM

1. `list_available_metrics` — nombres exactos de `METRIC`
2. `top_zones_by_metric` — ranking por semana (default `L0W_ROLL`)
3. `compare_zone_types` — Wealthy vs Non Wealthy por país
4. `metric_trend_for_zone` — serie L8…L0 para una zona (búsqueda parcial, ej. Chapinero)
5. `average_metric_by_country`
6. `zones_high_metric_low_metric` — alto en una métrica y bajo en otra (P75/P25)
7. `top_growing_orders_zones` — crecimiento órdenes L0W vs L{n}W + contexto de métricas (sin afirmar causalidad)
8. `problematic_zones` — caída fuerte L1→L0 (sinónimo de “zonas problemáticas” en el system prompt)

Alias de métricas/países: `operaciones/tools.py` (`METRIC_ALIASES`, `COUNTRY_ALIASES`, `resolve_metric`).

---

## Requisitos del brief (checklist)

| Requisito | Estado |
|-----------|--------|
| Filtro / ranking (Lead Penetration, etc.) | Cubierto con `top_zones_by_metric` |
| Comparación Wealthy / Non Wealthy (ej. Perfect Orders, MX) | `compare_zone_types` |
| Tendencia 8 semanas (ej. Gross Profit UE, Chapinero) | `metric_trend_for_zone` |
| Promedio por país | `average_metric_by_country` |
| Alto X y bajo Y | `zones_high_metric_low_metric` |
| Crecimiento órdenes + narrativa con métricas | `top_growing_orders_zones` |
| Contexto negocio (“zonas problemáticas”) | `problematic_zones` + instrucciones en `SYSTEM_PROMPT` |
| Sugerencias proactivas | Botones en sidebar (`SUGGESTIONS` en `app.py`) |
| Memoria conversacional | Historial completo en `api_messages` (OpenAI) |

**Bonus gráficos / export CSV:** no implementados en esta iteración.

---

## Cómo probar

```powershell
cd C:\Users\Malelizarazo\Desktop\RappiAIEngineer
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Configurar .env con OPENAI_API_KEY
streamlit run operaciones/app.py
```

Exploración sin LLM (smoke test de herramientas):

```powershell
.\.venv\Scripts\python.exe -c "from operaciones.data import load_metrics, load_orders; from operaciones.tools import ToolExecutor; e=ToolExecutor(load_metrics(), load_orders()); print(e.compare_zone_types('Perfect Orders','MX'))"
```

---

## Nota entorno Windows

Si `pip install` devuelve **WinError 32** o `pandas` queda a medias, suele ser un proceso bloqueando `.venv` (IDE, antivirus). Cierra terminales/otras apps que usen ese Python o borra `.venv`, créalo de nuevo y ejecuta `pip install -r requirements.txt` en una consola sin otros usos del venv.

---

## Siguiente paso (Fase 2)

Sistema de insights automáticos + reporte Markdown/HTML (`plan_operaciones.md` § Fase 2).

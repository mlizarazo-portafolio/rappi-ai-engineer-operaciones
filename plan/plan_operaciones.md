# Plan de acción — Caso Operaciones (Bot + Insights automáticos)

**Brief:** `docs/caso_operaciones_rappi.md`  
**Datos:** `docs/RAW_INPUT_METRICS.csv`, `docs/RAW_ORDERS.csv`  
**Orden recomendado si haces ambos casos:** empezar por este.

---

## Objetivo de entrega

| Peso | Entregable |
|------|------------|
| **70%** | Bot conversacional: NL → respuestas sobre métricas y órdenes, con contexto de negocio, sugerencias y memoria. |
| **30%** | Sistema de insights automáticos → reporte ejecutivo (Markdown/HTML/PDF). |

**Presentación:** ~30 min (demo en vivo del bot obligatoria según brief).

---

## Fase 0 — Entender datos (0.5–1 día)

**Avance:** completada — detalle en `StepByStepOperaciones/fase_0.md` y script `StepByStepOperaciones/scripts/explore_phase0.py`.

- [x] Abrir ambos CSV en pandas/notebook: contar filas, países, zonas únicas, métricas distintas (`METRIC`).
- [x] **Normalizar semanas:** en `RAW_INPUT_METRICS` las columnas son `L8W_ROLL` … `L0W_ROLL` (no `L8W_VALUE` del texto del caso). En `RAW_ORDERS`: `L8W` … `L0W`. Documentar en README el mapeo L8W = hace 8 semanas, L0W = semana actual.
- [x] Definir **join** lógico: `COUNTRY`, `CITY`, `ZONE` entre métricas y órdenes (validar que todas las zonas con órdenes existan en métricas o viceversa).
- [x] Crear vista unificada opcional: tabla ancha por zona + métrica con series semanales, o dos tablas que el bot consulte según la pregunta.

**Criterio de salida:** un script o notebook que carga datos sin errores y lista dimensiones clave.

---

## Fase 1 — Diseño del bot (70%) — 1–1.5 días

**Avance:** implementación inicial en `operaciones/` + detalle en `StepByStepOperaciones/fase_1.md`. UI: `streamlit run operaciones/app.py`.

### 1.1 Arquitectura (elige una y documéntala)

- **Opción A — Text-to-SQL:** esquema fijo en SQLite/duckdb cargado desde CSV; el LLM genera SQL acotado (solo `SELECT`, tablas permitidas).
- **Opción B — Agente + herramientas:** el modelo llama funciones que ejecutan pandas predefinidas (`top_zones_by_metric`, `compare_zone_types`, `orders_trend`, etc.).
- **Opción C — Híbrido:** clasificador de intención + plantillas pandas para preguntas frecuentes + LLM para reformular resultados.

**Recomendación pragmática:** B o C minimizan alucinaciones de SQL y son fáciles de testear.

**Elegido:** **B** — `ToolExecutor` + OpenAI function calling (`operaciones/tools.py`, `tool_schemas.py`, `chat.py`).

### 1.2 Casos de uso mínimos del brief (checklist)

Implementar y **probar con preguntas literales y variaciones**:

- [x] **Filtro / ranking:** p. ej. top 5 zonas por `% Lead Penetration` (o métrica equivalente en tus datos) “esta semana” → usar `L0W_ROLL` o `L0W`.
- [x] **Comparación:** Perfect Order (o `Perfect Orders` en CSV) entre `Wealthy` y `Non Wealthy` en México (`COUNTRY == MX`).
- [x] **Tendencia:** evolución de `Gross Profit UE` en zona tipo Chapinero (ajustar al nombre exacto en `ZONE` del CSV) últimas 8 semanas.
- [x] **Agregación:** promedio de Lead Penetration por país.
- [x] **Multivariable:** zonas con alto Lead Penetration y bajo Perfect Order (definir umbrales percentiles o top/bottom cuartil).
- [x] **Inferencia / narrativa:** zonas con mayor crecimiento de órdenes últimas 5 semanas + posible explicación usando métricas de esas zonas (correlación simple o bullet points con datos, sin pretender causalidad fuerte).

### 1.3 Requisitos UX del brief

- [x] **Contexto de negocio:** sinónimos (“zonas problemáticas” → métricas bajas o deterioro; documentar reglas en prompt o en código).
- [x] **Sugerencias proactivas:** 2–4 prompts sugeridos al abrir el chat o tras cada respuesta.
- [x] **Memoria conversacional:** seguimiento del hilo (última zona, país, métrica mencionados).

### 1.4 Bonus (si alcanza tiempo)

- [ ] Gráficos (tendencias línea, comparaciones barras) cuando la pregunta lo pida.
- [ ] Exportar tabla resultado a CSV.

**Criterio de salida:** demo en vivo con ≥5 preguntas de tipos distintos respondiendo bien.

---

## Fase 2 — Insights automáticos (30%) — 0.5–1 día

**Avance:** `python -m operaciones.generate_report` → `reports/*.md` y `.html`. Código: `insights_engine.py`, `report_markdown.py`, `generate_report.py`. Ver `StepByStepOperaciones/fase_2.md`.

### 2.1 Reglas mínimas (pandas)

- [x] **Anomalías:** variación semana a semana >10% entre `L1W` y `L0W` (u otras parejas consecutivas) por zona/métrica.
- [x] **Tendencias preocupantes:** mismo indicador empeorando 3+ semanas seguidas (comparar `L0W` vs `L1W` vs `L2W` …).
- [x] **Benchmarking:** parejas de zonas mismo `COUNTRY` y `ZONE_TYPE` con divergencia grande en una métrica clave.
- [x] **Correlaciones:** p. ej. Lead Penetration vs Non-Pro PTC > OP CVR a nivel zona (Spearman/Pearson con advertencia de no causalidad).
- [x] **Oportunidades:** zonas priorizadas con buen volumen (órdenes) y margen/mejorables según reglas simples.

### 2.2 Reporte ejecutivo

- [x] Resumen top 3–5 hallazgos críticos.
- [x] Detalle por categoría (anomalías, tendencias, benchmarking, correlaciones, oportunidades).
- [x] Recomendación accionable por hallazgo.
- [x] Salida: Markdown o HTML (y PDF opcional vía pandoc/print).

**Criterio de salida:** un comando o script `generate_report.py` que escribe el archivo final.

---

## Fase 3 — Empaquetado y demo

**Avance:** `README.md` ampliado; coste API documentado; checklist `docs/demo_checklist_operaciones.md`; notas `StepByStepOperaciones/fase_3.md`.

- [x] **README:** setup, variables de entorno (API keys), `pip install`, cómo lanzar UI y cómo generar reporte.
- [x] **Coste estimado** si usas API de LLM (por sesión / 10 preguntas).
- [x] **Pruebas:** lista fija de preguntas en `tests/` o markdown que ejecutas antes de la presentación.
- [x] Ensayo de presentación según estructura del brief (contexto, demo bot, insights, decisiones técnicas, limitaciones).

---

## Riesgos y mitigación

| Riesgo | Mitigación |
|--------|------------|
| Nombres de zona/métrica distintos al ejemplo del brief | Usar búsqueda fuzzy o listar zonas disponibles al usuario cuando no haya match exacto. |
| Alucinaciones del LLM | Preferir herramientas que ejecuten código sobre datos reales; validar números contra pandas. |
| Tiempo | Priorizar casos de uso obligatorios antes de bonus y UI pulida. |

---

## Orden de tareas en un día intenso (resumen)

1. Carga + join CSV + diccionario de columnas en README.  
2. Esqueleto UI (Streamlit/Gradio) + una herramienta pandas que responda una pregunta tipo ranking.  
3. Cubrir los 6 tipos de pregunta del brief.  
4. Insights + reporte Markdown.  
5. README + ensayo demo.

# Checklist pre-demo — caso Operaciones

Usar antes de la presentación en vivo (~30 min según brief).

## Entorno

- [ ] `.\.venv\Scripts\Activate.ps1` y `pip install -r requirements.txt` sin errores.
- [ ] Archivo `.env` con `OPENAI_API_KEY` válida (no commiteada).
- [ ] `streamlit run operaciones/app.py` abre sin error en el navegador.
- [ ] `python -m operaciones.generate_report` genera `.md` y `.html` en `reports/`.
- [ ] Último informe HTML se ve bien (tablas renderizadas); PDF de respaldo si quieres: Imprimir → Guardar como PDF.

## Datos

- [ ] Existen `docs/RAW_INPUT_METRICS.csv` y `docs/RAW_ORDERS.csv`.

## Preguntas mínimas para la demo del bot (≥5 tipos distintos)

Marcar al probar que la respuesta usa datos coherentes (tablas/números del CSV):

1. [ ] **Ranking / filtro:** ¿Cuáles son las 5 zonas con mayor Lead Penetration esta semana en México?
2. [ ] **Comparación Wealthy / Non Wealthy:** Compara Perfect Orders entre zonas Wealthy y Non Wealthy en México.
3. [ ] **Tendencia 8 semanas:** Muestra la evolución de Gross Profit UE en Chapinero las últimas 8 semanas.
4. [ ] **Agregación por país:** ¿Cuál es el promedio de Lead Penetration por país?
5. [ ] **Multivariable:** ¿Qué zonas tienen alto Lead Penetration pero bajo Perfect Orders?
6. [ ] **Órdenes + contexto:** ¿Cuáles son las zonas que más crecen en órdenes en las últimas 5 semanas y qué métricas las acompañan?
7. [ ] **Contexto de negocio:** ¿Qué zonas problemáticas hay en Gross Profit UE en Colombia? (o variante con “deterioro”).

## Insights automáticos

- [ ] Mostrar el informe reciente (`reports/*.html` o `.md` en editor).
- [ ] Saber explicar en 1 frase cada bloque: anomalías, tendencias, benchmarking, correlación, oportunidades.
- [ ] Mencionar limitación: datos sintéticos; % extremos por denominadores cercanos a cero.

## Guion sugerido (20 min + Q&A)

1. Contexto y approach (3 min).
2. Demo del bot con al menos 5 preguntas de la lista (10 min).
3. Informe de insights y 2–3 hallazgos que elijas (5 min).
4. Decisiones técnicas: agente + tools, `gpt-4o-mini`, Streamlit, pandas puro en insights (5 min).
5. Limitaciones y próximos pasos (2 min).

## Plan B

- [ ] Si falla la API o la red: capturas o informe + Markdown ya generado listos para mostrar.

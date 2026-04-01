# Plan de acción — Caso Competitive Intelligence (Scraping + Informe)

**Brief:** `docs/caso_competitive_intelligence_rappi.md`  
**Datos:** los generas tú (scraping/API); salida mínima CSV o JSON.  
**Orden recomendado si haces ambos casos:** después de validar acceso a plataformas (o en paralelo solo la validación al inicio).

---

## Objetivo de entrega

| Peso | Entregable |
|------|------------|
| **70%** | Sistema automatizado: Rappi + **2 competidores** (p. ej. Uber Eats, DiDi Food) en **México**, **20–50 direcciones**, ≥**3 métricas**, ejecutable con un comando, salida CSV/JSON. |
| **30%** | Informe de insights: comparativo precios/tiempos/fees/promos, **top 5 insights** accionables, **≥3 visualizaciones**, formato ejecutivo. |

**Presentación:** datos pre-scrapeados como backup si el live falla.

---

## Fase 0 — Viabilidad (obligatoria, 2–4 h antes de codificar fuerte)

- [ ] **Prueba manual** (una dirección, un producto referencia): ¿ves precio, delivery fee, service fee, ETA, promos en **Rappi, Uber Eats y DiDi Food** desde México?
- [ ] Decidir **canal:** web (Playwright/Selenium), app emulada, o endpoints no oficiales si los documentas.
- [ ] Revisar **robots.txt / ToS** y documentar approach ético (rate limit, user-agent, sin saturar servidores).

**Criterio de salida:** decisión explícita de qué plataforma/métrica es viable; si algo falla, scope reducido documentado (menos direcciones o menos métricas).

---

## Fase 1 — Scope de productos y geografía

### 1.1 Productos de referencia (brief)

Elegir **pocos ítems comparables** entre apps (mismo restaurante cadena cuando sea posible):

- Fast food: Big Mac / Whopper, combo mediano, nuggets.
- Retail (bonus): Coca-Cola 500 ml, agua 1L, etc.

**Regla:** mejor **3–5 SKUs bien comparados** que muchos mal enlazados.

### 1.2 Direcciones (20–50)

- [ ] Lista en CSV/JSON: dirección o coordenadas + etiqueta (centro, periferia, zona prioritaria, etc.).
- [ ] **Justificación** en README o anexo: cobertura de tipos de zona.
- [ ] Si el tiempo aprieta: **mínimo viable** con menos direcciones pero justificación clara (el brief valora calidad sobre cantidad).

---

## Fase 2 — Implementación del scraper (70%)

### 2.1 Estructura del proyecto

- [ ] Módulo por plataforma (o por flujo) con interfaz común: `fetch_quote(address, product_query) -> dict`.
- [ ] Config externa: lista de direcciones, lista de productos, credenciales/proxies si aplica (sin commitear secretos).

### 2.2 Campos mínimos sugeridos en el output

Alineados al brief (rellenar null si no disponible):

- `platform`, `scraped_at`, `address_id`, `lat`, `lon` (si aplica)
- `restaurant_name`, `product_name`
- `item_price`, `delivery_fee`, `service_fee`, `total_checkout` (si aplica)
- `eta_min`, `eta_max` o texto parseado
- `promotions_visible` (texto o flags)
- `availability` (abierto/cerrado, ítem disponible)

### 2.3 Robustez (valorado en rúbrica)

- [ ] Rate limiting y delays aleatorios.
- [ ] Reintentos con backoff ante timeout / 5xx.
- [ ] Logging: éxito/fallo por dirección y por plataforma.
- [ ] Manejo de “producto no encontrado” / tienda cerrada sin romper el batch.

### 2.4 Ejecución

- [ ] Un comando documentado: `python run_scrape.py` o `make scrape`.
- [ ] Artefacto: `data/raw_scrape_YYYYMMDD.csv` (o JSON lines).

### 2.5 Bonus (opcional)

- [ ] Misma tienda cruzada entre plataformas.
- [ ] Screenshots de evidencia por scrape.
- [ ] Segunda vertical (retail/farma).

---

## Fase 3 — Informe e insights (30%)

### 3.1 Análisis comparativo (brief)

- [ ] Posicionamiento de precios: Rappi vs competencia por zona/agregado.
- [ ] Tiempos de entrega comparados.
- [ ] Estructura de fees (delivery + service).
- [ ] Estrategia promocional visible por plataforma.
- [ ] Variabilidad geográfica (heatmap o tabla por `address_id`).

### 3.2 Top 5 insights accionables

Cada uno con:

1. **Finding**  
2. **Impacto**  
3. **Recomendación** para Rappi  

### 3.3 Visualizaciones (≥3)

- Barras: precio total o fee por plataforma.
- Heatmap o facetas: métrica por zona.
- Otra: promos, ETA, etc.

Herramientas libres: Python (matplotlib/seaborn/plotly), export PNG/HTML para deck/PDF.

### 3.4 Formato

- [ ] PDF, PowerPoint, Notion o **dashboard** (Streamlit/Plotly como bonus).

---

## Fase 4 — Repositorio y demo

- [ ] **README:** dependencias, cómo ejecutar scrape, cómo regenerar informe, costos de proxies/APIs, limitaciones y bloqueos encontrados.
- [ ] Datos de ejemplo commiteados o muestra anonimizada (sin PII real si usas direcciones sensibles).
- [ ] **Plan B:** archivo CSV de última corrida exitosa para la presentación.
- [ ] Estructura sugerida del brief: approach, demo (o grabación), datos, top insights, decisiones técnicas, limitaciones.

---

## Riesgos y mitigación

| Riesgo | Mitigación |
|--------|------------|
| Bloqueos / CAPTCHA | Proxies rotativos o throttling; documentar; no penalizan diseño sólido según FAQ del caso. |
| Selectores frágiles | Selectores relativos, tests en 2–3 direcciones, versionado de “snapshots” HTML para debug. |
| Comparabilidad de productos | Misma cadena y SKU lo más parecido posible; documentar cuando la comparación es aproximada. |
| Tiempo vs 50 direcciones | Priorizar pipeline estable con N menor antes de escalar N. |

---

## Orden sugerido si trabajas ambos casos

1. **Mismo día 1:** Fase 0 de este plan (validación) en paralelo mental con el arranque del caso Operaciones.  
2. Cuando Operaciones tenga MVP: **Fases 1–2** aquí (scope + scraper estable).  
3. **Fase 3–4** informe + README + backup para demo.

---

## Checklist rápido pre-entrega

- [ ] 3 plataformas contempladas (Rappi + 2 competidores).  
- [ ] ≥3 métricas distintas en el dataset.  
- [ ] 20–50 direcciones documentadas (o menos con justificación fuerte).  
- [ ] Comando único de ejecución.  
- [ ] CSV/JSON + informe con 3 gráficos + 5 insights.  
- [ ] README reproducible + notas legales/éticas.

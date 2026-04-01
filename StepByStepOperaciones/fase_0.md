# Fase 0 — Entender datos (completada)

**Fecha:** 2026-03-31  
**Plan de referencia:** `plan/plan_operaciones.md`  
**Datos:** `docs/RAW_INPUT_METRICS.csv`, `docs/RAW_ORDERS.csv`

---

## Checklist del plan

| Tarea | Estado |
|-------|--------|
| Abrir ambos CSV en pandas: filas, países, zonas únicas, métricas (`METRIC`) | Hecho |
| Documentar mapeo de semanas (L8W…L0W) vs nombres del brief | Hecho |
| Validar join `COUNTRY`, `CITY`, `ZONE` entre métricas y órdenes | Hecho |
| Vista unificada: decisión de modelado para el bot | Hecho (recomendación abajo) |
| Script que carga sin errores y lista dimensiones clave | Hecho: `scripts/explore_phase0.py` |

---

## Qué se hizo

1. Se añadió el script **`StepByStepOperaciones/scripts/explore_phase0.py`**, que carga los dos CSV desde la raíz del repo y imprime resúmenes.
2. Se ejecutó con:  
   `python StepByStepOperaciones/scripts/explore_phase0.py`

---

## Mapeo de semanas (brief vs archivos reales)

El caso en `docs/caso_operaciones_rappi.md` habla de `L8W_VALUE` … `L0W_VALUE` en el dataset de métricas. En los CSV que tienes:

| Dataset | Columnas de semanas | Significado |
|---------|---------------------|-------------|
| **RAW_INPUT_METRICS** | `L8W_ROLL`, `L7W_ROLL`, …, `L1W_ROLL`, `L0W_ROLL` | **L0W** = semana actual (más reciente); **L8W** = hace 8 semanas. |
| **RAW_ORDERS** | `L8W`, `L7W`, …, `L1W`, `L0W` | Misma convención: **L0W** actual, **L8W** hace 8 semanas. |

**“Esta semana”** en preguntas del bot → usar **`L0W_ROLL`** (métricas) o **`L0W`** (órdenes).

---

## Dimensiones clave (resultados del script)

### RAW_INPUT_METRICS

| Medida | Valor |
|--------|------:|
| Filas | 12.573 |
| Ciudades únicas (`CITY`) | 270 |
| Zonas únicas (`COUNTRY` + `CITY` + `ZONE`) | 980 |
| Métricas distintas (`METRIC`) | 13 |
| `ZONE_TYPE` | `Wealthy`, `Non Wealthy` |
| `ZONE_PRIORITIZATION` | `High Priority`, `Prioritized`, `Not Prioritized` |
| Países (`COUNTRY`) | AR, BR, CL, CO, CR, EC, MX, PE, UY |

**Lista de métricas (`METRIC`):**

- % PRO Users Who Breakeven  
- % Restaurants Sessions With Optimal Assortment  
- Gross Profit UE  
- Lead Penetration  
- MLTV Top Verticals Adoption  
- Non-Pro PTC > OP  
- Perfect Orders  
- Pro Adoption (Last Week Status)  
- Restaurants Markdowns / GMV  
- Restaurants SS > ATC CVR  
- Restaurants SST > SS CVR  
- Retail SST > SS CVR  
- Turbo Adoption  

*(El brief menciona “Perfect Order”; en datos aparece **Perfect Orders**.)*

### RAW_ORDERS

| Medida | Valor |
|--------|------:|
| Filas | 1.242 |
| Zonas únicas (`COUNTRY`, `CITY`, `ZONE`) | 1.242 |
| `METRIC` | siempre `Orders` (según muestra y brief) |
| Países | mismos códigos que en métricas |

---

## Join `COUNTRY`, `CITY`, `ZONE`

| Conjunto | Cantidad |
|----------|----------:|
| Claves presentes en **ambos** datasets | **978** |
| Solo en **órdenes** (sin filas de métricas para esa zona) | **264** |
| Solo en **métricas** (sin fila de órdenes para esa zona) | **2** |

**Interpretación:** `RAW_ORDERS` cubre muchas zonas que no aparecen en el dataset de métricas (p. ej. agregados “Other” o zonas solo con volumen). Para el bot:

- Preguntas **solo de órdenes** → usar `RAW_ORDERS` completo.  
- Preguntas **métricas operacionales** → usar `RAW_INPUT_METRICS` (980 zonas).  
- Preguntas **combinadas** (ej. crecimiento de órdenes + explicación con métricas) → **inner join** en las 978 claves comunes, o left join desde órdenes y mostrar “sin métricas” donde falten.

---

## Valores nulos en series semanales

- **Métricas:** nulos bajos (~0.3%–0.9% en L8W–L1W; **0% en L0W_ROLL**).  
- **Órdenes:** ~**17%–20%** nulos por columna de semana (muchas zonas sin historia completa de 9 semanas).

El bot y los insights deben manejar `NaN` (no asumir siempre 8 semanas completas en órdenes).

---

## Zona tipo brief (“Chapinero”)

En métricas existe la clave:

| COUNTRY | CITY   | ZONE      |
|---------|--------|-----------|
| CO      | Bogota | Chapinero |

Sirve para la pregunta de evolución de **Gross Profit UE** en Chapinero (últimas 8 semanas).

---

## Vista unificada (decisión para fases siguientes)

No es obligatorio un solo DataFrame ancho gigante al inicio. Propuesta:

1. Cargar **`metrics`** y **`orders`** en memoria (o DuckDB con dos tablas).  
2. Helper `get_zone_key()` = `(COUNTRY, CITY, ZONE)` normalizado (strings strip).  
3. Para tendencias de órdenes: tabla `orders` tal cual.  
4. Para KPIs por zona/semana: tabla `metrics` en formato largo (opcional `melt` de `L8W_ROLL`…`L0W_ROLL`) si simplifica consultas del LLM o herramientas.

---

## Criterio de salida Fase 0

Cumplido: script reproducible, dimensiones documentadas, join y semanas aclarados, implicaciones para el bot anotadas.

**Siguiente paso (Fase 1):** elegir arquitectura del bot (p. ej. agente + herramientas pandas) e implementar el primer caso de uso.

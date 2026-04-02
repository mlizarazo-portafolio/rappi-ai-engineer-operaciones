# Caso 2 — Competitive Intelligence

Entrega del **segundo caso técnico**: sistema para comparar precios, fees y señales operativas entre plataformas (Rappi, Uber Eats, intento DiDi) sobre **web pública**, con CSV tabular, informe reproducible y scraper Playwright.

## Dataset entregado (CSV fusionado)

El archivo consolidado de la última corrida (posible fusión de ejecuciones Uber-only + Rappi-only o de otras pasadas con `merge-scrapes`) es:

| Ubicación en el repo | Ruta absoluta (tu máquina) |
|----------------------|----------------------------|
| `data/caso_2_competitive_intelligence/output/scrape_latest.csv` | `C:\Users\Malelizarazo\Desktop\RappiAIEngineer\data\caso_2_competitive_intelligence\output\scrape_latest.csv` |

- **Esquema:** 120 filas objetivo = 20 direcciones en México × 2 plataformas (filas `rappi` / `uber_eats`) × 3 productos tipo McDonald’s (Big Mac, Coca-Cola 600 ml, McNuggets 10).
- **Columnas:** ver `competitive_intel/scrapers/schema.py` (`item_price_mxn`, fees, ETA, promociones, etc.).
- **Nota:** La cobertura (cuántas celdas tienen precio) **depende de la red, rate limits y UI en vivo**. Para medirla de nuevo:

```powershell
python -c "import pandas as pd; df=pd.read_csv(r'data\caso_2_competitive_intelligence\output\scrape_latest.csv'); u=df[df.platform=='uber_eats']; r=df[df.platform=='rappi']; print('Uber con precio:', int(u.item_price_mxn.notna().sum()), '/ 60'); print('Rappi con precio:', int(r.item_price_mxn.notna().sum()), '/ 60')"
```

(Ejecutar desde la raíz del monorepo `RappiAIEngineer`.)

---

## Qué se encontró (hallazgos técnicos)

1. **Uber Eats — “We're coming soon”**  
   La web a veces no muestra la tienda según **IP / región**, aunque la URL sea `mx`. No es un bug de Playwright; en muchos entornos fuera de México la tienda no carga. **Firefox** embebido en Playwright a veces se comporta distinto a Chromium.

2. **Uber — solo la primera dirección parecía funcionar en corridas largas**  
   Se atribuyó a **estado de sesión / cookies** arrastradas entre pasos. Se mitigó limpiando cookies del contexto **antes de cada paso Uber** (`live_pipeline.py`; desactivable con `CI_SCRAPER_NO_UBER_COOKIE_CLEAR=1`).

3. **Falsos positivos de “rate limit” en Uber**  
   Inspeccionar `innerHTML` de la página disparaba coincidencias con texto dentro de bundles JS. Se ajustó la heurística a **`innerText`** u otro criterio más estricto (`rate_limit.py`).

4. **Rate limits reales (Rappi / Uber)**  
   Respuestas tipo error JSON o páginas de “demasiadas solicitudes”. Se añadieron **reintentos con backoff**, **delay configurable** (`--delay`), **pausa entre plataformas** (`CI_SCRAPER_PLATFORM_GAP_SEC`) y **jitter**.

5. **Rappi — cobertura más baja que Uber en la práctica**  
   Búsqueda de tienda (McDonald’s), selectores y límites del sitio hacen que muchas filas queden sin `item_price_mxn`. Se probó **limpieza de cookies antes de cada paso Rappi** (análogo a Uber; `CI_SCRAPER_NO_RAPPI_COOKIE_CLEAR=1` para desactivar).

6. **Consola Windows y Unicode**  
   Caracteres como `→` en logs rompían la salida en algunas codificaciones; se unificó a ASCII en mensajes de progreso (`->`, `...`).

7. **DiDi Food**  
   La web suele exigir **login** y sesión en México; sin credenciales el scrape es limitado. Hay flujo opcional `save-didi-session` y `PLAYWRIGHT_STORAGE_STATE` (ver `.env.example`).

8. **Dos navegadores en paralelo (Uber en una terminal, Rappi en otra)**  
   Puede **aumentar** rate limiting; es opcional. Scripts en `scripts/*.ps1`.

---

## Cómo se intentó solucionar (resumen de implementación)

| Problema | Enfoque |
|----------|---------|
| Uber bloqueado por región | Documentación `LIMITACION_UBER_WEB.md`; Firefox; VPN/proxy MX; `PLAYWRIGHT_PROXY`, `UBER_EATS_URL` |
| Sesión Uber degradada entre ciudades | `context.clear_cookies()` antes de cada bloque `uber_eats` |
| Rate limit / throttling | `rate_limit.py`, delays, gap entre plataformas, reintentos en `uber_playwright.py` / `rappi_playwright.py` |
| Rappi inestable | Delays mayores, cookie clear por paso, nueva pestaña por plataforma en el pipeline |
| Corridas parciales o plataformas separadas | `--limit-addresses`, `--skip-addresses`; `merge-scrapes` que **prioriza filas con precio** |
| Paralelo Uber / Rappi | `scripts/scrape_uber_only.ps1`, `scrape_rappi_only.ps1`, `merge_parallel_scrapes.ps1` |

Documentación operativa adicional: **`PLAN_MEJORA_DATOS_REALES.md`** (objetivo ~75% cobertura, comandos, checklist).

---

## Estructura de código

| Ruta | Rol |
|------|-----|
| `enunciado.md` | Brief del reclutador |
| `competitive_intel/` | CLI, demo, reporte, paths, `merge_scrapes.py` |
| `competitive_intel/addresses_mx.json` | 20 direcciones (ciudad, barrio, coords) |
| `competitive_intel/scrapers/` | Playwright: `live_pipeline`, `rappi_playwright`, `uber_playwright`, `didi_playwright`, `rate_limit`, etc. |
| `competitive_intel/reports/` | Informe Markdown + figuras (regenerables con `report`) |
| `scripts/` | PowerShell para scrapes paralelos por plataforma + merge |
| `LIMITACION_UBER_WEB.md` | Uber y región / VPN |
| `PLAN_MEJORA_DATOS_REALES.md` | Plan de cobertura y comandos avanzados |

---

## Comandos principales

Desde `caso_2_competitive_intelligence/`:

```powershell
playwright install firefox
```

**Sin red (demo sintético + informe):**

```powershell
python -m competitive_intel demo
python -m competitive_intel report
```

**Scrape real (ejemplo):**

```powershell
python -m competitive_intel scrape --browser firefox --platforms uber_eats,rappi --delay 6
```

**Ver navegador:**

```powershell
python -m competitive_intel scrape --browser firefox --platforms uber_eats,rappi --headed
```

**Fusionar dos CSV** (gana la fila con precio por `platform` + `address_id` + `product_name`):

```powershell
python -m competitive_intel merge-scrapes ruta\a.csv ruta\b.csv -o ..\data\caso_2_competitive_intelligence\output\scrape_latest.csv
```

**Informe leyendo el CSV entregado** (desde esta carpeta, rutas relativas al monorepo):

```powershell
python -m competitive_intel report -i ..\data\caso_2_competitive_intelligence\output\scrape_latest.csv
```

Detalle ético, flags y límites del scrape: **`competitive_intel/scrapers/README.md`**.

---

## Entrega y buenas prácticas

- Uso razonable de las webs públicas, volumen bajo, revisar términos de cada plataforma.
- No subir `.env` ni archivos de sesión con cookies personales (`didi_storage_state.json` en `.gitignore`).
- Los CSV en `output/` distintos de `scrape_latest.csv` siguen ignorados por git salvo que se force; el **artefacto de entrega versionado** es `scrape_latest.csv`.

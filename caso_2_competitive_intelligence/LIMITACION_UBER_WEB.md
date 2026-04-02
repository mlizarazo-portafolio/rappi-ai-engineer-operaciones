# Uber Eats — pantalla “We're coming soon”

## Qué pasa

Al abrir `https://www.ubereats.com/mx-en/` (o variantes) **a veces** aparece:

**“We're coming soon”** — *“We are always expanding our coverage area…”*

Eso **no es un fallo de Playwright**. Uber decide según **IP / región / política web** si te muestra la tienda real o esa pantalla. Desde muchos países **fuera de México** la web de pedidos **no está disponible**, aunque la URL lleve `mx`.

## Cómo comprobarlo

Abre la **misma URL en Chrome normal** en tu PC. Si ves lo mismo, el scraper **no podrá** encontrar el input de dirección.

## Qué hacer (orden recomendado)

1. **Probar el scrape con Firefox (Playwright)** — a veces Uber sirve la tienda en Firefox y “Coming soon” en Chromium:  
   `playwright install firefox`  
   `python -m competitive_intel scrape --browser firefox --limit-addresses 1 --platforms uber_eats --headed`  
   O en `.env`: `PLAYWRIGHT_BROWSER=firefox`  
   (No es el mismo binario que tu Firefox de escritorio; es el Firefox embebido en Playwright.)
2. **VPN con salida en México** y vuelve a probar + scrape.  
3. Variable **`PLAYWRIGHT_PROXY`** (ver `.env.example`): proxy HTTP/SOCKS con salida MX si tu VPN lo expone así.  
4. **Geolocalización**: el scrape concede por defecto ubicación en CDMX y el permiso `geolocation` (necesario para DiDi y útil en otras UIs). **No sustituye** un bloqueo por IP. Para desactivar: **`CI_SCRAPER_NO_GEOLOCATION=1`**.  
5. **`UBER_EATS_URL`**: URL alternativa si descubres una que cargue en tu red (probar manualmente antes).  
6. **Entrega / defensa:** documentar cobertura parcial — datos reales **Rappi** + Uber **no accesible desde entorno actual** + DiDi según corresponda.

## Referencia en código

- `competitive_intel/scrapers/uber_playwright.py` — intenta varias URLs y detecta texto “coming soon”.  
- `competitive_intel/scrapers/live_pipeline.py` — cabeceras, geolocalización, proxy opcionales; **una pestaña nueva por plataforma** para que Uber no herede estado de Rappi/DiDi.

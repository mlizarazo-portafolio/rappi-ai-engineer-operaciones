# Scrapers (Playwright) — uso apropiado

## Qué hace este código

Automatiza un **navegador real** (Chromium) contra las **webs públicas** de:

- **Rappi** (`rappi.com.mx`): entra a McDonald’s por ciudad (slug) y lee texto visible del menú.
- **Uber Eats** (`ubereats.com/mx-en/`): escribe dirección en el typeahead, busca “McDonald’s” y lee la página de tienda.
- **DiDi Food** (`didi-food.com`): intento limitado; muchas veces la experiencia empuja a la app, sin precios fiables en web.

Los precios y fees se obtienen con **heurísticas sobre el texto** (`text_extract.py`), no con APIs oficiales. Si la UI cambia, habrá que ajustar selectores o regex.

## Ética y legal

1. **APIs y acuerdos oficiales** son la vía preferida en producción (partners, datos licenciados).
2. **Términos de uso** de cada plataforma pueden restringir automatización; este código es para **demostración técnica / challenge** con **bajo volumen**.
3. **Robots.txt** y carga razonable: usa `--limit-addresses`, `--delay` y no ejecutes en bucle agresivo.
4. **Datos personales:** no recolectar cuentas ni cookies de sesión para otros fines.

## Instalación

```bash
pip install -r requirements.txt
playwright install chromium
```

## Comandos

Desde `caso_2_competitive_intelligence/`:

```bash
# Prueba rápida: 1 dirección, solo Rappi
python -m competitive_intel scrape --limit-addresses 1 --platforms rappi --headed

# Headless, tres plataformas (lento: 20 direcciones × 3)
python -m competitive_intel scrape --delay 2.5

# Si Playwright falla, CSV sintético
python -m competitive_intel scrape --fallback-demo
```

Salida por defecto: `data/caso_2_competitive_intelligence/output/scrape_latest.csv` (respetar `.gitignore` para corridas locales).

## Límites conocidos

- **Anti-bot / CAPTCHA / login**: puede bloquear; probar `--headed` o otra red.
- **Selectores**: Uber y Rappi cambian el front con frecuencia.
- **Fees totales**: a menudo solo visibles en checkout; el CSV puede tener `null` en delivery/service fee aunque el ítem tenga precio.
- **DiDi**: suele ser el más pobre en web; filas con `store_available=false` son esperables.

## Demo sintético

Si no necesitas datos reales: `python -m competitive_intel demo`.

## Roadmap para acercarse al enunciado (datos “de verdad”)

1. **APIs oficiales / partners:** Uber Eats, Rappi y DiDi exponen APIs orientadas a **restaurantes aliados** (menús, órdenes), no a un “panel competitivo” público. En una empresa real, CI suele combinar **datos propios**, **proveedores de datos** o acuerdos; no asumir que esas APIs cubren al competidor sin contrato.
2. **Geocodificación:** Resolver cada dirección del JSON a **lat/lon + place_id** (p. ej. Google Places / Mapbox) y usar la **misma coordenada** en las tres UIs (o deep links si existen) en lugar de solo texto “barrio, ciudad”.
3. **Interceptar red:** En Playwright, `page.on("response", …)` sobre JSON de feed/checkout de Uber/Rappi suele ser **más estable** que regex sobre `innerText` (cuando no vaya cifrado).
4. **Sesión / anti-bot:** `storage_state` con login de prueba (si el reclutador lo permite), user-agent real, `--headed` en depuración, ritmo humano; documentar límites legales.
5. **DiDi:** Valorar **Appium** sobre app real o aceptar cobertura parcial web + nota en el informe.
6. **Validación:** Reglas de sanidad en fees (como `fee_sanity.py`) + columna `confidence` / exclusiones en el informe.

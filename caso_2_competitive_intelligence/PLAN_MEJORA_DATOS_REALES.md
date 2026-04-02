# Plan: datos reales y cobertura ~75% (Rappi + Uber Eats)

## Qué tenemos hoy

| Área | Estado |
|------|--------|
| Orquestación Playwright (Uber → Rappi por dirección) | Implementado (`live_pipeline.py`) |
| Limpieza de cookies antes de cada paso Uber | Por defecto activa; `CI_SCRAPER_NO_UBER_COOKIE_CLEAR=1` para desactivar |
| Limpieza de cookies antes de cada paso Rappi | Por defecto activa; `CI_SCRAPER_NO_RAPPI_COOKIE_CLEAR=1` para desactivar |
| Pausa entre plataformas + jitter en delay | `CI_SCRAPER_PLATFORM_GAP_SEC`, `--delay` |
| Detección de rate limit (sin falsos positivos duros en Uber) | `rate_limit.py` |
| Reintentos / cooldown en Uber y Rappi | En scrapers respectivos |
| Geolocalización CDMX por defecto | Configurable vía `.env` |
| DiDi con sesión guardada | `save-didi-session` + `PLAYWRIGHT_STORAGE_STATE` (sigue dependiendo de login MX) |
| CLI: `scrape`, `report`, `demo`, `merge-scrapes` | `python -m competitive_intel …` |
| Corridas partidas | `--limit-addresses`, `--skip-addresses` |
| Fusión de CSV parciales | `merge-scrapes` prioriza filas con `item_price_mxn` |
| Scrapes en paralelo (Uber / Rappi) | Scripts en `scripts/scrape_uber_only.ps1`, `scrape_rappi_only.ps1`, `merge_parallel_scrapes.ps1` |

## Qué no tenemos (o es frágil)

| Área | Motivo |
|------|--------|
| Cobertura estable ~75% en **Rappi** sin tuning | UI cambiante, búsqueda McDonald’s, rate limits; suele necesitar delay alto y corridas en franjas distintas |
| DiDi sin login en México | La web exige cuenta; sin credenciales no hay precios fiables |
| Uber “coming soon” desde IP fuera de MX | VPN/proxy México (ver `LIMITACION_UBER_WEB.md`) |
| Garantía legal/comercial de scraping | Solo uso razonable de web pública; sin API oficial |

## Objetivo numérico

- Matriz de referencia: **20 ciudades × 2 plataformas × 3 productos = 120 filas**.
- **~75% por plataforma** ≈ **45/60 filas** con `item_price_mxn` no nulo (o, como proxy, **≥15/20 ciudades** con al menos un precio por plataforma).

## Estrategia recomendada (dividir trabajo + fusionar)

1. **Subir tiempos** para corridas largas: `--delay 6` (o 8–10 si hay rate limits), `CI_SCRAPER_PLATFORM_GAP_SEC=45` (o 60–90).
2. **Primera pasada** (todas las ciudades o mitad):
   - Desde la raíz del repo (o con `PYTHONPATH` apuntando a `caso_2_competitive_intelligence`):

   ```bash
   python -m competitive_intel scrape -o data/caso_2_competitive_intelligence/output/scrape_part_a.csv --platforms uber_eats,rappi --delay 6 --browser firefox
   ```

3. **Segunda mitad** (si partes en dos lotes de 10 direcciones):

   ```bash
   python -m competitive_intel scrape -o data/caso_2_competitive_intelligence/output/scrape_part_b.csv --platforms uber_eats,rappi --skip-addresses 10 --delay 6 --browser firefox
   ```

4. **Solo Uber** o **solo Rappi** si una plataforma falla en bloque (evita arrastrar errores):

   ```bash
   python -m competitive_intel scrape -o data/caso_2_competitive_intelligence/output/scrape_uber_only.csv --platforms uber_eats --delay 6
   python -m competitive_intel scrape -o data/caso_2_competitive_intelligence/output/scrape_rappi_only.csv --platforms rappi --delay 8
   ```

5. **Fusionar** conservando la mejor fila por `(platform, address_id, product_name)`:

   ```bash
   python -m competitive_intel merge-scrapes data/caso_2_competitive_intelligence/output/scrape_part_a.csv data/caso_2_competitive_intelligence/output/scrape_part_b.csv -o data/caso_2_competitive_intelligence/output/scrape_latest.csv
   ```

6. Entre lotes, **pausa humana** (15–30 min) si Uber o Rappi devuelven muchos vacíos o JSON de error.

7. **Medir** cobertura (PowerShell ejemplo):

   ```powershell
   python -c "import pandas as pd; df=pd.read_csv('data/caso_2_competitive_intelligence/output/scrape_latest.csv'); u=df[df.platform=='uber_eats']; r=df[df.platform=='rappi']; print('Uber con precio:', u.item_price_mxn.notna().sum(), '/60'); print('Rappi con precio:', r.item_price_mxn.notna().sum(), '/60')"
   ```

## Dos terminales: Uber en uno, Rappi en otro

Salidas: `output/scrape_parallel_uber.csv` y `output/scrape_parallel_rappi.csv`. Luego se fusionan en `scrape_latest.csv`. **Aviso:** dos navegadores a la vez pueden disparar rate limits; si ves muchos errores, corre una terminal y después la otra.

Desde la raíz del repo (carpeta `RappiAIEngineer`):

```powershell
cd "c:\Users\Malelizarazo\Desktop\RappiAIEngineer\caso_2_competitive_intelligence"
```

**Terminal A (Uber):**

```powershell
.\scripts\scrape_uber_only.ps1
```

**Terminal B (Rappi):**

```powershell
.\scripts\scrape_rappi_only.ps1
```

Opcional ventana visible: `.\scripts\scrape_uber_only.ps1 -Headed` o `-Delay 10`.

**Cuando ambas terminen:**

```powershell
.\scripts\merge_parallel_scrapes.ps1
```

## Checklist rápido antes de una corrida completa

- [ ] Firefox + `playwright install firefox`
- [ ] `.env` con proxy/VPN si Uber muestra “coming soon”
- [ ] `--headed` una vez para validar geolocalización y flujo McDonald’s
- [ ] Delay y gap altos en producción
- [ ] Partir en 2 CSV + `merge-scrapes` si la sesión se degrada a mitad de las 20 ciudades

## Archivos clave

- `scripts/scrape_uber_only.ps1`, `scripts/scrape_rappi_only.ps1`, `scripts/merge_parallel_scrapes.ps1` — flujo dos terminales
- `competitive_intel/scrapers/live_pipeline.py` — orden Uber/Rappi, cookies, gap
- `competitive_intel/merge_scrapes.py` — lógica de fusión
- `competitive_intel/cli.py` — `scrape`, `merge-scrapes`
- `LIMITACION_UBER_WEB.md` — restricciones Uber desde el extranjero

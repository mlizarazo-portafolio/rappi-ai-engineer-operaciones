"""
Orquesta Playwright: direcciones × plataformas → CSV (mismo esquema que demo).

Uso responsable: volumen bajo, revisar términos de cada plataforma.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright

from competitive_intel.paths import addresses_json_path, default_scrape_csv, project_root
from competitive_intel.scrapers.didi_playwright import scrape_didi_for_address
from competitive_intel.scrapers.rappi_playwright import scrape_rappi_for_address
from competitive_intel.scrapers.schema import CSV_COLUMNS
from competitive_intel.scrapers.uber_playwright import scrape_uber_for_address

SCRAPERS: dict[str, Any] = {
    "rappi": scrape_rappi_for_address,
    "uber_eats": scrape_uber_for_address,
    "didi_food": scrape_didi_for_address,
}


def load_addresses() -> list[dict[str, Any]]:
    raw = json.loads(addresses_json_path().read_text(encoding="utf-8"))
    return list(raw["addresses"])


def _browser_name(explicit: str | None) -> str:
    # Firefox por defecto: Uber suele cargar en FF y fallar en Chromium ("Coming soon").
    n = (explicit or os.getenv("PLAYWRIGHT_BROWSER", "firefox")).strip().lower()
    if n in ("chrome", "chromium"):
        return "chromium"
    if n in ("ff", "firefox"):
        return "firefox"
    if n in ("webkit", "safari"):
        return "webkit"
    return "firefox"


def playwright_browser_and_context(
    pw: Playwright,
    *,
    headless: bool,
    browser: str | None = None,
) -> tuple[Browser, BrowserContext]:
    """Abre navegador + contexto con la misma config que el scrape (geo, UA, storage_state opcional)."""
    load_dotenv(project_root() / ".env")

    bname = _browser_name(browser)
    if bname == "firefox":
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) "
            "Gecko/20100101 Firefox/128.0"
        )
    else:
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

    ctx_kw: dict[str, Any] = {
        "locale": "es-MX",
        "timezone_id": "America/Mexico_City",
        "user_agent": ua,
        "viewport": {"width": 1365, "height": 900},
        "extra_http_headers": {
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    }
    if os.getenv("CI_SCRAPER_NO_GEOLOCATION", "").strip().lower() not in ("1", "true", "yes"):
        ctx_kw["geolocation"] = {"latitude": 19.4326, "longitude": -99.1332}
        ctx_kw["permissions"] = ["geolocation"]

    raw_state = os.getenv("PLAYWRIGHT_STORAGE_STATE", "").strip()
    if raw_state:
        sp = Path(raw_state)
        if not sp.is_absolute():
            sp = project_root() / raw_state
        sp = sp.resolve()
        if sp.is_file():
            ctx_kw["storage_state"] = str(sp)
        else:
            print(
                f"Aviso: PLAYWRIGHT_STORAGE_STATE={raw_state!r} -> {sp} no existe; ignorado.",
                file=sys.stderr,
            )

    launch_kw: dict[str, Any] = {"headless": headless}
    if bname == "chromium":
        launch_kw["args"] = ["--disable-blink-features=AutomationControlled"]
    proxy = os.getenv("PLAYWRIGHT_PROXY", "").strip()
    if proxy:
        launch_kw["proxy"] = {"server": proxy}

    if bname == "chromium":
        browser_engine = pw.chromium.launch(**launch_kw)
    elif bname == "firefox":
        browser_engine = pw.firefox.launch(**launch_kw)
    else:
        browser_engine = pw.webkit.launch(**launch_kw)
    context = browser_engine.new_context(**ctx_kw)
    return browser_engine, context


def run_save_didi_session(
    output: Path | None = None,
    headless: bool = False,
    browser: str | None = None,
    start_url: str = "https://www.didi-food.com/es-MX/food/",
) -> Path:
    """
    Abre DiDi en el navegador para que inicies sesión a mano; al pulsar Enter se guarda storage_state.
    No guarda contraseñas en el repo: solo cookies/localStorage en un JSON de Playwright.
    """
    out = (output or (project_root() / "didi_storage_state.json")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser_engine, context = playwright_browser_and_context(pw, headless=headless, browser=browser)
        page = context.new_page()
        page.set_default_timeout(60000)
        try:
            page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
            print(
                "Inicia sesión en DiDi en la ventana del navegador. "
                "Cuando el home o el catálogo estén listos, pulsa Enter aquí para guardar la sesión.",
                file=sys.stderr,
            )
            input()
            context.storage_state(path=str(out))
            print(f"Sesión guardada: {out}", file=sys.stderr)
            print(
                "Añade en .env: PLAYWRIGHT_STORAGE_STATE=didi_storage_state.json "
                "(ruta relativa a la raíz del repo) y vuelve a ejecutar scrape.",
                file=sys.stderr,
            )
        finally:
            context.close()
            browser_engine.close()
    return out


def run_live_scrape(
    output: Path | None = None,
    platforms: list[str] | None = None,
    limit_addresses: int | None = None,
    skip_addresses: int = 0,
    headless: bool = True,
    delay_sec: float = 2.0,
    browser: str | None = None,
    progress: bool = True,
) -> Path:
    out = output or default_scrape_csv()
    out.parent.mkdir(parents=True, exist_ok=True)
    plats = platforms or list(SCRAPERS.keys())
    for p in plats:
        if p not in SCRAPERS:
            raise ValueError(f"Plataforma desconocida: {p}. Opciones: {list(SCRAPERS)}")

    addrs = load_addresses()
    if skip_addresses > 0:
        addrs = addrs[skip_addresses:]
    if limit_addresses is not None:
        addrs = addrs[: max(0, limit_addresses)]

    all_rows: list[dict[str, Any]] = []
    total_steps = max(1, len(plats) * len(addrs))
    step_i = 0

    if progress:
        print(
            f"[scrape] Inicio  |  plataformas: {', '.join(plats)}  |  direcciones: {len(addrs)}  "
            f"|  pasos: {total_steps}",
            flush=True,
        )

    with sync_playwright() as pw:
        browser_engine, context = playwright_browser_and_context(pw, headless=headless, browser=browser)

        try:
            gap_plat = float(os.getenv("CI_SCRAPER_PLATFORM_GAP_SEC", "0") or "0")
            # Por plataforma en bloque (p. ej. las 20 direcciones en Uber y luego las 20 en Rappi):
            # un solo CSV al final; suele ir mejor que alternar Uber/Rappi por cada dirección.
            for plat_i, plat in enumerate(plats):
                for addr in addrs:
                    step_i += 1
                    if progress:
                        print(
                            f"[scrape] {step_i}/{total_steps}  {plat}  |  {addr['id']}  |  "
                            f"{addr['neighborhood']}, {addr['city']}",
                            flush=True,
                        )
                    page = context.new_page()
                    page.set_default_timeout(25000)
                    # Uber: tras la 1ª dirección la web suele quedar en feed/sesión y ya no muestra el
                    # input de dirección en la home; cookies limpias ≈ visita nueva por cada ciudad.
                    _no_uber_clear = os.getenv("CI_SCRAPER_NO_UBER_COOKIE_CLEAR", "").strip().lower() in (
                        "1",
                        "true",
                        "yes",
                    )
                    _no_rappi_clear = os.getenv("CI_SCRAPER_NO_RAPPI_COOKIE_CLEAR", "").strip().lower() in (
                        "1",
                        "true",
                        "yes",
                    )
                    if plat == "uber_eats" and not _no_uber_clear:
                        try:
                            context.clear_cookies()
                        except Exception:
                            pass
                    if plat == "rappi" and not _no_rappi_clear:
                        try:
                            context.clear_cookies()
                        except Exception:
                            pass
                    try:
                        fn = SCRAPERS[plat]
                        rows = fn(page, addr)
                        all_rows.extend(rows)
                    finally:
                        page.close()
                    if progress and rows:
                        with_price = sum(1 for r in rows if r.get("item_price_mxn") is not None)
                        avail = sum(1 for r in rows if r.get("store_available"))
                        print(
                            f"[scrape]     -> {len(rows)} filas  |  precio en {with_price}/{len(rows)}  |  "
                            f"tienda_disponible {avail}/{len(rows)}",
                            flush=True,
                        )
                    jitter = random.uniform(0.4, min(4.0, max(0.8, delay_sec * 0.5)))
                    time.sleep(delay_sec + jitter)
                if gap_plat > 0 and plat_i < len(plats) - 1:
                    if progress:
                        print(
                            f"[scrape] Pausa entre plataformas {gap_plat:.0f}s (CI_SCRAPER_PLATFORM_GAP_SEC)...",
                            flush=True,
                        )
                    time.sleep(gap_plat)
        finally:
            context.close()
            browser_engine.close()

    if progress:
        print(f"[scrape] Escribiendo CSV ({len(all_rows)} filas)...", flush=True)

    df = pd.DataFrame(all_rows, columns=CSV_COLUMNS)
    df.to_csv(out, index=False, encoding="utf-8")
    return out

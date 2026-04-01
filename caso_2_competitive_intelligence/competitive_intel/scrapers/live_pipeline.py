"""
Orquesta Playwright: direcciones × plataformas → CSV (mismo esquema que demo).

Uso responsable: volumen bajo, revisar términos de cada plataforma.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
from playwright.sync_api import sync_playwright

from competitive_intel.paths import addresses_json_path, default_scrape_csv
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


def run_live_scrape(
    output: Path | None = None,
    platforms: list[str] | None = None,
    limit_addresses: int | None = None,
    headless: bool = True,
    delay_sec: float = 2.0,
) -> Path:
    out = output or default_scrape_csv()
    out.parent.mkdir(parents=True, exist_ok=True)
    plats = platforms or list(SCRAPERS.keys())
    for p in plats:
        if p not in SCRAPERS:
            raise ValueError(f"Plataforma desconocida: {p}. Opciones: {list(SCRAPERS)}")

    addrs = load_addresses()
    if limit_addresses is not None:
        addrs = addrs[: max(0, limit_addresses)]

    all_rows: list[dict[str, Any]] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            locale="es-MX",
            timezone_id="America/Mexico_City",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1365, "height": 900},
        )
        page = context.new_page()
        page.set_default_timeout(25000)

        try:
            for addr in addrs:
                for plat in plats:
                    fn = SCRAPERS[plat]
                    rows = fn(page, addr)
                    all_rows.extend(rows)
                    time.sleep(delay_sec)
        finally:
            context.close()
            browser.close()

    df = pd.DataFrame(all_rows, columns=CSV_COLUMNS)
    df.to_csv(out, index=False, encoding="utf-8")
    return out

"""DiDi Food web (es-MX): intento controlado; la UI suele empujar a app."""

from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Page

from competitive_intel.scrapers.schema import PRODUCTS, build_row
from competitive_intel.scrapers.text_extract import (
    delivery_fee_from_text,
    eta_minutes_from_text,
    price_near_keyword,
    service_fee_from_text,
)


def scrape_didi_for_address(page: Page, address: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    line = f"{address['neighborhood']}, {address['city']}"
    try:
        page.goto("https://www.didi-food.com/es-MX/food/", wait_until="domcontentloaded", timeout=55000)
        page.wait_for_timeout(2500)
    except Exception:
        for p in PRODUCTS:
            rows.append(
                build_row(
                    data_source="playwright_didi_food",
                    platform="didi_food",
                    address=address,
                    product_name=p,
                    item_price_mxn=None,
                    store_available=False,
                    promotions_visible="No se cargó didi-food.com",
                )
            )
        return rows

    # Intentar localizar campo de dirección o búsqueda
    filled = False
    for sel in (
        'input[placeholder*="direcci" i]',
        'input[placeholder*="Direcci" i]',
        'input[type="search"]',
        "input[autocomplete='street-address']",
    ):
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible():
                loc.fill(line, timeout=5000)
                page.wait_for_timeout(1000)
                page.keyboard.press("Enter")
                page.wait_for_timeout(2500)
                filled = True
                break
        except Exception:
            continue

    # Buscar McDonald's
    try:
        s = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first
        if s.count() > 0 and s.is_visible():
            s.fill("McDonald's")
            page.keyboard.press("Enter")
            page.wait_for_timeout(2500)
    except Exception:
        pass

    try:
        link = page.get_by_role("link", name=re.compile(r"mcdonald", re.I)).first
        if link.count() > 0:
            link.click(timeout=8000)
            page.wait_for_timeout(2500)
    except Exception:
        pass

    try:
        body = page.evaluate("() => document.body.innerText.slice(0, 80000)")
    except Exception:
        body = ""

    if not body or len(body) < 200 or "app" in body.lower()[:400]:
        note = "DiDi empuja a app o sin menú web; datos no extraíbles de forma fiable"
        for p in PRODUCTS:
            rows.append(
                build_row(
                    data_source="playwright_didi_food",
                    platform="didi_food",
                    address=address,
                    product_name=p,
                    item_price_mxn=None,
                    store_available=False,
                    promotions_visible=note,
                )
            )
        return rows

    delivery = delivery_fee_from_text(body)
    service = service_fee_from_text(body)
    eta = eta_minutes_from_text(body)
    promo = "Ninguna visible"
    if re.search(r"promo|descuento|gratis", body, re.I):
        promo = "Posible promo (texto)"

    any_price = False
    for product in PRODUCTS:
        price = price_near_keyword(body, product, radius=300)
        if price:
            any_price = True
        rows.append(
            build_row(
                data_source="playwright_didi_food",
                platform="didi_food",
                address=address,
                product_name=product,
                item_price_mxn=price,
                delivery_fee_mxn=delivery,
                service_fee_mxn=service,
                eta_minutes=eta,
                promotions_visible=promo,
                store_available=price is not None,
            )
        )

    if not any_price and filled:
        for r in rows:
            r["promotions_visible"] = "Página cargada sin precios de ítems detectados"
            r["store_available"] = False
    return rows

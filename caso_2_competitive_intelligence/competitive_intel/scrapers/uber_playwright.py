"""Uber Eats web mx-en: dirección vía typeahead + búsqueda McDonald's."""

from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Page

from competitive_intel.scrapers.fee_sanity import sanitize_fees_mxn
from competitive_intel.scrapers.schema import PRODUCTS, build_row
from competitive_intel.scrapers.text_extract import (
    delivery_fee_from_text,
    eta_minutes_from_text,
    price_near_keyword,
    service_fee_from_text,
)


def _fill_delivery_address(page: Page, address: dict[str, Any]) -> bool:
    line = f"{address['neighborhood']}, {address['city']}, México"
    selectors = [
        "#location-typeahead-home-input",
        'input[placeholder*="delivery address" i]',
        'input[placeholder*="direcci" i]',
        'input[aria-label*="address" i]',
    ]
    inp = None
    for sel in selectors:
        loc = page.locator(sel)
        try:
            if loc.count() > 0:
                inp = loc.first
                break
        except Exception:
            continue
    if inp is None:
        return False
    try:
        inp.click(timeout=5000)
        inp.fill("", timeout=3000)
        inp.type(line, delay=35)
        page.wait_for_timeout(1800)
        page.keyboard.press("ArrowDown")
        page.wait_for_timeout(400)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3500)
        return True
    except Exception:
        return False


def _open_mcdonalds_from_search(page: Page) -> bool:
    search_selectors = [
        'input[placeholder*="Search" i]',
        'input[placeholder*="Buscar" i]',
        'input[type="search"]',
        '[data-testid="search-input"]',
    ]
    box = None
    for sel in search_selectors:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible():
                box = loc
                break
        except Exception:
            continue
    if box is None:
        return False
    try:
        box.click(timeout=5000)
        box.fill("McDonald's")
        page.wait_for_timeout(1200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        l1 = page.get_by_role("link", name=re.compile(r"mcdonald", re.I))
        if l1.count() > 0:
            l1.first.click(timeout=10000)
            page.wait_for_load_state("domcontentloaded", timeout=25000)
            page.wait_for_timeout(2000)
            return True
        l2 = page.locator("a").filter(has_text=re.compile(r"mcdonald", re.I))
        if l2.count() > 0:
            l2.first.click(timeout=10000)
            page.wait_for_load_state("domcontentloaded", timeout=25000)
            page.wait_for_timeout(2000)
            return True
    except Exception:
        return False
    return False


def scrape_uber_for_address(page: Page, address: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        page.goto("https://www.ubereats.com/mx-en/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
    except Exception:
        for p in PRODUCTS:
            rows.append(
                build_row(
                    data_source="playwright_uber_eats",
                    platform="uber_eats",
                    address=address,
                    product_name=p,
                    item_price_mxn=None,
                    store_available=False,
                    promotions_visible="Fallo al cargar ubereats.com",
                )
            )
        return rows

    if not _fill_delivery_address(page, address):
        for p in PRODUCTS:
            rows.append(
                build_row(
                    data_source="playwright_uber_eats",
                    platform="uber_eats",
                    address=address,
                    product_name=p,
                    item_price_mxn=None,
                    store_available=False,
                    promotions_visible="No se encontró input de dirección (UI cambió o bloqueo)",
                )
            )
        return rows

    if not _open_mcdonalds_from_search(page):
        for p in PRODUCTS:
            rows.append(
                build_row(
                    data_source="playwright_uber_eats",
                    platform="uber_eats",
                    address=address,
                    product_name=p,
                    item_price_mxn=None,
                    store_available=False,
                    promotions_visible="No se abrió McDonald's tras dirección",
                )
            )
        return rows

    try:
        body = page.evaluate(
            """() => (document.body.innerText || '').normalize('NFC').slice(0, 200000)"""
        )
    except Exception:
        body = ""

    delivery = delivery_fee_from_text(body)
    service = service_fee_from_text(body)
    delivery, service = sanitize_fees_mxn(delivery, service)
    eta = eta_minutes_from_text(body)
    promo = "Ninguna visible"
    if re.search(r"free delivery|gratis|off|descuento|promo", body, re.I):
        promo = "Texto promocional visible (sin clasificar)"

    for product in PRODUCTS:
        price = price_near_keyword(body, product, radius=320)
        if price is None:
            price = price_near_keyword(body, product.replace("Combo ", ""), radius=320)
        rows.append(
            build_row(
                data_source="playwright_uber_eats",
                platform="uber_eats",
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
    return rows

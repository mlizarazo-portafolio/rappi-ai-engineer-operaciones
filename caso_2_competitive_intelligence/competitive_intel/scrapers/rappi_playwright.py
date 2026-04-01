"""Scrape público rappi.com.mx — tienda McDonald's por ciudad (web, no app)."""

from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from competitive_intel.scrapers.geo import rappi_slug_for_city
from competitive_intel.scrapers.rappi_products import EXTRACTORS
from competitive_intel.scrapers.schema import PRODUCTS, build_row
from competitive_intel.scrapers.text_extract import (
    delivery_fee_from_text,
    eta_minutes_from_text,
    price_near_keyword,
    price_near_keyword_multiline,
    service_fee_from_text,
)

# ID de tienda en enlaces públicos de la home MX (puede variar; hay fallback por búsqueda).
MCD_SLUG = "706-mcdonald-s"


def _dismiss_rappi_cookies(page: Page) -> None:
    for name in ("Ok, entendido", "Ok, entiendo", "Aceptar", "Entendido"):
        try:
            page.get_by_role("button", name=re.compile(re.escape(name), re.I)).click(timeout=2500)
            return
        except PlaywrightTimeout:
            continue
        except Exception:
            continue


def _open_first_branch_menu_if_hub(page: Page) -> None:
    """Si la página es el hub de marca (muchas sucursales '… Menú'), abrir la primera McDonald's."""
    links = page.locator("a").filter(has_text=re.compile(r"Men[uú]", re.I))
    try:
        n = links.count()
    except Exception:
        return
    if n < 40:
        return
    try:
        first = links.first
        first.scroll_into_view_if_needed(timeout=5000)
        first.click(timeout=20000, force=True)
        page.wait_for_load_state("domcontentloaded", timeout=45000)
        page.wait_for_timeout(2500)
        _dismiss_rappi_cookies(page)
    except Exception:
        pass


def _goto_mcdonalds(page: Page, slug: str) -> bool:
    urls = [
        f"https://www.rappi.com.mx/{slug}/restaurantes/delivery/{MCD_SLUG}",
        f"https://www.rappi.com.mx/{slug}/restaurantes?q=mcdonalds",
    ]
    for url in urls:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(1500)
            _dismiss_rappi_cookies(page)
            page.wait_for_timeout(800)
            if page.url.startswith("https://www.rappi.com.mx/") and (
                "mcdonald" in page.url.lower() or "q=mcdonalds" in page.url.lower()
            ):
                # En búsqueda, clic en primer McDonald's si hace falta
                if "q=mcdonalds" in page.url.lower():
                    try:
                        links = page.locator('a[href*="/delivery/"][href*="mcdonald"]')
                        if links.count() > 0:
                            links.first.click(timeout=8000)
                            page.wait_for_load_state("domcontentloaded", timeout=20000)
                            page.wait_for_timeout(1200)
                            _dismiss_rappi_cookies(page)
                    except Exception:
                        pass
                return True
        except Exception:
            continue
    return False


def scrape_rappi_for_address(page: Page, address: dict[str, Any]) -> list[dict[str, Any]]:
    slug = rappi_slug_for_city(address["city"])
    rows: list[dict[str, Any]] = []
    if not slug:
        for p in PRODUCTS:
            rows.append(
                build_row(
                    data_source="playwright_rappi",
                    platform="rappi",
                    address=address,
                    product_name=p,
                    item_price_mxn=None,
                    store_available=False,
                    promotions_visible="Ciudad sin slug Rappi mapeado",
                )
            )
        return rows

    ok = _goto_mcdonalds(page, slug)
    if not ok:
        for p in PRODUCTS:
            rows.append(
                build_row(
                    data_source="playwright_rappi",
                    platform="rappi",
                    address=address,
                    product_name=p,
                    item_price_mxn=None,
                    store_available=False,
                    promotions_visible="No se pudo abrir McDonald's en Rappi (URL/ciudad)",
                )
            )
        return rows

    page.wait_for_timeout(2500)
    _open_first_branch_menu_if_hub(page)

    # Menú suele cargar con scroll (virtualización / lazy load).
    try:
        page.wait_for_timeout(1200)
        for _ in range(8):
            page.mouse.wheel(0, 1400)
            page.wait_for_timeout(350)
        page.wait_for_timeout(800)
    except Exception:
        pass

    try:
        body = page.evaluate(
            """() => (document.body.innerText || '').normalize('NFC').slice(0, 200000)"""
        )
    except Exception:
        body = ""

    eta = eta_minutes_from_text(body)
    delivery = None
    if re.search(r"env[ií]o[\s\S]{0,30}gratis|gratis[\s\S]{0,40}env[ií]o|env[ií]o\s+gratis", body, re.I):
        delivery = 0.0
    if delivery is None:
        delivery = delivery_fee_from_text(body)
    if delivery is not None and eta is not None and abs(float(delivery) - float(eta)) < 0.01:
        delivery = None
    service = service_fee_from_text(body)
    promo = "Ninguna visible"
    if re.search(r"gratis|descuento|2x1|cup[oó]n|promo", body, re.I):
        promo = "Promoción visible en página (texto genérico)"

    for product in PRODUCTS:
        extractor = EXTRACTORS.get(product)
        price = extractor(body) if extractor else None
        if price is None:
            price = price_near_keyword(body, product, radius=400)
        if price is None:
            price = price_near_keyword_multiline(body, product)
        if price is None:
            alt = product.replace("Combo ", "").replace("600ml", "600")
            price = price_near_keyword(body, alt, radius=400)
        if price is None:
            price = price_near_keyword_multiline(body, alt)
        rows.append(
            build_row(
                data_source="playwright_rappi",
                platform="rappi",
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

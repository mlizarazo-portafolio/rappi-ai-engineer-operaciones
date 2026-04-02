"""Uber Eats web mx-en: dirección vía typeahead + búsqueda McDonald's."""

from __future__ import annotations

import os
import re
import time
from typing import Any
from urllib.parse import quote

from playwright.sync_api import Page

from competitive_intel.scrapers.fee_sanity import sanitize_fees_mxn
from competitive_intel.scrapers.rate_limit import cooldown_sleep, page_looks_rate_limited
from competitive_intel.scrapers.schema import PRODUCTS, build_row
from competitive_intel.scrapers.text_extract import (
    delivery_fee_from_text,
    eta_minutes_from_text,
    price_near_keyword,
    service_fee_from_text,
)

# Pantallas sustitutas (mantenimiento, región, anti-bot) sin el formulario de dirección.
_UBER_BLOCK_PATTERNS = re.compile(
    r"trabajando\s+para|estamos\s+trabajando|working\s+on\s+it|under\s+maintenance|"
    r"mantenimiento|temporarily\s+unavailable|no\s+disponible|something\s+went\s+wrong|"
    r"access\s+denied|unusual\s+traffic|"
    r"we.re\s+coming\s+soon|coming\s+soon|expanding\s+our\s+coverage|check\s+back\s+in\s+the\s+future|"
    r"pronto\s+llegamos|muy\s+pronto",
    re.I,
)


def _uber_start_urls() -> list[str]:
    custom = os.getenv("UBER_EATS_URL", "").strip()
    if custom:
        return [custom]
    # mx/ a veces responde distinto a mx-en/ según región
    return [
        "https://www.ubereats.com/mx/",
        "https://www.ubereats.com/mx-en/",
    ]


def _goto_working_uber_home(page: Page) -> tuple[bool, str | None]:
    """Prueba varias URLs hasta una sin pantalla 'coming soon' / bloqueo / JSON de rate limit."""
    last_msg: str | None = None
    for url in _uber_start_urls():
        for attempt in range(6):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2800)
            except Exception as e:
                last_msg = f"Error al cargar {url}: {e!s}"
                break
            if page_looks_rate_limited(page):
                cooldown_sleep(42.0 + attempt * 38.0, "Uber: too_many_requests / bd.error (home)")
                continue
            msg = _uber_landing_issue_message(page)
            if msg is None:
                return True, None
            last_msg = msg
            break
        else:
            last_msg = last_msg or "Uber: rate limit persistente en esta URL tras reintentos"
            continue
    return False, last_msg or "Uber Eats no cargó una página con tiendas (bloqueo regional o red)."


def _uber_landing_issue_message(page: Page) -> str | None:
    try:
        snippet = page.evaluate("() => (document.body.innerText || '').slice(0, 4000)")
    except Exception:
        return None
    if not snippet or len(snippet.strip()) < 30:
        return "Página casi vacía o sin cargar (red, bloqueo o timeout)."
    if _UBER_BLOCK_PATTERNS.search(snippet):
        return (
            "Uber Eats mostró 'Coming soon' / fuera de cobertura (típico desde IP o país sin servicio web); "
            "no hay input de dirección. Opciones: VPN a México, otra red, o documentar cobertura parcial en el informe."
        )
    return None


def _dismiss_uber_chrome(page: Page) -> None:
    """Cierra banners de cookies / consentimiento que tapan la búsqueda."""
    for pat in (
        re.compile(r"^accept(\s+all)?$", re.I),
        re.compile(r"^aceptar", re.I),
        re.compile(r"^agree", re.I),
        re.compile(r"^entendido$", re.I),
        re.compile(r"^ok$", re.I),
        re.compile(r"^continuar$", re.I),
    ):
        try:
            btn = page.get_by_role("button", name=pat)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click(timeout=2500)
                page.wait_for_timeout(600)
        except Exception:
            continue


def _uber_settle_after_address(page: Page) -> None:
    """Tras elegir dirección, la SPA tarda en mostrar el feed y el buscador de tiendas."""
    page.wait_for_timeout(6500)
    try:
        page.evaluate("window.scrollTo(0, 0)")
    except Exception:
        pass
    _dismiss_uber_chrome(page)
    page.wait_for_timeout(2000)


def _uber_locale_prefix(url: str) -> str | None:
    m = re.match(r"(https://www\.ubereats\.com/(?:mx-en|mx))(?:/|$)", url)
    return m.group(1) if m else None


def _open_uber_search_panel(page: Page) -> None:
    """Muchas UIs de Uber no muestran el input hasta pulsar buscar / lupa."""
    tries = [
        lambda: page.get_by_role("button", name=re.compile(r"^search$|^buscar$", re.I)),
        lambda: page.get_by_role("button", name=re.compile(r"search restaurants|buscar restaurantes", re.I)),
        lambda: page.locator('[data-testid*="search"][data-testid*="icon" i]'),
        lambda: page.locator('[aria-label*="Search" i][role="button"]'),
        lambda: page.locator('[aria-label*="Buscar" i][role="button"]'),
        lambda: page.locator("header").get_by_role("button", name=re.compile(r"search", re.I)),
        lambda: page.locator('a[href*="/search"]').first,
    ]
    for get_loc in tries:
        try:
            loc = get_loc()
            if hasattr(loc, "count") and loc.count() > 0:
                el = loc.first
            else:
                continue
            if el.is_visible():
                el.click(timeout=3500)
                page.wait_for_timeout(1400)
                return
        except Exception:
            continue


def _field_is_address_not_store(ph: str, aid: str, nid: str) -> bool:
    blob = f"{ph} {aid} {nid}".lower()
    return bool(
        re.search(
            r"address|direcci|entrega|delivery|ubicaci|location|street|postal|"
            r"where\s+to|add\s+address|tu\s+direcci",
            blob,
            re.I,
        )
    )


def _find_store_search_input(page: Page):
    """Localiza el input de búsqueda de restaurantes (no el de dirección)."""
    # Placeholders frecuentes en Uber (EN/ES)
    for pat in (
        re.compile(r"search", re.I),
        re.compile(r"buscar", re.I),
        re.compile(r"craving", re.I),
        re.compile(r"antojo", re.I),
        re.compile(r"restaurant", re.I),
        re.compile(r"food", re.I),
        re.compile(r"comida", re.I),
    ):
        try:
            loc = page.get_by_placeholder(pat)
            if loc.count() == 0:
                continue
            n = min(loc.count(), 5)
            for i in range(n):
                el = loc.nth(i)
                try:
                    if not el.is_visible():
                        continue
                    ph = el.get_attribute("placeholder") or ""
                    aid = el.get_attribute("aria-label") or ""
                    nid = el.get_attribute("id") or ""
                    if nid == "location-typeahead-home-input" or _field_is_address_not_store(ph, aid, nid):
                        continue
                    return el
                except Exception:
                    continue
        except Exception:
            continue

    for role in ("searchbox", "combobox"):
        try:
            loc = page.get_by_role(role)
            n = min(loc.count(), 12)
            for i in range(n):
                el = loc.nth(i)
                try:
                    if not el.is_visible():
                        continue
                    ph = el.get_attribute("placeholder") or ""
                    aid = el.get_attribute("aria-label") or ""
                    nid = el.get_attribute("id") or ""
                    if nid == "location-typeahead-home-input" or _field_is_address_not_store(ph, aid, nid):
                        continue
                    return el
                except Exception:
                    continue
        except Exception:
            continue

    selectors = [
        'textarea[placeholder*="Search" i]',
        'textarea[placeholder*="Buscar" i]',
        'input[placeholder*="Search" i]',
        'input[placeholder*="Buscar" i]',
        'input[placeholder*="restaurant" i]',
        'input[placeholder*="restaurante" i]',
        'input[placeholder*="craving" i]',
        'input[placeholder*="antojo" i]',
        'input[aria-label*="Search" i]',
        'input[aria-label*="Buscar" i]',
        '[data-testid*="search-input"]',
        '[data-testid*="Search"]',
        'input[type="search"]',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() == 0:
                continue
            n = min(loc.count(), 8)
            for i in range(n):
                el = loc.nth(i)
                try:
                    if not el.is_visible():
                        continue
                    ph = el.get_attribute("placeholder") or ""
                    aid = el.get_attribute("aria-label") or ""
                    nid = el.get_attribute("id") or ""
                    if nid == "location-typeahead-home-input" or _field_is_address_not_store(ph, aid, nid):
                        continue
                    return el
                except Exception:
                    continue
        except Exception:
            continue
    return None


def _fill_delivery_address(page: Page, address: dict[str, Any]) -> bool:
    line = f"{address['neighborhood']}, {address['city']}, México"
    _dismiss_uber_chrome(page)
    page.wait_for_timeout(1500)

    for pat in (
        re.compile(r"add (delivery )?address", re.I),
        re.compile(r"enter address", re.I),
        re.compile(r"agregar direcci", re.I),
        re.compile(r"ingresa tu direcci", re.I),
        re.compile(r"elige (tu )?direcci", re.I),
        re.compile(r"where to", re.I),
    ):
        try:
            btn = page.get_by_role("button", name=pat)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click(timeout=4000)
                page.wait_for_timeout(2000)
                break
        except Exception:
            continue

    selectors = [
        "#location-typeahead-home-input",
        'input[id*="LocationTypeahead" i]',
        'input[id*="location-typeahead" i]',
        'input[data-testid*="location-typeahead" i]',
        'input[data-testid*="address" i]',
        'input[aria-label*="Delivery address" i]',
        'input[aria-label*="delivery address" i]',
        'input[aria-label*="Enter address" i]',
        'input[aria-label*="direcci" i]',
        'input[placeholder*="delivery address" i]',
        'input[placeholder*="Enter delivery" i]',
        'input[placeholder*="direcci" i]',
        'input[placeholder*="Tu dirección" i]',
        'input[placeholder*="Tu direccion" i]',
    ]

    inp = None
    deadline = time.monotonic() + 24.0
    while time.monotonic() < deadline:
        for sel in selectors:
            loc = page.locator(sel)
            try:
                if loc.count() > 0 and loc.first.is_visible():
                    inp = loc.first
                    break
            except Exception:
                continue
        if inp is not None:
            break
        page.wait_for_timeout(800)
        _dismiss_uber_chrome(page)

    if inp is None:
        try:
            page.wait_for_selector("#location-typeahead-home-input", state="visible", timeout=10000)
            loc = page.locator("#location-typeahead-home-input")
            if loc.count() > 0 and loc.first.is_visible():
                inp = loc.first
        except Exception:
            pass

    if inp is None:
        return False

    try:
        inp.scroll_into_view_if_needed(timeout=6000)
        inp.click(timeout=6000)
        inp.fill("", timeout=3000)
        inp.type(line, delay=40)
        page.wait_for_timeout(2200)
        page.keyboard.press("ArrowDown")
        page.wait_for_timeout(500)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5500)
        return True
    except Exception:
        return False


def _click_mcdonalds_result(page: Page) -> bool:
    """Abre la tienda McDonald's desde resultados de búsqueda o enlaces."""
    tries = [
        lambda: page.get_by_role("link", name=re.compile(r"mcdonald", re.I)),
        lambda: page.get_by_role("button", name=re.compile(r"mcdonald", re.I)),
        lambda: page.locator("a").filter(has_text=re.compile(r"mcdonald", re.I)),
        lambda: page.locator('[href*="mcdonald" i]'),
        lambda: page.locator('[href*="mc-donalds" i]'),
    ]
    for get_loc in tries:
        try:
            loc = get_loc()
            n = min(loc.count(), 12)
            for i in range(n):
                el = loc.nth(i)
                try:
                    if el.is_visible():
                        el.click(timeout=12000)
                        page.wait_for_load_state("domcontentloaded", timeout=30000)
                        page.wait_for_timeout(3500)
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False


def _try_mcdonalds_via_ubereats_search_url(page: Page) -> bool:
    """Fallback: /search?q=... con la misma sesión (dirección ya elegida)."""
    prefix = _uber_locale_prefix(page.url)
    if not prefix:
        return False
    for raw_q in ("McDonalds", "mcdonalds", "McDonald's"):
        try:
            q = quote(raw_q)
            page.goto(f"{prefix}/search?q={q}", wait_until="domcontentloaded", timeout=55000)
            page.wait_for_timeout(4500)
            if _click_mcdonalds_result(page):
                return True
        except Exception:
            continue
    return False


def _open_mcdonalds_from_search(page: Page) -> bool:
    box = None
    deadline = time.monotonic() + 26.0
    while time.monotonic() < deadline:
        _open_uber_search_panel(page)
        _dismiss_uber_chrome(page)
        box = _find_store_search_input(page)
        if box is not None:
            break
        page.wait_for_timeout(900)

    if box is None:
        return _try_mcdonalds_via_ubereats_search_url(page)

    queries = ("McDonald's", "McDonalds", "mcdonalds")
    for q in queries:
        try:
            box.click(timeout=5000)
            page.wait_for_timeout(500)
            box.fill("", timeout=3000)
            box.type(q, delay=45)
            page.wait_for_timeout(3200)
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(400)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)
            if _click_mcdonalds_result(page):
                return True
            page.keyboard.press("Enter")
            page.wait_for_timeout(4000)
            if _click_mcdonalds_result(page):
                return True
        except Exception:
            pass
        box = _find_store_search_input(page)
        if box is None:
            break

    return _try_mcdonalds_via_ubereats_search_url(page)


def _uber_fail_rows(address: dict[str, Any], msg: str) -> list[dict[str, Any]]:
    return [
        build_row(
            data_source="playwright_uber_eats",
            platform="uber_eats",
            address=address,
            product_name=p,
            item_price_mxn=None,
            store_available=False,
            promotions_visible=msg,
        )
        for p in PRODUCTS
    ]


def scrape_uber_for_address(page: Page, address: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for round_i in range(4):
        ok, err = _goto_working_uber_home(page)
        if not ok:
            return _uber_fail_rows(address, err or "Fallo al cargar ubereats.com")

        _dismiss_uber_chrome(page)
        page.wait_for_timeout(1200)

        filled = _fill_delivery_address(page, address)
        if not filled:
            if page_looks_rate_limited(page):
                cooldown_sleep(48.0 + round_i * 32.0, "Uber: rate limit sin completar dirección")
                continue
            hint = _uber_landing_issue_message(page) or (
                "No se encontró input de dirección (UI cambió, cookie wall o otra variante de la home)."
            )
            return _uber_fail_rows(address, hint)

        if page_looks_rate_limited(page):
            cooldown_sleep(52.0 + round_i * 32.0, "Uber: rate limit tras elegir dirección")
            continue

        _uber_settle_after_address(page)

        if page_looks_rate_limited(page):
            cooldown_sleep(55.0 + round_i * 35.0, "Uber: rate limit en feed / búsqueda")
            continue

        if not _open_mcdonalds_from_search(page):
            if page_looks_rate_limited(page):
                cooldown_sleep(58.0 + round_i * 35.0, "Uber: rate limit al buscar McDonald's")
                continue
            return _uber_fail_rows(address, "No se abrió McDonald's tras dirección")

        try:
            body = page.evaluate(
                """() => (document.body.innerText || '').normalize('NFC').slice(0, 200000)"""
            )
        except Exception:
            body = ""

        bl = body.lower()
        if page_looks_rate_limited(page) or (
            len(body.strip()) < 800 and ("too_many_requests" in bl or "bd.error" in bl)
        ):
            cooldown_sleep(62.0 + round_i * 35.0, "Uber: rate limit en página de tienda")
            continue

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

    return _uber_fail_rows(
        address,
        "Uber: límite de peticiones (bd.error / too_many_requests) tras varios reintentos",
    )

"""DiDi Food web (es-MX): intento controlado; la UI suele empujar a app."""

from __future__ import annotations

import os
import re
import sys
from typing import Any

from playwright.sync_api import Page

from competitive_intel.scrapers.schema import PRODUCTS, build_row
from competitive_intel.scrapers.text_extract import (
    delivery_fee_from_text,
    eta_minutes_from_text,
    price_near_keyword,
    service_fee_from_text,
)


def _didi_debug(msg: str) -> None:
    if os.getenv("CI_SCRAPER_DEBUG", "").strip().lower() not in ("1", "true", "yes"):
        return
    print(f"[didi debug] {msg}", file=sys.stderr)


_LOGIN_HINT = (
    "DiDi exige inicio de sesión en web; el scrape no usa credenciales. "
    "Opcional: guarda sesión con `python -m competitive_intel save-didi-session` "
    "y en .env `PLAYWRIGHT_STORAGE_STATE=didi_storage_state.json`."
)

_LOGIN_BODY_RE = re.compile(
    r"iniciar\s+sesión|inicia\s+sesión|log\s*in|sign\s*in|"
    r"regístrate|crear\s+cuenta|"
    r"código\s+de\s+verificación|verifica\s+tu\s+teléfono|ingresa\s+tu\s+teléfono",
    re.I,
)


def _didi_login_wall_detect(page: Page) -> str | None:
    """Si la web exige cuenta, devuelve mensaje para CSV; si no, None."""
    try:
        url = page.url.lower()
        if any(x in url for x in ("/login", "/signin", "sign-in", "/auth", "/account")):
            return f"{_LOGIN_HINT} (URL de autenticación)."
    except Exception:
        pass

    try:
        pw_inp = page.locator('input[type="password"]')
        if pw_inp.count() > 0 and pw_inp.first.is_visible():
            return f"{_LOGIN_HINT} (formulario con contraseña)."
    except Exception:
        pass

    try:
        for label in ("Iniciar sesión", "Inicia sesión", "Sign in", "Log in"):
            loc = page.get_by_role("button", name=re.compile("^" + re.escape(label) + "$", re.I))
            if loc.count() == 0:
                loc = page.get_by_role("link", name=re.compile("^" + re.escape(label) + "$", re.I))
            if loc.count() > 0 and loc.first.is_visible():
                return f"{_LOGIN_HINT} (CTA «{label}» visible)."
    except Exception:
        pass

    try:
        body = page.evaluate("() => (document.body.innerText || '').slice(0, 6000)")
    except Exception:
        body = ""
    if body and _LOGIN_BODY_RE.search(body):
        if re.search(
            r"contraseña|password|teléfono|celular|phone|SMS|código|verification",
            body,
            re.I,
        ):
            return f"{_LOGIN_HINT} (texto de login/registro)."
    return None


def _didi_rows_login_blocked(address: dict[str, Any], note: str) -> list[dict[str, Any]]:
    return [
        build_row(
            data_source="playwright_didi_food",
            platform="didi_food",
            address=address,
            product_name=p,
            item_price_mxn=None,
            store_available=False,
            promotions_visible=note,
        )
        for p in PRODUCTS
    ]


# CTAs en pantalla de ubicación (no confundir con login; «Entrar» suele ser submit de login).
_LOCATION_BUTTON_LABELS = (
    "Continuar",
    "Confirmar",
    "Siguiente",
    "Aceptar",
    "Listo",
    "Guardar",
    "Empezar",
    "Entrar",
    "Ver restaurantes",
    "Explorar",
    "Usar ubicación actual",
    "Confirmar ubicación",
    "Permitir",
    "Entendido",
)
_LOCATION_BUTTON_RE = re.compile(
    r"confirmar|continuar|siguiente|aceptar|listo|guardar|empezar|entrar|comenzar|"
    r"permitir|entendido|ver\s+restaurantes|explorar|usar\s+esta|elegir\s+manual",
    re.I,
)


def _try_click_first_visible(page: Page, locator_callable) -> bool:
    """Intenta clic en el primer elemento visible de un locator (hasta 8 coincidencias)."""
    try:
        loc = locator_callable()
        n = min(loc.count(), 8)
        for i in range(n):
            el = loc.nth(i)
            try:
                if el.is_visible():
                    el.click(timeout=5000)
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def _pass_didi_location_gate(page: Page, address_line: str) -> None:
    """
    Tras cargar, DiDi suele mostrar una pantalla/modal de ubicación.
    Sin clic o confirmación, la SPA puede quedar en blanco o redirigir y 'cerrarse' el flujo útil.
    """
    page.wait_for_timeout(4000)

    for round_i in range(4):
        _didi_debug(f"location gate ronda {round_i + 1} url={page.url!r}")

        clicked = False
        for label in _LOCATION_BUTTON_LABELS:
            if _try_click_first_visible(page, lambda l=label: page.get_by_role("button", name=l)):
                clicked = True
                _didi_debug(f"click botón (label): {label!r}")
                page.wait_for_timeout(3500)
                break

        if not clicked and _try_click_first_visible(
            page, lambda: page.get_by_role("button", name=_LOCATION_BUTTON_RE)
        ):
            clicked = True
            _didi_debug("click botón (regex ubicación)")
            page.wait_for_timeout(3500)

        if not clicked and _try_click_first_visible(
            page, lambda: page.get_by_role("link", name=_LOCATION_BUTTON_RE)
        ):
            clicked = True
            _didi_debug("click link (regex ubicación)")
            page.wait_for_timeout(3500)

        # "Ingresar dirección" / manual
        if not clicked:
            for manual_pat in (
                re.compile(r"ingresar|escribir|manual|otra\s+direcci|agregar\s+direcci", re.I),
            ):
                if _try_click_first_visible(page, lambda p=manual_pat: page.get_by_role("link", name=p)):
                    clicked = True
                    _didi_debug("click enlace modo manual")
                    page.wait_for_timeout(2500)
                    break

        # Rellenar cualquier input de dirección/ubicación visible en esta capa
        for sel in (
            'input[placeholder*="direcci" i]',
            'input[placeholder*="Direcci" i]',
            'input[placeholder*="ubicaci" i]',
            'input[placeholder*="Ubicaci" i]',
            'input[placeholder*="calle" i]',
            'input[type="search"]',
            "input[autocomplete='street-address']",
        ):
            loc = page.locator(sel)
            try:
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click(timeout=3000)
                    loc.first.fill("", timeout=2000)
                    loc.first.type(address_line, delay=40)
                    page.wait_for_timeout(2000)
                    page.keyboard.press("ArrowDown")
                    page.wait_for_timeout(400)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(3500)
                    _didi_debug(f"typed address en selector {sel!r}")
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            page.wait_for_timeout(1500)


def scrape_didi_for_address(page: Page, address: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    line = f"{address['neighborhood']}, {address['city']}"
    # Refuerzo: permiso por origen (algunos builds muestran el prompt aunque el contexto tenga geo).
    try:
        ctx = page.context
        for origin in ("https://www.didi-food.com", "https://didi-food.com"):
            try:
                ctx.grant_permissions(["geolocation"], origin=origin)
            except Exception:
                pass
    except Exception:
        pass

    try:
        page.goto("https://www.didi-food.com/es-MX/food/", wait_until="domcontentloaded", timeout=55000)
        page.wait_for_timeout(2500)
        _didi_debug(f"URL final: {page.url}")
        try:
            title = page.title()
        except Exception:
            title = "?"
        _didi_debug(f"Título: {title[:200]}")
    except Exception as e:
        _didi_debug(f"goto falló: {e!s}")
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

    early_login = _didi_login_wall_detect(page)
    if early_login:
        _didi_debug(f"login wall: {early_login[:120]}")
        return _didi_rows_login_blocked(address, early_login)

    _pass_didi_location_gate(page, line)

    after_gate = _didi_login_wall_detect(page)
    if after_gate:
        _didi_debug(f"login wall tras ubicación: {after_gate[:120]}")
        return _didi_rows_login_blocked(address, after_gate)

    # Intentar localizar campo de dirección o búsqueda (pantalla principal)
    filled = False
    for sel in (
        'input[placeholder*="direcci" i]',
        'input[placeholder*="Direcci" i]',
        'input[type="search"]',
        "input[autocomplete='street-address']",
    ):
        loc = page.locator(sel)
        try:
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click(timeout=4000)
                loc.first.fill("", timeout=3000)
                loc.first.type(line, delay=35)
                page.wait_for_timeout(1800)
                page.keyboard.press("ArrowDown")
                page.wait_for_timeout(400)
                page.keyboard.press("Enter")
                page.wait_for_timeout(3000)
                filled = True
                _didi_debug(f"Campo dirección/búsqueda usado: {sel!r}")
                break
        except Exception:
            continue

    if not filled:
        _didi_debug("No se encontró input de dirección/búsqueda visible.")

    # Buscar McDonald's
    try:
        s = page.locator('input[type="search"], input[placeholder*="Buscar" i]')
        if s.count() > 0 and s.first.is_visible():
            s.first.fill("McDonald's")
            page.keyboard.press("Enter")
            page.wait_for_timeout(2500)
    except Exception:
        pass

    try:
        link = page.get_by_role("link", name=re.compile(r"mcdonald", re.I))
        if link.count() > 0:
            link.first.click(timeout=8000)
            page.wait_for_timeout(2500)
            _didi_debug("Clic en enlace McDonald's.")
    except Exception as e:
        _didi_debug(f"McDonald's link: {e!s}")

    late_login = _didi_login_wall_detect(page)
    if late_login:
        _didi_debug(f"login wall tardío: {late_login[:120]}")
        return _didi_rows_login_blocked(address, late_login)

    try:
        body = page.evaluate("() => document.body.innerText.slice(0, 80000)")
    except Exception:
        body = ""

    _didi_debug(f"Longitud texto visible: {len(body)} caracteres")
    if body:
        _didi_debug("--- Inicio del texto de la página (1200 chars) ---")
        _didi_debug(body[:1200].replace("\n", " ")[:1200])
        _didi_debug("--- fin ---")

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

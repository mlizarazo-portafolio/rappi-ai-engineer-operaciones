"""Patrones de texto reales en menú Rappi (McDonald's) para mapear al brief."""

from __future__ import annotations

import re

# Precio típico: "$ 159.00" o "$159.00"
_PRICE = r"\$\s*(\d{1,4}[.,]\d{2})"


def price_combo_big_mac(body: str) -> float | None:
    """McTrío mediano Big Mac (evita matchear la variante *Tocino*)."""
    m = re.search(
        rf"McTr[ií]o\s+mediano\s+Big\s+Mac(?!\s*Tocino)\s*\n\s*McTr[ií]o\s+mediano\s+Big\s+Mac(?!\s*Tocino)[\s\S]{{0,100}}?{_PRICE}",
        body,
        re.I,
    )
    if m:
        return _f(m.group(1))
    m = re.search(
        rf"McTr[ií]o\s+mediano\s+Big\s+Mac(?!\s*Tocino)[\s\S]{{0,120}}?{_PRICE}",
        body,
        re.I,
    )
    if m:
        return _f(m.group(1))
    m2 = re.search(rf"Home\s+Office\s+con\s+Big\s+Mac[\s\S]{{0,120}}?{_PRICE}", body, re.I)
    if m2:
        return _f(m2.group(1))
    return None


def price_coca_cola_600(body: str) -> float | None:
    """Bebida tipo Coca en menú (suelta o 600ml); evita combos caros."""
    for m in re.finditer(r"Coca[- ]?Cola", body, re.I):
        chunk = body[m.start() : m.start() + 500]
        p = re.search(_PRICE, chunk)
        if p:
            v = _f(p.group(1))
            if v is not None and v <= 95:
                return v
    m2 = re.search(rf"Refresco[^\n]{{0,30}}16\s*Oz[\s\S]{{0,100}}?{_PRICE}", body, re.I)
    if m2:
        return _f(m2.group(1))
    return None


def price_mcnuggets_10(body: str) -> float | None:
    m = re.search(
        rf"McTr[ií]o\s+mediano\s+McNuggets\s+10[\s\S]{{0,160}}?{_PRICE}",
        body,
        re.I,
    )
    if m:
        return _f(m.group(1))
    m2 = re.search(rf"10\s+McNuggets[\s\S]{{0,100}}?{_PRICE}", body, re.I)
    if m2:
        return _f(m2.group(1))
    return None


def _f(s: str) -> float | None:
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


EXTRACTORS = {
    "Combo Big Mac": price_combo_big_mac,
    "Coca-Cola 600ml": price_coca_cola_600,
    "McNuggets 10 piezas": price_mcnuggets_10,
}

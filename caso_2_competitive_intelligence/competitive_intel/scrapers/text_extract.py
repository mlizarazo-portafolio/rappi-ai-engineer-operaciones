"""Extrae precios MXN y ETA desde texto visible (menos frágil que CSS fijo)."""

from __future__ import annotations

import re

# Precios tipo $123, $123.45, 123,45, 123.45 MXN
_PRICE_PATTERNS = [
    re.compile(r"\$\s*(\d{1,4}(?:[.,]\d{1,2})?)"),
    re.compile(r"(\d{1,4}[.,]\d{2})\s*(?:MXN|mxn)?"),
]


def _normalize_mxn_num(raw: str) -> float | None:
    s = raw.strip().replace(",", ".")
    if s.count(".") > 1:
        s = s.replace(".", "", s.count(".") - 1)
    try:
        v = float(s)
        return v if 5 <= v <= 9999 else None
    except ValueError:
        return None


def price_near_keyword(text: str, keyword: str, radius: int = 200) -> float | None:
    """Busca el primer precio en ventana de caracteres tras la keyword."""
    lower = text.lower()
    k = keyword.lower()
    idx = lower.find(k)
    if idx < 0:
        # variantes cortas
        for short in k.split():
            if len(short) >= 4:
                idx = lower.find(short)
                if idx >= 0:
                    break
        if idx < 0:
            return None
    window = text[idx : idx + radius]
    for pat in _PRICE_PATTERNS:
        m = pat.search(window)
        if m:
            n = _normalize_mxn_num(m.group(1))
            if n is not None:
                return n
    return None


def price_near_keyword_multiline(text: str, keyword: str) -> float | None:
    """Busca precio en la misma línea o en las siguientes (menús en lista)."""
    lines = text.splitlines()
    k = keyword.lower()
    for i, line in enumerate(lines):
        if k not in line.lower():
            continue
        chunk = "\n".join(lines[i : min(i + 5, len(lines))])
        for pat in _PRICE_PATTERNS:
            m = pat.search(chunk)
            if m:
                n = _normalize_mxn_num(m.group(1))
                if n is not None:
                    return n
    return None


def delivery_fee_from_text(text: str) -> float | None:
    m = re.search(
        r"(?:env[ií]o|delivery|costo\s+de\s+env[ií]o)[^\d]{0,24}\$?\s*(\d{1,3}(?:[.,]\d{1,2})?)",
        text,
        re.I | re.DOTALL,
    )
    if m:
        return _normalize_mxn_num(m.group(1))
    m2 = re.search(r"\$\s*(\d{1,2}(?:[.,]\d{1,2})?)\s*(?:env[ií]o|delivery)", text, re.I)
    if m2:
        return _normalize_mxn_num(m2.group(1))
    return None


def service_fee_from_text(text: str) -> float | None:
    m = re.search(
        r"(?:service|servicio|comisi[oó]n)[^\d]{0,20}\$?\s*(\d{1,3}(?:[.,]\d{1,2})?)",
        text,
        re.I,
    )
    if m:
        return _normalize_mxn_num(m.group(1))
    return None


def eta_minutes_from_text(text: str) -> int | None:
    m = re.search(r"(\d{1,2})\s*[-–]?\s*(\d{1,2})?\s*min", text, re.I)
    if m:
        a = int(m.group(1))
        if m.group(2):
            b = int(m.group(2))
            return (a + b) // 2
        return a if 5 <= a <= 120 else None
    m2 = re.search(r"(\d{1,2})\s*min", text, re.I)
    if m2:
        v = int(m2.group(1))
        return v if 5 <= v <= 120 else None
    return None

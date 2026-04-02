"""Detección de respuestas tipo API con rate limit (Rappi / Uber: `bd.error.too_many_requests`, JSON en página)."""

from __future__ import annotations

import re
import sys
import time

from playwright.sync_api import Page


def page_looks_rate_limited(page: Page) -> bool:
    """
    True solo si el TEXTO VISIBLE del body parece error API / rate limit.

    No usa innerHTML: los bundles JS de Uber/Rappi suelen contener subcadenas como
    `too_many_requests` y generaban falsos positivos → el scraper nunca llegaba a la dirección.
    """
    try:
        t = page.evaluate(
            """() => {
            const b = document.body;
            if (!b) return '';
            return (b.innerText || '').trim().slice(0, 150000);
        }"""
        )
    except Exception:
        return False
    if not t:
        return False
    tl = t.lower()
    if "too_many_requests" in tl or "bd.error.too_many" in tl.replace(" ", ""):
        return True
    if "bd.error" in tl and "too_many" in tl:
        return True
    if ('"status":"failure"' in t or "'status':'failure'" in t or re.search(
        r"status\s*[:=]\s*[\"']failure[\"']", t, re.I
    )) and ("too_many" in tl or "bd.error" in tl):
        return True
    # Páginas de error cortas (solo JSON o mensaje)
    if len(t) < 2500 and ("rate limit" in tl or "too many request" in tl):
        return True
    return False


def cooldown_sleep(seconds: float, reason: str = "rate limit") -> None:
    print(f"[scrape] Pausa {seconds:.0f}s ({reason})...", file=sys.stderr, flush=True)
    time.sleep(seconds)

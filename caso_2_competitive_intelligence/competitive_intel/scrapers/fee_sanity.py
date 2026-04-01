"""Límites heurísticos para fees en MX (delivery apps); descarta extracciones regex erróneas."""

from __future__ import annotations

# Orden de magnitud típico CDMX/metro; ajustar si el mercado cambia.
MAX_SERVICE_FEE_MXN = 35.0
MAX_DELIVERY_FEE_MXN = 99.0


def sanitize_fees_mxn(
    delivery: float | None,
    service: float | None,
) -> tuple[float | None, float | None]:
    d, s = delivery, service
    if d is not None and (d < 0 or d > MAX_DELIVERY_FEE_MXN):
        d = None
    if s is not None and (s < 0 or s > MAX_SERVICE_FEE_MXN):
        s = None
    return d, s

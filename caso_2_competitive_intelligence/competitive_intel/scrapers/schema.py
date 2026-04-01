"""Esquema de filas compatible con `demo_scrape` y `report_ci`."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# Mismos productos que el demo (brief: ítems comparables tipo McDonald's).
PRODUCTS: list[str] = [
    "Combo Big Mac",
    "Coca-Cola 600ml",
    "McNuggets 10 piezas",
]

CSV_COLUMNS: list[str] = [
    "data_source",
    "platform",
    "address_id",
    "city",
    "neighborhood",
    "zone_type",
    "lat",
    "lon",
    "product_name",
    "item_price_mxn",
    "delivery_fee_mxn",
    "service_fee_mxn",
    "total_checkout_mxn",
    "eta_minutes",
    "promotions_visible",
    "store_available",
    "scraped_at",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_row(
    *,
    data_source: str,
    platform: str,
    address: dict[str, Any],
    product_name: str,
    item_price_mxn: float | None,
    delivery_fee_mxn: float | None = None,
    service_fee_mxn: float | None = None,
    total_checkout_mxn: float | None = None,
    eta_minutes: int | None = None,
    promotions_visible: str = "Ninguna visible",
    store_available: bool = True,
    scraped_at: str | None = None,
) -> dict[str, Any]:
    total = total_checkout_mxn
    if total is None and item_price_mxn is not None:
        d = delivery_fee_mxn or 0.0
        s = service_fee_mxn or 0.0
        total = round(float(item_price_mxn) + float(d) + float(s), 2)
    return {
        "data_source": data_source,
        "platform": platform,
        "address_id": address["id"],
        "city": address["city"],
        "neighborhood": address["neighborhood"],
        "zone_type": address["zone_type"],
        "lat": address["lat"],
        "lon": address["lon"],
        "product_name": product_name,
        "item_price_mxn": item_price_mxn,
        "delivery_fee_mxn": delivery_fee_mxn,
        "service_fee_mxn": service_fee_mxn,
        "total_checkout_mxn": total,
        "eta_minutes": eta_minutes,
        "promotions_visible": promotions_visible,
        "store_available": store_available,
        "scraped_at": scraped_at or now_iso(),
    }

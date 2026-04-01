"""
Genera CSV de demostración (México, Rappi / Uber Eats / DiDi Food).

El brief pide scraping real; las apps cambian y bloquean bots. Este módulo
produce datos **sintéticos reproducibles** (seed fija) para pipeline e informe.
Scrape web real: `python -m competitive_intel scrape` (Playwright, ver `scrapers/README.md`).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from competitive_intel.paths import addresses_json_path, default_scrape_csv

PRODUCTS = [
    "Combo Big Mac",
    "Coca-Cola 600ml",
    "McNuggets 10 piezas",
]
PLATFORMS = ["rappi", "uber_eats", "didi_food"]


def load_addresses() -> list[dict]:
    raw = json.loads(addresses_json_path().read_text(encoding="utf-8"))
    return list(raw["addresses"])


def generate_demo_rows(rng: np.random.Generator | None = None) -> pd.DataFrame:
    rng = rng or np.random.default_rng(42)
    rows = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    addresses = load_addresses()

    # Sesgos ligeros por plataforma (orden de magnitud realista demo)
    platform_fee_bias = {"rappi": 1.0, "uber_eats": 0.92, "didi_food": 0.88}
    platform_price_bias = {"rappi": 1.02, "uber_eats": 1.0, "didi_food": 0.97}
    platform_eta_bias = {"rappi": 1.0, "uber_eats": 1.08, "didi_food": 1.12}

    for addr in addresses:
        for platform in PLATFORMS:
            for product in PRODUCTS:
                base_item = rng.uniform(95, 195) * platform_price_bias[platform]
                item_price = round(base_item, 2)
                delivery_fee = round(rng.uniform(15, 45) * platform_fee_bias[platform], 2)
                service_fee = round(rng.uniform(5, 18) * platform_fee_bias[platform], 2)
                total = round(item_price + delivery_fee + service_fee - rng.choice([0, 0, 5, 12]), 2)
                eta = int(rng.integers(22, 48) * platform_eta_bias[platform])
                promos = rng.choice(
                    [
                        "Ninguna visible",
                        "Envío gratis pedido mínimo",
                        "2x1 en bebidas",
                        "Descuento primera orden",
                        "Cupón zona",
                    ],
                    p=[0.35, 0.25, 0.15, 0.15, 0.1],
                )
                rows.append(
                    {
                        "data_source": "synthetic_demo",
                        "platform": platform,
                        "address_id": addr["id"],
                        "city": addr["city"],
                        "neighborhood": addr["neighborhood"],
                        "zone_type": addr["zone_type"],
                        "lat": addr["lat"],
                        "lon": addr["lon"],
                        "product_name": product,
                        "item_price_mxn": item_price,
                        "delivery_fee_mxn": delivery_fee,
                        "service_fee_mxn": service_fee,
                        "total_checkout_mxn": total,
                        "eta_minutes": eta,
                        "promotions_visible": promos,
                        "store_available": rng.random() > 0.03,
                        "scraped_at": now,
                    }
                )
    return pd.DataFrame(rows)


def write_demo_scrape(path: Path | None = None) -> Path:
    path = path or default_scrape_csv()
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_demo_rows()
    df.to_csv(path, index=False, encoding="utf-8")
    return path

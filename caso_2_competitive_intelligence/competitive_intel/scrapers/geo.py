"""Mapeo ciudad (JSON de direcciones) → slug de URL en rappi.com.mx."""

from __future__ import annotations

# Slugs observados en rutas públicas tipo /{slug}/restaurantes/...
CITY_TO_RAPPI_SLUG: dict[str, str] = {
    "Ciudad de México": "ciudad-de-mexico",
    "Guadalajara": "guadalajara",
    "Monterrey": "monterrey",
    "Puebla": "puebla",
    "Querétaro": "queretaro",
    "Mérida": "merida",
    "Cancún": "cancun",
    "Tijuana": "tijuana",
    "León": "leon",
    "Aguascalientes": "aguascalientes",
    "Veracruz": "veracruz",
    "Hermosillo": "hermosillo",
    "Culiacán": "culiacan",
    "Chihuahua": "chihuahua",
    "Mexicali": "mexicali",
}


def rappi_slug_for_city(city: str) -> str | None:
    return CITY_TO_RAPPI_SLUG.get(city.strip())

"""Rutas del caso Competitive Intelligence (raíz del monorepo)."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Raíz del monorepo (`data/`, `reports/`, etc.)."""
    return Path(__file__).resolve().parents[2]


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def output_dir() -> Path:
    p = project_root() / "data" / "caso_2_competitive_intelligence" / "output"
    p.mkdir(parents=True, exist_ok=True)
    return p


def reports_dir() -> Path:
    p = package_dir() / "reports"
    p.mkdir(parents=True, exist_ok=True)
    return p


def addresses_json_path() -> Path:
    return package_dir() / "addresses_mx.json"


def default_scrape_csv() -> Path:
    return output_dir() / "scrape_latest.csv"

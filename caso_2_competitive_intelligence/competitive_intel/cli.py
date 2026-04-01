"""CLI: `python -m competitive_intel demo|report`"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from competitive_intel.demo_scrape import write_demo_scrape
from competitive_intel.paths import default_scrape_csv
from competitive_intel.report_ci import build_report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Competitive Intelligence — México (Rappi / Uber Eats / DiDi Food)")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="Genera CSV sintético en data/caso_2_competitive_intelligence/output/")
    d.add_argument("-o", "--output", type=Path, default=None, help="Ruta CSV (default: scrape_latest.csv)")

    r = sub.add_parser("report", help="Construye informe Markdown + figuras desde el CSV")
    r.add_argument("-i", "--input", type=Path, default=None, help="CSV (default: scrape_latest.csv)")

    s = sub.add_parser("scrape", help="Stub: hoy escribe el mismo demo (scrape real → implementar en scrapers/)")
    s.add_argument("-o", "--output", type=Path, default=None)

    args = p.parse_args(argv)

    if args.cmd == "demo":
        path = write_demo_scrape(args.output)
        print(f"CSV demo escrito: {path}")
        return 0

    if args.cmd == "scrape":
        print(
            "Nota: scrape real requiere Playwright + selectores por app (anti-bot). "
            "Se genera CSV demo equivalente a `demo`."
        )
        path = write_demo_scrape(args.output)
        print(f"CSV escrito: {path}")
        return 0

    if args.cmd == "report":
        try:
            out = build_report(args.input)
            print(f"Informe: {out}")
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            return 1
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

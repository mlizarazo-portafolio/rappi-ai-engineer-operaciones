"""CLI: `python -m competitive_intel demo|report`"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from competitive_intel.demo_scrape import write_demo_scrape
from competitive_intel.paths import default_scrape_csv
from competitive_intel.scrapers.live_pipeline import run_live_scrape


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Competitive Intelligence — México (Rappi / Uber Eats / DiDi Food)")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="Genera CSV sintético en data/caso_2_competitive_intelligence/output/")
    d.add_argument("-o", "--output", type=Path, default=None, help="Ruta CSV (default: scrape_latest.csv)")

    r = sub.add_parser("report", help="Construye informe Markdown + figuras desde el CSV")
    r.add_argument("-i", "--input", type=Path, default=None, help="CSV (default: scrape_latest.csv)")

    s = sub.add_parser(
        "scrape",
        help="Playwright: web pública Rappi + Uber Eats + intento DiDi (ver scrapers/README.md)",
    )
    s.add_argument("-o", "--output", type=Path, default=None)
    s.add_argument(
        "--platforms",
        type=str,
        default="rappi,uber_eats,didi_food",
        help="Comma-separated: rappi,uber_eats,didi_food",
    )
    s.add_argument("--limit-addresses", type=int, default=None, help="Solo las primeras N direcciones (pruebas)")
    s.add_argument("--headed", action="store_true", help="Navegador visible (depuración)")
    s.add_argument("--delay", type=float, default=2.0, help="Pausa entre pasos de plataforma (s)")
    s.add_argument(
        "--fallback-demo",
        action="store_true",
        help="Si falla el scrape (p.ej. sin Playwright), escribe CSV sintético como demo",
    )

    args = p.parse_args(argv)

    if args.cmd == "demo":
        path = write_demo_scrape(args.output)
        print(f"CSV demo escrito: {path}")
        return 0

    if args.cmd == "scrape":
        plats = [x.strip() for x in args.platforms.split(",") if x.strip()]
        try:
            path = run_live_scrape(
                output=args.output,
                platforms=plats,
                limit_addresses=args.limit_addresses,
                headless=not args.headed,
                delay_sec=args.delay,
            )
            print(f"CSV scrape (Playwright): {path}")
            return 0
        except Exception as e:
            print(f"Error en scrape: {e}", file=sys.stderr)
            if args.fallback_demo:
                path = write_demo_scrape(args.output)
                print(f"Fallback demo: {path}", file=sys.stderr)
                return 0
            print(
                "Instala navegador: playwright install chromium. "
                "O usa: python -m competitive_intel demo",
                file=sys.stderr,
            )
            return 1

    if args.cmd == "report":
        from competitive_intel.report_ci import build_report

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

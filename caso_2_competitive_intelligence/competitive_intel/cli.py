"""CLI: `python -m competitive_intel demo|report`"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from competitive_intel.demo_scrape import write_demo_scrape
from competitive_intel.merge_scrapes import merge_scrape_csvs
from competitive_intel.paths import default_scrape_csv
from competitive_intel.scrapers.live_pipeline import run_live_scrape, run_save_didi_session


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
        default="uber_eats,rappi",
        help="Comma-separated: uber_eats,rappi,didi_food (orden: Uber primero suele ir mejor en corridas largas)",
    )
    s.add_argument("--limit-addresses", type=int, default=None, help="Solo las primeras N direcciones (pruebas)")
    s.add_argument(
        "--skip-addresses",
        type=int,
        default=0,
        help="Salta las primeras K direcciones del CSV (útil para segunda mitad en corridas partidas)",
    )
    s.add_argument(
        "--headed",
        "--show-browser",
        action="store_true",
        help="Ventana del navegador visible: ves en vivo qué hace Playwright (clics, búsqueda, etc.)",
    )
    s.add_argument("--delay", type=float, default=2.0, help="Pausa entre pasos de plataforma (s)")
    s.add_argument(
        "--fallback-demo",
        action="store_true",
        help="Si falla el scrape (p.ej. sin Playwright), escribe CSV sintético como demo",
    )
    s.add_argument(
        "--browser",
        type=str,
        default=None,
        choices=("chromium", "firefox", "webkit"),
        help="Motor Playwright (default: env PLAYWRIGHT_BROWSER o firefox). Chromium si lo prefieres.",
    )
    s.add_argument(
        "--quiet",
        action="store_true",
        help="Sin líneas de progreso en consola (por defecto se muestra avance por paso)",
    )

    ss = sub.add_parser(
        "save-didi-session",
        help="Abre DiDi, inicias sesión a mano; Enter guarda cookies (PLAYWRIGHT_STORAGE_STATE). Ver .env.example",
    )
    ss.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Ruta del JSON de sesión (default: didi_storage_state.json en la raíz del repo)",
    )
    ss.add_argument(
        "--headless",
        action="store_true",
        help="Sin ventana (no sirve para login; solo pruebas)",
    )
    ss.add_argument(
        "--browser",
        type=str,
        default=None,
        choices=("chromium", "firefox", "webkit"),
        help="Motor Playwright (default: env o firefox)",
    )

    m = sub.add_parser(
        "merge-scrapes",
        help="Fusiona varios CSV de scrape; por (plataforma, dirección, producto) gana fila con precio",
    )
    m.add_argument("inputs", nargs="+", type=Path, help="Rutas a CSV")
    m.add_argument("-o", "--output", type=Path, default=None, help="Salida (default: scrape_latest.csv)")

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
                skip_addresses=max(0, args.skip_addresses),
                headless=not args.headed,
                delay_sec=args.delay,
                browser=args.browser,
                progress=not args.quiet,
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
                "Instala navegador: playwright install firefox  (o chromium con --browser chromium). "
                "O usa: python -m competitive_intel demo",
                file=sys.stderr,
            )
            return 1

    if args.cmd == "merge-scrapes":
        try:
            out = merge_scrape_csvs(list(args.inputs), args.output)
            print(f"CSV fusionado: {out}")
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if args.cmd == "save-didi-session":
        try:
            run_save_didi_session(
                output=args.output,
                headless=args.headless,
                browser=args.browser,
            )
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
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

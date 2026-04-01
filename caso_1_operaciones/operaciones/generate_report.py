"""
Genera informe de insights (Markdown + HTML) en `reports/`.

Uso (desde la carpeta `caso_1_operaciones/`):
  python -m operaciones.generate_report
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

_PKG_PARENT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_PKG_PARENT) not in sys.path:
    sys.path.insert(0, str(_PKG_PARENT))

from operaciones.insights_engine import run_all
from operaciones.report_markdown import build_markdown_report, markdown_to_report_html


def main() -> None:
    out_dir = _REPO_ROOT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    md_path = out_dir / f"insights_executive_{stamp}.md"
    html_path = out_dir / f"insights_executive_{stamp}.html"

    bundle = run_all()
    md = build_markdown_report(bundle)
    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(markdown_to_report_html(md), encoding="utf-8")

    print(f"Markdown: {md_path}")
    print(f"HTML:     {html_path}")


if __name__ == "__main__":
    main()

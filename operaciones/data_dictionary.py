"""
Carga `data/operaciones/RAW_SUMMARY.csv` (diccionario de columnas del caso).
Requisito del enunciado: usar los tres archivos compartidos.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from operaciones.data import project_root


def summary_path() -> Path:
    return project_root() / "data" / "operaciones" / "RAW_SUMMARY.csv"


def load_data_dictionary_for_prompt(max_chars: int = 4000) -> str:
    """Texto compacto para el system prompt del bot."""
    path = summary_path()
    if not path.exists():
        return ""

    df = pd.read_csv(path)
    desc_col = "Description (inferred)"
    if "Column" not in df.columns or desc_col not in df.columns:
        return ""

    lines = [
        "Referencia de columnas según **RAW_SUMMARY.csv** (diccionario del dataset de métricas):",
        "En los CSV entregados, las semanas en métricas se nombran **L0W_ROLL…L8W_ROLL** (no L0W_VALUE); órdenes usan **L0W…L8W**.",
        "",
    ]
    for _, row in df.iterrows():
        col = row.get("Column")
        if pd.isna(col) or str(col).strip() == "":
            continue
        typ = row.get("Type", "")
        desc = row.get(desc_col, "")
        if pd.isna(desc):
            desc = ""
        ex = row.get("Examples", "")
        bit = f"- **{col}** (`{typ}`): {str(desc).strip()}"
        if not pd.isna(ex) and str(ex).strip():
            bit += f" Ejemplos: {str(ex).strip()[:120]}"
        lines.append(bit)

    text = "\n".join(lines)
    if len(text) > max_chars:
        return text[: max_chars - 20] + "\n…(truncado)"
    return text

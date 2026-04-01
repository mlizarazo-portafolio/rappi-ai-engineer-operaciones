"""
Bot conversacional — caso Operaciones Rappi.

Desde la raíz del repo (con venv activado):
  streamlit run operaciones/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Streamlit pone en sys.path la carpeta del script (`operaciones/`), no la raíz del repo;
# hace falta la raíz para `import operaciones`.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from operaciones.chat import build_system_prompt, run_chat_turn
from operaciones.data import load_metrics, load_orders
from operaciones.data_dictionary import load_data_dictionary_for_prompt
from operaciones.tools import ToolExecutor

load_dotenv(_ROOT / ".env")

st.set_page_config(page_title="Rappi Ops Bot", page_icon="📊", layout="wide")

SUGGESTIONS = [
    "¿Cuáles son las 5 zonas con mayor Lead Penetration esta semana en México?",
    "Compara Perfect Orders entre zonas Wealthy y Non Wealthy en México",
    "Muestra la evolución de Gross Profit UE en Chapinero las últimas 8 semanas",
    "¿Cuál es el promedio de Lead Penetration por país?",
    "¿Qué zonas tienen alto Lead Penetration pero bajo Perfect Orders?",
    "¿Cuáles son las zonas que más crecen en órdenes en las últimas 5 semanas y qué métricas las acompañan?",
    "¿Qué zonas problemáticas hay en Gross Profit UE en Colombia?",
]


@st.cache_data
def _datasets() -> tuple[Any, Any]:
    return load_metrics(), load_orders()


@st.cache_data
def _system_prompt_full() -> str:
    return build_system_prompt(load_data_dictionary_for_prompt())


def main() -> None:
    st.title("Rappi — bot de operaciones")
    st.caption(
        "Datos: `docs/RAW_INPUT_METRICS.csv`, `docs/RAW_ORDERS.csv` y diccionario `docs/RAW_SUMMARY.csv`. "
        "Requiere `OPENAI_API_KEY`."
    )

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        st.error(
            "Falta `OPENAI_API_KEY`. Crea un archivo `.env` en la raíz del proyecto "
            "(ver `.env.example`) o define la variable en el entorno."
        )
        return

    metrics, orders = _datasets()
    executor = ToolExecutor(metrics, orders)

    system_content = _system_prompt_full()
    if "api_messages" not in st.session_state:
        st.session_state.api_messages = [{"role": "system", "content": system_content}]

    with st.sidebar:
        st.subheader("Sugerencias")
        for i, s in enumerate(SUGGESTIONS):
            if st.button(s[:72] + ("…" if len(s) > 72 else ""), key=f"sug_{i}"):
                st.session_state["pending_prompt"] = s
        if st.button("Nueva conversación"):
            st.session_state.api_messages = [{"role": "system", "content": _system_prompt_full()}]
            st.session_state.pop("pending_prompt", None)
            st.rerun()

    # Re-render chat from api_messages (solo user/assistant visibles)
    for m in st.session_state.api_messages:
        if m["role"] == "user":
            with st.chat_message("user"):
                st.markdown(m["content"])
        elif m["role"] == "assistant" and m.get("content"):
            with st.chat_message("assistant"):
                st.markdown(m["content"])

    pending = st.session_state.pop("pending_prompt", None)
    user_text = st.chat_input("Pregunta sobre zonas, métricas u órdenes…")
    prompt = pending or user_text

    if prompt:
        st.session_state.api_messages.append({"role": "user", "content": prompt})
        client = OpenAI(api_key=api_key)
        with st.spinner("Consultando datos…"):
            st.session_state.api_messages, _ = run_chat_turn(
                client,
                st.session_state.api_messages,
                executor,
            )
        st.rerun()


if __name__ == "__main__":
    main()

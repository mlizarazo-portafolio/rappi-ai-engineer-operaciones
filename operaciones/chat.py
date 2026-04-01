"""Un turno de chat con OpenAI + herramientas pandas."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from operaciones.tool_schemas import OPENAI_TOOLS
from operaciones.tools import ToolExecutor

SYSTEM_PROMPT = """Eres un analista de operaciones de Rappi. Respondes en español.

Reglas:
- Para números, tablas o rankings SIEMPRE usa las herramientas; no inventes cifras.
- Los datos de métricas usan columnas L0W_ROLL (semana actual) … L8W_ROLL (hace 8 semanas). Las órdenes usan L0W…L8W.
- "México" = código MX; "Colombia" = CO, etc.
- "Zonas problemáticas" / "mal desempeño": usa la herramienta problematic_zones o compara caídas; no asumas sin datos.
- Si el usuario pide gráficos y no tienes herramienta de gráfico, resume en tabla y ofrece describir el patrón.
- Sé conciso; cita país/ciudad/zona cuando la herramienta lo devuelva.
"""


def run_chat_turn(
    client: OpenAI,
    api_messages: list[dict[str, Any]],
    executor: ToolExecutor,
    model: str = "gpt-4o-mini",
    max_tool_rounds: int = 6,
) -> tuple[list[dict[str, Any]], str]:
    """
    Añade el mensaje del usuario a api_messages antes de llamar (caller responsibility).
    Devuelve (api_messages_actualizados, último_texto_asistente).
    """
    rounds = 0
    last_assistant_text = ""

    while rounds < max_tool_rounds:
        rounds += 1
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = response.choices[0].message
        finish = response.choices[0].finish_reason

        if msg.tool_calls:
            api_messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments or "{}",
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                }
            )
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                out = executor.run(tc.function.name, args)
                api_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": out[:120000],
                    }
                )
            continue

        last_assistant_text = msg.content or ""
        api_messages.append({"role": "assistant", "content": last_assistant_text})
        if finish == "stop":
            break

    return api_messages, last_assistant_text

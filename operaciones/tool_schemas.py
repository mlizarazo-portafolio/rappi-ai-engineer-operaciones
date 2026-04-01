"""Definiciones de tools para OpenAI Chat Completions (function calling)."""

from typing import Any

OPENAI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_available_metrics",
            "description": "Lista los nombres exactos de métricas en el dataset. Úsalo si no estás seguro del nombre.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_zones_by_metric",
            "description": "Ranking de zonas por una métrica operacional en una semana (por defecto L0W_ROLL = semana actual).",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string"},
                    "country_code": {
                        "type": "string",
                        "description": "Código ISO2 (MX, CO) o nombre (México, Colombia). Opcional.",
                    },
                    "n": {"type": "integer", "description": "Cantidad de zonas (default 5)", "default": 5},
                    "week_column": {
                        "type": "string",
                        "description": "L0W_ROLL..L8W_ROLL",
                        "default": "L0W_ROLL",
                    },
                },
                "required": ["metric_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_zone_types",
            "description": "Compara promedio de una métrica entre Wealthy y Non Wealthy en un país.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string"},
                    "country_code": {"type": "string"},
                    "week_column": {"type": "string", "default": "L0W_ROLL"},
                },
                "required": ["metric_name", "country_code"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "metric_trend_for_zone",
            "description": "Serie semanal L8W_ROLL..L0W_ROLL de una métrica para una zona (búsqueda parcial en nombre de zona).",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string"},
                    "zone_search": {"type": "string", "description": "Texto que aparece en ZONE, ej. Chapinero"},
                    "country_code": {"type": "string", "description": "Opcional, ej. CO"},
                },
                "required": ["metric_name", "zone_search"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "average_metric_by_country",
            "description": "Promedio de una métrica por país.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string"},
                    "week_column": {"type": "string", "default": "L0W_ROLL"},
                },
                "required": ["metric_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "zones_high_metric_low_metric",
            "description": "Zonas con una métrica alta (percentil 75) y otra baja (percentil 25) en L0W_ROLL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "high_metric_name": {"type": "string"},
                    "low_metric_name": {"type": "string"},
                    "country_code": {"type": "string"},
                    "top_n": {"type": "integer", "default": 15},
                },
                "required": ["high_metric_name", "low_metric_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_growing_orders_zones",
            "description": "Zonas con mayor crecimiento porcentual de órdenes comparando L0W vs L{n}W (default n=5). Incluye contexto de métricas en esas zonas (no causal).",
            "parameters": {
                "type": "object",
                "properties": {
                    "num_weeks": {"type": "integer", "default": 5},
                    "top_n": {"type": "integer", "default": 10},
                    "country_code": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "problematic_zones",
            "description": "Zonas con fuerte deterioro semana a semana en una métrica (útil para 'zonas problemáticas').",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_name": {
                        "type": "string",
                        "description": "Opcional; default Gross Profit UE",
                    },
                    "country_code": {"type": "string"},
                    "threshold_pct": {"type": "number", "default": 10.0},
                    "top_n": {"type": "integer", "default": 10},
                },
                "additionalProperties": False,
            },
        },
    },
]

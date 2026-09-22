"""Configuración del modelo compatible con OpenAI de Groq."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from smolagents import OpenAIModel

load_dotenv(Path(__file__).resolve().parent / ".env")


def create_model() -> OpenAIModel:
    """Construye el modelo de Groq usando sólo variables de entorno."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y agrega tu clave de Groq."
        )

    return OpenAIModel(
        model_id=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        api_base=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=api_key,
        temperature=0.2,
        max_tokens=1000,
    )

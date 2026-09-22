"""Configuración del modelo compatible con OpenAI de Groq."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")


def create_client() -> OpenAI:
    """Construye el cliente OpenAI-compatible de Groq."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y agrega tu clave de Groq."
        )

    return OpenAI(
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=api_key,
        timeout=30,
        max_retries=2,
    )


def model_name() -> str:
    """Devuelve el modelo configurado para Groq."""

    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

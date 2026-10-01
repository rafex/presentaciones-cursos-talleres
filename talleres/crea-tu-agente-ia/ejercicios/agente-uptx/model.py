"""Configuración del cliente de Groq.

Groq ofrece un endpoint compatible con la API de OpenAI. Este módulo concentra
la lectura de variables de entorno y la creación del cliente para que el resto
del agente no tenga que conocer URLs, timeouts ni nombres de variables.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# El .env vive junto al ejercicio, no depende del directorio desde el que se
# ejecute el comando.
load_dotenv(Path(__file__).resolve().parent / ".env")


def create_client() -> OpenAI:
    """Construye el cliente OpenAI-compatible de Groq.

    La clave se exige en tiempo de ejecución y nunca se define como constante
    en el código. ``max_retries`` cubre fallos transitorios sin esconder un
    error permanente de configuración.
    """

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
    """Devuelve el modelo configurado para Groq o el modelo del taller."""

    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

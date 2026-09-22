"""Tools reales que el agente puede elegir durante la conversación."""

from __future__ import annotations

from pathlib import Path

import requests
from smolagents import tool

from retriever import UPTxRetriever

ROOT = Path(__file__).resolve().parent
retriever = UPTxRetriever(ROOT / "knowledge" / "uptx.md")


@tool
def obtener_clima(ciudad: str) -> str:
    """Obtiene el clima actual de una ciudad usando Open-Meteo.

    Args:
        ciudad: Ciudad o municipio que se desea consultar.
    """

    geocoding = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ciudad, "count": 1, "language": "es", "format": "json"},
        timeout=10,
    )
    geocoding.raise_for_status()
    results = geocoding.json().get("results", [])
    if not results:
        return f"No encontré coordenadas para {ciudad}."

    location = results[0]
    latitude = location["latitude"]
    longitude = location["longitude"]
    forecast = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
            "timezone": "auto",
        },
        timeout=10,
    )
    forecast.raise_for_status()
    current = forecast.json().get("current", {})

    return (
        f"Clima actual en {location.get('name', ciudad)}, {location.get('country', '')}: "
        f"{current.get('temperature_2m', 'sin dato')} °C, "
        f"sensación térmica {current.get('apparent_temperature', 'sin dato')} °C, "
        f"humedad {current.get('relative_humidity_2m', 'sin dato')} %, "
        f"viento {current.get('wind_speed_10m', 'sin dato')} km/h. "
        "Fuente: https://open-meteo.com/"
    )


@tool
def consultar_uptx(pregunta: str) -> str:
    """Consulta información institucional de la Universidad Politécnica de Tlaxcala.

    Args:
        pregunta: Pregunta sobre carreras, admisión, ciclos, cursos o reglamento.
    """

    matches = retriever.search(pregunta)
    if not matches:
        return (
            "No encontré información suficiente en la base UPTx local. "
            "Consulta directamente las fuentes oficiales incluidas en el Markdown."
        )

    evidence = []
    for match in matches:
        evidence.append(f"[{match.heading}]\n{match.text}")
    return "\n\n---\n\n".join(evidence)


TOOLS = [obtener_clima, consultar_uptx]

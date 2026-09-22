"""Tools del agente y sus esquemas OpenAI function calling."""

from __future__ import annotations

from pathlib import Path

import requests

from retriever import UPTxRetriever

ROOT = Path(__file__).resolve().parent
retriever = UPTxRetriever(ROOT / "knowledge" / "uptx.md")


def obtener_clima(ciudad: str) -> str:
    """Obtiene el clima actual de una ciudad usando Open-Meteo."""

    try:
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
        forecast = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=10,
        )
        forecast.raise_for_status()
        current = forecast.json().get("current", {})
    except requests.RequestException as error:
        return f"No pude consultar el clima de {ciudad}: {error}"

    return (
        f"Clima actual en {location.get('name', ciudad)}, {location.get('country', '')}: "
        f"{current.get('temperature_2m', 'sin dato')} °C, "
        f"sensación térmica {current.get('apparent_temperature', 'sin dato')} °C, "
        f"humedad {current.get('relative_humidity_2m', 'sin dato')} %, "
        f"viento {current.get('wind_speed_10m', 'sin dato')} km/h. "
        "Fuente: https://open-meteo.com/"
    )


def consultar_uptx(pregunta: str) -> str:
    """Consulta información institucional de la Universidad Politécnica de Tlaxcala."""

    matches = retriever.search(pregunta)
    if not matches:
        return (
            "No encontré información suficiente en la base UPTx local. "
            "Consulta directamente las fuentes oficiales incluidas en el Markdown."
        )

    return "\n\n---\n\n".join(f"[{match.heading}]\n{match.text}" for match in matches)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Obtiene las condiciones meteorológicas actuales de una ciudad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Ciudad o municipio que se desea consultar.",
                    }
                },
                "required": ["ciudad"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_uptx",
            "description": "Consulta carreras, admisión, ciclos, cursos y reglamento de la UPTx.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pregunta": {
                        "type": "string",
                        "description": "Pregunta sobre información institucional de la UPTx.",
                    }
                },
                "required": ["pregunta"],
                "additionalProperties": False,
            },
        },
    },
]

FUNCTIONS = {
    "obtener_clima": obtener_clima,
    "consultar_uptx": consultar_uptx,
}

# /// script
# requires-python = ">=3.11"
# dependencies = ["groq", "requests"]
# ///
"""
Agente super basico: responde preguntas sobre el clima.

Como ejecutarlo:
    export GROQ_API_KEY=gsk_...      # gratis en https://console.groq.com/keys
    uv run clima.py "¿que clima hay en Tlaxcala?"
"""
import json
import os
import sys

import requests
from groq import Groq

MODELO = "llama-3.3-70b-versatile"


def obtener_coordenadas(ciudad: str) -> dict:
    """Convierte el nombre de una ciudad en latitud/longitud."""
    resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ciudad, "count": 1, "language": "es"},
        timeout=10,
    )
    resultados = resp.json().get("results") or []
    if not resultados:
        return {"error": f"No encontre la ciudad '{ciudad}'"}
    lugar = resultados[0]
    return {"latitud": lugar["latitude"], "longitud": lugar["longitude"], "nombre": lugar["name"]}


def obtener_clima(latitud: float, longitud: float) -> dict:
    """Da el clima actual para unas coordenadas."""
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": latitud, "longitude": longitud, "current_weather": True, "timezone": "auto"},
        timeout=10,
    )
    return resp.json()["current_weather"]


HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_coordenadas",
            "description": "Convierte el nombre de una ciudad en latitud/longitud.",
            "parameters": {
                "type": "object",
                "properties": {"ciudad": {"type": "string", "description": "Nombre de la ciudad"}},
                "required": ["ciudad"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Da el clima actual (temperatura, viento) para unas coordenadas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitud": {"type": "number"},
                    "longitud": {"type": "number"},
                },
                "required": ["latitud", "longitud"],
            },
        },
    },
]

FUNCIONES = {"obtener_coordenadas": obtener_coordenadas, "obtener_clima": obtener_clima}


def preguntar_al_agente(pregunta: str) -> str:
    cliente = Groq(api_key=os.environ["GROQ_API_KEY"])
    mensajes = [
        {"role": "system", "content": "Eres un agente que responde sobre el clima. Usa las herramientas cuando las necesites."},
        {"role": "user", "content": pregunta},
    ]

    for _ in range(5):  # tope de seguridad: maximo 5 vueltas del ciclo
        respuesta = cliente.chat.completions.create(model=MODELO, messages=mensajes, tools=HERRAMIENTAS)
        mensaje = respuesta.choices[0].message
        mensajes.append(mensaje)

        if not mensaje.tool_calls:
            return mensaje.content

        for llamada in mensaje.tool_calls:
            funcion = FUNCIONES[llamada.function.name]
            argumentos = json.loads(llamada.function.arguments)
            resultado = funcion(**argumentos)
            print(f"  -> el agente uso {llamada.function.name}({argumentos})")
            mensajes.append({
                "role": "tool",
                "tool_call_id": llamada.id,
                "content": json.dumps(resultado),
            })

    return "No pude resolverlo en el numero de intentos permitido."


if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or "¿Que clima hay en Tlaxcala?"
    print(preguntar_al_agente(pregunta))

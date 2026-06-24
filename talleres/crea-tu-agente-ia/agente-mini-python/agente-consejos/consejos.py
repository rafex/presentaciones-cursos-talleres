# /// script
# requires-python = ">=3.11"
# dependencies = ["groq", "requests"]
# ///
"""
Agente super basico: da consejos usando Advice Slip API.

Como ejecutarlo:
    export GROQ_API_KEY=gsk_...      # gratis en https://console.groq.com/keys
    uv run consejos.py "dame un consejo sobre el amor"
"""
import json
import os
import sys

import requests
from groq import Groq

MODELO = "llama-3.3-70b-versatile"


def obtener_consejo_aleatorio() -> dict:
    """Da un consejo al azar."""
    resp = requests.get("https://api.adviceslip.com/advice", timeout=10)
    return resp.json()["slip"]


def buscar_consejo(palabra: str) -> dict:
    """Busca consejos que contengan una palabra clave."""
    resp = requests.get(f"https://api.adviceslip.com/advice/search/{palabra}", timeout=10)
    datos = resp.json()
    if "slips" not in datos:
        return {"error": f"No encontre consejos sobre '{palabra}'"}
    return {"consejos": [s["advice"] for s in datos["slips"][:3]]}


HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_consejo_aleatorio",
            "description": "Da un consejo al azar, sin tema en especifico.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_consejo",
            "description": "Busca consejos relacionados con una palabra clave, ej. 'love' o 'money'.",
            "parameters": {
                "type": "object",
                "properties": {"palabra": {"type": "string", "description": "Palabra clave en ingles"}},
                "required": ["palabra"],
            },
        },
    },
]

FUNCIONES = {"obtener_consejo_aleatorio": obtener_consejo_aleatorio, "buscar_consejo": buscar_consejo}


def preguntar_al_agente(pregunta: str) -> str:
    cliente = Groq(api_key=os.environ["GROQ_API_KEY"])
    mensajes = [
        {"role": "system", "content": "Eres un agente que da consejos. Usa las herramientas cuando las necesites."},
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
    pregunta = " ".join(sys.argv[1:]) or "Dame un consejo al azar"
    print(preguntar_al_agente(pregunta))

# /// script
# requires-python = ">=3.11"
# dependencies = ["groq", "requests"]
# ///
"""
Agente super basico: responde preguntas sobre Pokemon usando PokeAPI.

Como ejecutarlo:
    export GROQ_API_KEY=gsk_...      # gratis en https://console.groq.com/keys
    uv run pokemon.py "¿cuanto pesa pikachu?"
"""
import json
import os
import sys

import requests
from groq import Groq

MODELO = "llama-3.3-70b-versatile"


def obtener_pokemon(nombre: str) -> dict:
    """Busca datos de un Pokemon por nombre en PokeAPI."""
    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}", timeout=10)
    if resp.status_code != 200:
        return {"error": f"No encontre un Pokemon llamado '{nombre}'"}
    datos = resp.json()
    return {
        "nombre": datos["name"],
        "altura_decimetros": datos["height"],
        "peso_hectogramos": datos["weight"],
        "tipos": [t["type"]["name"] for t in datos["types"]],
    }


HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_pokemon",
            "description": "Busca altura, peso y tipos de un Pokemon por su nombre.",
            "parameters": {
                "type": "object",
                "properties": {"nombre": {"type": "string", "description": "Nombre del Pokemon, ej. 'pikachu'"}},
                "required": ["nombre"],
            },
        },
    },
]

FUNCIONES = {"obtener_pokemon": obtener_pokemon}


def preguntar_al_agente(pregunta: str) -> str:
    cliente = Groq(api_key=os.environ["GROQ_API_KEY"])
    mensajes = [
        {"role": "system", "content": "Eres un agente experto en Pokemon. Usa las herramientas cuando las necesites."},
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
    pregunta = " ".join(sys.argv[1:]) or "¿Cuanto pesa pikachu?"
    print(preguntar_al_agente(pregunta))

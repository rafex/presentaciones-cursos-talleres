# /// script
# requires-python = ">=3.11"
# dependencies = ["openai", "requests"]
# ///
"""
Agente orquestador: el mismo ciclo de siempre, pero con las tools de los
tres agentes anteriores (clima, pokemon, consejos) juntas en una sola
lista. El modelo decide, pregunta por pregunta, cual o cuales necesita —
nadie le dice "esto es una pregunta de clima" desde el codigo.

La GROQ_API_KEY se busca en este orden: variable de entorno ya exportada
> ./.env local > ../secrets/groq.enc.env cifrado con sops+age. No hace
falta acordarse de 'sops exec-env' a mano: si no encuentra la key suelta,
el propio script intenta descifrar el secreto.

Usa el cliente de OpenAI apuntando al endpoint de compatibilidad de Groq
(GROQ_BASE_URL) -- ver ../.env.example y ../scripts/configurar_env.sh.

Como ejecutarlo:
    uv run orquestador.py "¿que clima hay en Tlaxcala y cuanto pesa pikachu?"
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from openai import OpenAI


def _cargar_configuracion() -> None:
    """Carga variables en orden: ya exportadas > .env local > secrets/groq.enc.env cifrado."""
    raiz = Path(__file__).resolve().parent
    archivo_env = raiz / ".env"
    if archivo_env.exists():
        for linea in archivo_env.read_text().splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            os.environ.setdefault(clave.strip(), valor.strip())

    api_key = os.environ.get("GROQ_API_KEY", "")
    if api_key and not api_key.startswith("gsk_REEMPLAZA"):
        return

    archivo_cifrado = raiz.parent / "secrets" / "groq.enc.env"
    if not archivo_cifrado.exists():
        return
    try:
        resultado = subprocess.run(
            ["sops", "--decrypt", "--extract", '["GROQ_API_KEY"]', str(archivo_cifrado)],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        return  # sops no esta instalado -- se valida mas abajo con un mensaje claro
    if resultado.returncode == 0 and resultado.stdout.strip():
        os.environ["GROQ_API_KEY"] = resultado.stdout.strip()


_cargar_configuracion()

GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODELO = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")


# --- tools de clima (ver ../agente-clima/clima.py) ---

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


# --- tool de pokemon (ver ../agente-pokemon/pokemon.py) ---

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


# --- tools de consejos (ver ../agente-consejos/consejos.py) ---

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
                "properties": {"latitud": {"type": "number"}, "longitud": {"type": "number"}},
                "required": ["latitud", "longitud"],
            },
        },
    },
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

FUNCIONES = {
    "obtener_coordenadas": obtener_coordenadas,
    "obtener_clima": obtener_clima,
    "obtener_pokemon": obtener_pokemon,
    "obtener_consejo_aleatorio": obtener_consejo_aleatorio,
    "buscar_consejo": buscar_consejo,
}


def preguntar_al_agente(pregunta: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("gsk_REEMPLAZA"):
        raise SystemExit(
            "No encontre una GROQ_API_KEY valida. Exportala, ponla en .env, o "
            "configurala cifrada con ../scripts/configurar_secreto.sh"
        )
    cliente = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres un agente que puede responder sobre clima, Pokemon y dar consejos. "
                "Usa las herramientas que necesites, en el orden que necesites, para "
                "responder por completo la pregunta del usuario."
            ),
        },
        {"role": "user", "content": pregunta},
    ]

    for _ in range(8):  # tope de seguridad: con 5 tools, una pregunta combinada necesita mas vueltas
        respuesta = cliente.chat.completions.create(model=MODELO, messages=mensajes, tools=HERRAMIENTAS)
        mensaje = respuesta.choices[0].message
        mensajes.append(mensaje)

        if not mensaje.tool_calls:
            return mensaje.content

        for llamada in mensaje.tool_calls:
            funcion = FUNCIONES[llamada.function.name]
            # Groq a veces manda {"": {}} para tools sin parametros -- se descarta esa clave vacia.
            argumentos = {k: v for k, v in json.loads(llamada.function.arguments).items() if k}
            resultado = funcion(**argumentos)
            print(f"  -> el agente uso {llamada.function.name}({argumentos})")
            mensajes.append({
                "role": "tool",
                "tool_call_id": llamada.id,
                "content": json.dumps(resultado),
            })

    return "No pude resolverlo en el numero de intentos permitido."


if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or "¿Que clima hay en Tlaxcala y cuanto pesa pikachu?"
    print(preguntar_al_agente(pregunta))

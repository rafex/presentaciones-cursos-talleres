# /// script
# requires-python = ">=3.11"
# dependencies = ["openai", "requests"]
# ///
"""
Agente super basico: responde preguntas sobre el clima.

La GROQ_API_KEY se busca en este orden: variable de entorno ya exportada
> ./.env local > ../secrets/groq.enc.env cifrado con sops+age. No hace
falta acordarse de 'sops exec-env' a mano: si no encuentra la key suelta,
el propio script intenta descifrar el secreto.

Usa el cliente de OpenAI apuntando al endpoint de compatibilidad de Groq
(GROQ_BASE_URL) -- ver ../.env.example y ../scripts/configurar_env.sh.

Como ejecutarlo:
    uv run clima.py "¿que clima hay en Tlaxcala?"
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
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("gsk_REEMPLAZA"):
        raise SystemExit(
            "No encontre una GROQ_API_KEY valida. Exportala, ponla en .env, o "
            "configurala cifrada con ../scripts/configurar_secreto.sh"
        )
    cliente = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
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
    pregunta = " ".join(sys.argv[1:]) or "¿Que clima hay en Tlaxcala?"
    print(preguntar_al_agente(pregunta))

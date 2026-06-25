# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
El nivel mas bajo posible: hablarle a un LLM sin SDK, sin framework, sin
ciclo de agente. Solo un POST por HTTP al endpoint de chat completions de
Groq, armado a mano con la libreria estandar (urllib), y un print del
texto que regresa.

Comparalo con los demas scripts de esta carpeta:
- agente-sin-tool/sin_tool.py ya usa el SDK de `openai` (una linea menos
  que escribir el JSON y los headers a mano, pero sigue siendo una sola
  llamada, sin tools).
- agente-pokemon/pokemon.py, agente-clima/clima.py, agente-consejos/, y
  agente-orquestador/ usan ese mismo SDK MAS un ciclo for que vuelve a
  llamar al modelo cada vez que pide usar una herramienta -- eso es lo
  que hace que un LLM se comporte como "agente".
- agente-cp/ va un paso mas alla y usa LangGraph para declarar ese ciclo
  como un grafo, en vez de escribir el for a mano.

Este script no tiene nada de eso: ni tools, ni ciclo, ni SDK. Solo para
ver que, por debajo de cualquier framework, hablarle a un LLM siempre es
esto: un POST con una lista de mensajes, y una respuesta en JSON.

La GROQ_API_KEY se busca en este orden: variable de entorno ya exportada
> ./.env local > ../secrets/groq.enc.env cifrado con sops+age -- igual
que en los demas scripts de esta carpeta.

Como ejecutarlo:
    uv run llm_directo.py "¿que es un agente de IA?"
"""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path


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


def preguntar_sin_sdk(pregunta: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("gsk_REEMPLAZA"):
        raise SystemExit(
            "No encontre una GROQ_API_KEY valida. Exportala, ponla en .env, o "
            "configurala cifrada con ../scripts/configurar_secreto.sh"
        )

    cuerpo = json.dumps({
        "model": MODELO,
        "messages": [{"role": "user", "content": pregunta}],
    }).encode("utf-8")

    peticion = urllib.request.Request(
        url=f"{GROQ_BASE_URL}/chat/completions",
        data=cuerpo,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Sin esto Groq responde 403 -- algunos proveedores filtran el
            # User-Agent por default de urllib ("Python-urllib/x.y").
            "User-Agent": "llm-directo/1.0",
        },
    )

    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        datos = json.loads(respuesta.read())

    return datos["choices"][0]["message"]["content"]


if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or "¿Que es un agente de IA?"
    print(preguntar_sin_sdk(pregunta))

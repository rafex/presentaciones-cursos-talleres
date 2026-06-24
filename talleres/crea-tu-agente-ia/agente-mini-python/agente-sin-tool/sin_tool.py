# /// script
# requires-python = ">=3.11"
# dependencies = ["openai"]
# ///
"""
Agente SIN herramientas: el "antes" que justifica por que existen
clima.py, pokemon.py y consejos.py.

Mismo modelo, misma pregunta tipica de esos agentes, pero sin ninguna
tool conectada a una API real. El modelo solo tiene lo que aprendio en su
entrenamiento — no sabe el clima de ahora mismo, no tiene forma de
confirmar datos de Pokemon actualizados, y no tiene acceso a una base de
consejos real. Va a inventar una respuesta que SUENA segura pero no se
puede verificar (o, con suerte, va a admitir que no lo sabe).

La GROQ_API_KEY se busca en este orden: variable de entorno ya exportada
> ./.env local > ../secrets/groq.enc.env cifrado con sops+age. No hace
falta acordarse de 'sops exec-env' a mano: si no encuentra la key suelta,
el propio script intenta descifrar el secreto.

Usa el cliente de OpenAI apuntando al endpoint de compatibilidad de Groq
(GROQ_BASE_URL) -- ver ../.env.example y ../scripts/configurar_env.sh.

Como ejecutarlo:
    uv run sin_tool.py "¿que clima hay en Tlaxcala en este momento?"
"""
import os
import subprocess
import sys
from pathlib import Path

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


def preguntar_sin_herramientas(pregunta: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("gsk_REEMPLAZA"):
        raise SystemExit(
            "No encontre una GROQ_API_KEY valida. Exportala, ponla en .env, o "
            "configurala cifrada con ../scripts/configurar_secreto.sh"
        )
    cliente = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    respuesta = cliente.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Responde la pregunta del usuario lo mejor que puedas."},
            {"role": "user", "content": pregunta},
        ],
        # Sin "tools": el modelo no tiene ninguna forma de consultar datos reales.
    )
    return respuesta.choices[0].message.content


if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or "¿Que clima hay en Tlaxcala en este momento?"
    print(preguntar_sin_herramientas(pregunta))
    print()
    print("---")
    print("Compara esta respuesta con la de ../agente-clima/clima.py para la misma")
    print("pregunta. Sin una tool, el modelo no puede saber el clima real de ahora")
    print("mismo: solo puede inventar algo plausible o admitir que no lo sabe.")

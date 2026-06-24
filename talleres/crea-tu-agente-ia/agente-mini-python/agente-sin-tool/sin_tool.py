# /// script
# requires-python = ">=3.11"
# dependencies = ["groq"]
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

Como ejecutarlo:
    export GROQ_API_KEY=gsk_...      # gratis en https://console.groq.com/keys
    uv run sin_tool.py "¿que clima hay en Tlaxcala en este momento?"
"""
import os
import sys

from groq import Groq

MODELO = "llama-3.3-70b-versatile"


def preguntar_sin_herramientas(pregunta: str) -> str:
    cliente = Groq(api_key=os.environ["GROQ_API_KEY"])
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

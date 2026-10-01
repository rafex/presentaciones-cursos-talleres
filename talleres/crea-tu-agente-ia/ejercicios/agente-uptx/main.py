"""Runtime del agente informativo UPTx.

Este módulo coordina la conversación completa con Groq:

1. Envía la pregunta y los esquemas de las herramientas al modelo.
2. Ejecuta las funciones que el modelo solicita.
3. Devuelve los resultados al modelo para que redacte la respuesta final.

El loop es explícito porque algunos modelos compatibles con OpenAI no pueden
cerrar la conversación usando una tool sintética como ``final_answer``. Aquí
la respuesta final siempre llega como texto normal del modelo.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from openai import OpenAI, OpenAIError

from model import create_client, model_name
from tools import FUNCTIONS, TOOLS

# Límite de seguridad para evitar un ciclo infinito si el modelo sigue pidiendo
# herramientas y nunca produce una respuesta final.
MAX_STEPS = 6

# Estas instrucciones definen el alcance factual del agente y cuándo debe usar
# cada herramienta. La base local contiene la información institucional; el
# clima siempre se obtiene de la API de Open-Meteo.
INSTRUCTIONS = """
Eres un agente informativo de la Universidad Politécnica de Tlaxcala.
Usa consultar_uptx para carreras, admisión, cursos, ciclos escolares y reglamento.
Cuando consultar_uptx devuelva una línea "Fuente:" con una URL oficial,
usa consultar_fuente_uptx para visitar esa página y ampliar o verificar la
información. No inventes URLs: usa sólo las que aparezcan en el resultado.
Usa obtener_clima para preguntas meteorológicas.
No inventes datos institucionales. Cuando uses información UPTx, menciona que
proviene de la base local y conserva los enlaces oficiales que aparezcan en ella.
Aclara la fecha de consulta si la pregunta trata sobre convocatorias o calendarios.
""".strip()


def _assistant_message(message: Any) -> dict[str, Any]:
    """Convierte la respuesta del SDK en un mensaje para el siguiente turno.

    El SDK entrega objetos Python, pero la siguiente petición necesita el
    historial en el formato de diccionarios que espera la API de chat. Se
    conservan los ``tool_calls`` para que Groq pueda relacionar cada resultado
    con la llamada que originó la herramienta.
    """

    result: dict[str, Any] = {"role": "assistant", "content": message.content}
    if message.tool_calls:
        result["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in message.tool_calls
        ]
    return result


def _execute_tool(name: str, arguments: str) -> str:
    """Despacha una llamada del modelo a una función Python registrada.

    La API entrega el nombre de la función y sus argumentos como JSON. Este
    punto centraliza la validación básica y convierte los errores de una tool
    en texto que el modelo puede interpretar, en lugar de romper el proceso.
    """

    function = FUNCTIONS.get(name)
    if function is None:
        return f"La herramienta {name} no existe."

    try:
        parsed_arguments = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return f"Los argumentos de {name} no son JSON válido."

    try:
        return str(function(**parsed_arguments))
    except TypeError as error:
        return f"No pude ejecutar {name} con esos argumentos: {error}"


def ejecutar_agente(pregunta: str, client: OpenAI | None = None) -> str:
    """Responde una pregunta usando Groq y las herramientas disponibles.

    Args:
        pregunta: Texto que desea resolver la persona usuaria.
        client: Cliente compatible con OpenAI. Se puede inyectar en pruebas;
            si se omite, se crea el cliente real de Groq.

    Returns:
        La respuesta final del modelo como texto plano.

    Raises:
        RuntimeError: Si falta la API key, falla Groq o se alcanza el límite
            de pasos sin obtener una respuesta final.
    """

    client = client or create_client()
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": pregunta},
    ]

    for step in range(MAX_STEPS):
        try:
            # En el primer turno obligamos al modelo a elegir una tool. Esto
            # hace observable la capacidad de function calling del ejercicio.
            # En turnos posteriores permitimos que termine con texto normal.
            response = client.chat.completions.create(
                model=model_name(),
                messages=messages,
                tools=TOOLS,
                tool_choice="required" if step == 0 else "auto",
                temperature=0.2,
                max_tokens=1000,
            )
        except OpenAIError as error:
            raise RuntimeError(f"Groq no pudo generar la respuesta: {error}") from error

        message = response.choices[0].message
        if not message.tool_calls:
            return (message.content or "No pude generar una respuesta.").strip()

        # Un turno puede traer una o varias llamadas. Primero guardamos el
        # mensaje del asistente y después anexamos un resultado por llamada.
        messages.append(_assistant_message(message))
        for call in message.tool_calls:
            result = _execute_tool(call.function.name, call.function.arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )

    raise RuntimeError(f"El agente alcanzó el límite de {MAX_STEPS} pasos sin respuesta final.")


def main() -> None:
    """Expone el agente como comando de terminal."""

    parser = argparse.ArgumentParser(description="Agente informativo de la UPTx")
    parser.add_argument(
        "pregunta",
        nargs="?",
        default="¿Qué carreras ofrece la UPTx?",
        help="Pregunta que responderá el agente.",
    )
    args = parser.parse_args()
    try:
        print(ejecutar_agente(args.pregunta))
    except RuntimeError as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()

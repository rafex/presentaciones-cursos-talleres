"""Loop explícito de function calling compatible con Groq y OpenAI."""

from __future__ import annotations

import argparse
import json
from typing import Any

from openai import OpenAI, OpenAIError

from model import create_client, model_name
from tools import FUNCTIONS, TOOLS

MAX_STEPS = 6

INSTRUCTIONS = """
Eres un agente informativo de la Universidad Politécnica de Tlaxcala.
Usa consultar_uptx para carreras, admisión, cursos, ciclos escolares y reglamento.
Usa obtener_clima para preguntas meteorológicas.
No inventes datos institucionales. Cuando uses información UPTx, menciona que
proviene de la base local y conserva los enlaces oficiales que aparezcan en ella.
Aclara la fecha de consulta si la pregunta trata sobre convocatorias o calendarios.
""".strip()


def _assistant_message(message: Any) -> dict[str, Any]:
    """Convierte el mensaje del SDK a un dict reutilizable en la conversación."""

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
    """Valida argumentos y ejecuta una tool registrada."""

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
    """Responde una pregunta usando Groq y las tools disponibles."""

    client = client or create_client()
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": pregunta},
    ]

    for step in range(MAX_STEPS):
        try:
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

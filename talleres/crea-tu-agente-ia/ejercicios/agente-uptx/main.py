"""Punto de entrada del agente informativo de la UPTx."""

from __future__ import annotations

import argparse

from smolagents import ToolCallingAgent

from model import create_model
from tools import TOOLS

INSTRUCTIONS = """
Eres un agente informativo de la Universidad Politécnica de Tlaxcala.
Usa consultar_uptx para carreras, admisión, cursos, ciclos escolares y reglamento.
Usa obtener_clima para preguntas meteorológicas.
No inventes datos institucionales. Cuando uses información UPTx, menciona que
proviene de la base local y conserva los enlaces oficiales que aparezcan en ella.
Aclara la fecha de consulta si la pregunta trata sobre convocatorias o calendarios.
"""


def build_agent() -> ToolCallingAgent:
    """Construye un agente seguro que sólo puede llamar las tools declaradas."""

    return ToolCallingAgent(
        tools=TOOLS,
        model=create_model(),
        instructions=INSTRUCTIONS,
        max_steps=6,
        verbosity_level=1,
    )


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
        print(build_agent().run(args.pregunta))
    except RuntimeError as error:
        parser.exit(2, f"Error de configuración: {error}\n")


if __name__ == "__main__":
    main()

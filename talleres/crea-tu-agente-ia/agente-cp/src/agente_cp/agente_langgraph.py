"""Agente del taller: LangGraph + Groq, herramientas servidas por MCP.

El grafo es deliberadamente explicito (no se usa create_react_agent) para que
el ciclo Usuario -> Modelo -> Herramientas -> Modelo -> Respuesta, mostrado en
las slides, se vea linea por linea en codigo real.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode

SYSTEM_PROMPT = (
    "Eres un agente que verifica y repara direcciones postales mexicanas. "
    "Usa la tool buscar_cp para consultar el catalogo oficial de SEPOMEX, "
    "validar_direccion para confirmar si una colonia corresponde a un CP, "
    "y geocodificar_direccion cuando el CP no alcance para ubicar el lugar. "
    "Si una direccion esta mal, dilo explicitamente y sugiere la correccion. "
    "Si los datos vienen de un fixture local (sin red), acláralo en la respuesta."
)

MCP_SERVER_PARAMS = {
    "agente_cp": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "agente_cp.mcp_server"],
    }
}


def construir_modelo() -> ChatGroq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y pon tu API key de "
            "https://console.groq.com/keys"
        )
    modelo = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    return ChatGroq(model=modelo, temperature=0)


async def construir_grafo():
    client = MultiServerMCPClient(MCP_SERVER_PARAMS)
    tools = await client.get_tools()

    modelo = construir_modelo().bind_tools(tools)

    async def llamar_modelo(state: MessagesState) -> dict:
        mensajes = [SystemMessage(SYSTEM_PROMPT), *state["messages"]]
        respuesta = await modelo.ainvoke(mensajes)
        return {"messages": [respuesta]}

    def hay_tool_calls(state: MessagesState) -> str:
        ultimo = state["messages"][-1]
        if isinstance(ultimo, AIMessage) and ultimo.tool_calls:
            return "ejecutar_tools"
        return END

    grafo = StateGraph(MessagesState)
    grafo.add_node("llamar_modelo", llamar_modelo)
    grafo.add_node("ejecutar_tools", ToolNode(tools))
    grafo.set_entry_point("llamar_modelo")
    grafo.add_conditional_edges("llamar_modelo", hay_tool_calls, {"ejecutar_tools": "ejecutar_tools", END: END})
    grafo.add_edge("ejecutar_tools", "llamar_modelo")

    return grafo.compile()


async def preguntar(texto: str) -> str:
    grafo = await construir_grafo()
    resultado = await grafo.ainvoke({"messages": [("user", texto)]})
    return resultado["messages"][-1].content


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    pregunta = " ".join(sys.argv[1:]) or (
        "¿La colonia Tlaxcala Centro corresponde al CP 90001 en Tlaxcala?"
    )
    respuesta = asyncio.run(preguntar(pregunta))
    print(respuesta)


if __name__ == "__main__":
    main()

# `agente_langgraph.py` — el grafo, línea por línea

Archivo: [`src/agente_cp/agente_langgraph.py`](../src/agente_cp/agente_langgraph.py)

Este es el único módulo que sabe de LangGraph y de Groq. Construye
explícitamente el ciclo "modelo decide → ejecuta herramienta → vuelve al
modelo" que se muestra en la slide "Ciclo básico" — sin usar el agente
ReAct prearmado de LangGraph (`create_react_agent`), para que el ciclo sea
visible en código en vez de estar escondido en una librería.

## Conectarse al servidor MCP como subproceso

```python
MCP_SERVER_PARAMS = {
    "agente_cp": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "agente_cp.mcp_server"],
    }
}
```

`sys.executable` es la ruta al intérprete Python actual (el del `.venv`
que `uv` administra) — usarlo en vez de un `"python"` genérico garantiza
que el subproceso del servidor MCP corre con las mismas dependencias
instaladas, sin depender de qué `python` esté primero en el `PATH` del
sistema.

```python
client = MultiServerMCPClient(MCP_SERVER_PARAMS)
tools = await client.get_tools()
```

`MultiServerMCPClient` (de `langchain-mcp-adapters`) arranca
`mcp_server.py` como subproceso, le habla el protocolo MCP por
stdin/stdout, descubre sus 4 tools (`buscar_cp`, `validar_direccion`,
`descargar_estado`, `geocodificar_direccion`) y las envuelve como objetos
`BaseTool` de LangChain — listas para pasarle a cualquier modelo de chat
que soporte tool calling.

## El estado del grafo

```python
from langgraph.graph.message import MessagesState
```

`MessagesState` es un estado predefinido de LangGraph: un diccionario con
una sola clave, `"messages"`, que es una lista de mensajes
(`HumanMessage`, `AIMessage`, `ToolMessage`...). Cada nodo del grafo recibe
este estado completo y devuelve un *delta* (`{"messages": [...]}`) que
LangGraph fusiona automáticamente con el historial existente — por eso
ningún nodo necesita reconstruir la lista completa de mensajes, solo
añadir lo nuevo.

## Los dos nodos

### `llamar_modelo` — el modelo decide

```python
async def llamar_modelo(state: MessagesState) -> dict:
    mensajes = [SystemMessage(SYSTEM_PROMPT), *state["messages"]]
    respuesta = await modelo.ainvoke(mensajes)
    return {"messages": [respuesta]}
```

Antepone el `SYSTEM_PROMPT` (que le dice al modelo qué tools tiene y
cuándo usarlas) al historial actual, y le pregunta al modelo. La respuesta
de Groq puede ser:

- Una respuesta final en texto (si el modelo ya tiene todo lo que
  necesita), o
- Un `AIMessage` con `tool_calls` poblado (si el modelo decide que
  necesita ejecutar una tool antes de responder).

El modelo fue construido con `.bind_tools(tools)` (en `construir_grafo`),
que es lo que le permite a Groq generar `tool_calls` válidos en primer
lugar — sin esto, el modelo no sabría que las tools existen.

### `ejecutar_tools` — la herramienta actúa

```python
grafo.add_node("ejecutar_tools", ToolNode(tools))
```

`ToolNode` es un nodo prearmado de LangGraph: mira el último mensaje del
estado, encuentra los `tool_calls` que el modelo pidió, ejecuta cada tool
correspondiente (en este caso, vía el cliente MCP) y devuelve los
resultados como `ToolMessage`s — uno por cada llamada. A diferencia de
`create_react_agent` (que también encadena los nodos automáticamente),
usar `ToolNode` suelto deja visible *dónde* y *cuándo* se conecta al resto
del grafo.

## La arista condicional: cuándo seguir y cuándo parar

```python
def hay_tool_calls(state: MessagesState) -> str:
    ultimo = state["messages"][-1]
    if isinstance(ultimo, AIMessage) and ultimo.tool_calls:
        return "ejecutar_tools"
    return END

grafo.add_conditional_edges(
    "llamar_modelo", hay_tool_calls,
    {"ejecutar_tools": "ejecutar_tools", END: END},
)
grafo.add_edge("ejecutar_tools", "llamar_modelo")
```

Esto es el ciclo completo en tres líneas:

1. Después de `llamar_modelo`, `hay_tool_calls` decide a dónde ir.
2. Si el último mensaje tiene `tool_calls` → al nodo `ejecutar_tools`.
3. Si no → `END`, el grafo termina y ese mensaje es la respuesta final.
4. `ejecutar_tools` siempre vuelve a `llamar_modelo` (arista fija, no
   condicional) — porque después de ejecutar una tool, el modelo necesita
   ver el resultado y decidir su siguiente paso (otra tool, o la
   respuesta final).

No hay límite explícito de iteraciones en este grafo de taller — en
producción (ver `AGENT_MAX_STEPS` en
[ether-brain](https://github.com/rafex/ether-brain)) conviene acotar
cuántas veces puede dar la vuelta el ciclo antes de forzar una respuesta.

## `construir_modelo`: fail-fast si falta la API key

```python
def construir_modelo() -> ChatGroq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY. Copia .env.example a .env y pon tu API key de "
            "https://console.groq.com/keys"
        )
    modelo = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    return ChatGroq(model=modelo, temperature=0)
```

`ChatGroq` en realidad lee `GROQ_API_KEY` del entorno por su cuenta — esta
validación explícita existe solo para dar un mensaje de error claro y
accionable *antes* de que LangChain falle con un error genérico de
autenticación HTTP. `temperature=0` favorece respuestas deterministas,
útil para un taller donde se quiere poder reproducir un resultado en vivo.

## `main`: el punto de entrada de la CLI

```python
def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    pregunta = " ".join(sys.argv[1:]) or (
        "¿La colonia Tlaxcala Centro corresponde al CP 90001 en Tlaxcala?"
    )
    respuesta = asyncio.run(preguntar(pregunta))
    print(respuesta)
```

Carga `.env` explícitamente desde la raíz del proyecto (no depende de que
el directorio de trabajo actual sea el correcto), toma la pregunta de los
argumentos de línea de comandos o usa una de ejemplo si no se pasó
ninguna, y corre todo el flujo asíncrono con `asyncio.run`. Este es el
`main` que `cli.py` reexporta como el comando `agente-cp`.

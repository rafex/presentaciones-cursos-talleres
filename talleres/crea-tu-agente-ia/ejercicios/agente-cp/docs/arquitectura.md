# Arquitectura

## Mapa del proyecto

```
agente-cp/
├── data/
│   └── sepomex.sqlite        # catalogo nacional, 158,539 filas, 20 MB
├── scripts/
│   └── xml_a_sqlite.py       # genera sepomex.sqlite desde el XML oficial
├── src/agente_cp/
│   ├── sepomex.py            # acceso a datos: sqlite -> scraping -> fixture
│   ├── mcp_server.py         # expone funciones de sepomex.py como tools MCP
│   ├── agente_langgraph.py   # grafo LangGraph que consume esas tools via Groq
│   ├── cli.py                # `uv run agente-cp "..."`
│   └── fixtures/
│       └── 29_tlaxcala.txt   # catalogo reducido, ultimo respaldo
├── tools.json.example         # como conectar el mismo MCP server a ether-brain
└── .env.example                # GROQ_API_KEY
```

Cuatro capas, cada una sin saber casi nada de la siguiente:

```
sepomex.py  ──tools──>  mcp_server.py  ──stdio/MCP──>  agente_langgraph.py
   (datos)                  (protocolo)                    (decisión)
```

- `sepomex.py` no sabe que existe MCP, LangGraph ni Groq. Solo sabe resolver
  "dame las colonias del CP X en el estado Y" y devolver de dónde salieron
  los datos.
- `mcp_server.py` no sabe nada de LangGraph ni de Groq. Solo envuelve
  funciones de `sepomex.py` (más una de bonus) como tools MCP estándar,
  con un `input_schema` que el protocolo genera automáticamente desde los
  type hints de Python.
- `agente_langgraph.py` no sabe nada de SEPOMEX, scraping ni SQLite. Solo
  sabe hablar MCP para descubrir tools, y hablar con Groq para decidir
  cuándo usarlas.

Esta separación es la lección de fondo del taller: **las tools son el
contrato**, no el código de quien las construyó. Por eso el mismo
`mcp_server.py` puede conectarse después a [ether-brain](./ether-brain.md)
(un runtime en Java) sin tocar una línea de él.

## El ciclo completo de una pregunta

```
Usuario: "¿La colonia Tlaxcala Cento corresponde al CP 90001?"
   │
   ▼
agente_langgraph.preguntar(texto)
   │
   ▼
construir_grafo()
   ├─ MultiServerMCPClient arranca mcp_server.py como subproceso (stdio)
   ├─ client.get_tools() descubre buscar_cp, validar_direccion,
   │  descargar_estado, geocodificar_direccion
   └─ ChatGroq(...).bind_tools(tools)
   │
   ▼
grafo.ainvoke({"messages": [("user", texto)]})
   │
   ├─ nodo "llamar_modelo"
   │     SystemMessage + historial -> Groq
   │     Groq responde con un tool_call: validar_direccion(cp=90001, colonia="Tlaxcala Cento", estado=29)
   │
   ├─ hay_tool_calls() devuelve "ejecutar_tools" (condición de la arista)
   │
   ├─ nodo "ejecutar_tools" (ToolNode)
   │     invoca el tool MCP real -> mcp_server.validar_direccion(...)
   │       -> sepomex.validar_direccion(...)
   │         -> buscar_por_cp(...) -> sqlite local -> sin coincidencia exacta
   │           -> difflib sugiere "Tlaxcala Centro"
   │     resultado vuelve como ToolMessage en el historial
   │
   ├─ vuelve a "llamar_modelo" con el resultado de la tool en el contexto
   │     Groq ya tiene el dato real, redacta la respuesta final
   │
   └─ hay_tool_calls() devuelve END (no hay mas tool_calls)
   │
   ▼
"La colonia correcta es 'Tlaxcala Centro', no 'Tlaxcala Cento'..."
```

Esto es exactamente el diagrama "Ciclo básico" de las slides, pero con
nombres de función reales en cada flecha.

## Por qué un grafo explícito y no `create_react_agent`

LangGraph trae un agente ReAct prearmado (`langgraph.prebuilt.create_react_agent`)
que haría todo esto en una línea. Lo evitamos a propósito: el objetivo del
taller es que cada asistente *vea* el ciclo modelo → herramienta → modelo,
no que lo importe de una librería. `agente_langgraph.py` construye el mismo
patrón a mano con `StateGraph`, `add_conditional_edges` y `ToolNode` —
ver [agente_langgraph.md](./agente_langgraph.md) para el detalle.

## Por qué tres fuentes de datos en cascada

Un taller en vivo no controla el wifi del salón ni la disponibilidad del
sitio de Correos de México. La cascada SQLite → scraping → fixture
(documentada en [sepomex.md](./sepomex.md)) es el mismo patrón que se usa
en producción para depender de una API externa frágil: una fuente rápida y
confiable primero, degradando con gracia si falla, y siempre informando
de dónde vino el dato (`origen_datos`) en vez de fingir que todo es igual.

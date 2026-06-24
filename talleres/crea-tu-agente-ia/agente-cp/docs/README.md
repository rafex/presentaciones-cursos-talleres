# Documentación de `agente-cp`

Explicación detallada del código fuente del proyecto del taller. El
[README](../README.md) del proyecto cubre instalación y uso; estos
documentos explican **cómo** y **por qué** está construido cada módulo.

| Documento | Contenido |
|---|---|
| [arquitectura.md](./arquitectura.md) | Mapa general del proyecto y cómo fluye una pregunta del usuario hasta la respuesta |
| [sepomex.md](./sepomex.md) | La cascada de datos: SQLite → scraping en vivo → fixture, y por qué cada pieza existe |
| [xml_a_sqlite.md](./xml_a_sqlite.md) | El script de conversión del catálogo nacional, fila por fila |
| [mcp_server.md](./mcp_server.md) | Las 4 tools MCP expuestas y cómo el modelo decide usarlas |
| [agente_langgraph.md](./agente_langgraph.md) | El grafo LangGraph línea por línea: estado, nodos, condición de salida |
| [ether-brain.md](./ether-brain.md) | Cómo el mismo servidor MCP se conecta a un runtime distinto (Java) sin escribir Java |

## Orden de lectura sugerido

Si vienes del taller y quieres entender el código de arriba hacia abajo,
sigue este orden:

1. [arquitectura.md](./arquitectura.md) — la vista de pájaro.
2. [sepomex.md](./sepomex.md) — de dónde salen los datos.
3. [mcp_server.md](./mcp_server.md) — cómo se exponen como herramientas.
4. [agente_langgraph.md](./agente_langgraph.md) — cómo el modelo las usa.
5. [xml_a_sqlite.md](./xml_a_sqlite.md) y [ether-brain.md](./ether-brain.md) — opcionales, para ir más allá.

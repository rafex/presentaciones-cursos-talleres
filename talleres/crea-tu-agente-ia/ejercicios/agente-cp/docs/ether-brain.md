# Reusar las tools en ether-brain

[ether-brain](https://github.com/rafex/ether-brain) es un runtime de
agentes en Java 21 (arquitectura hexagonal, sin frameworks pesados en el
dominio) con su propio loop modelo → tools → modelo, codecs para varios
proveedores LLM (OpenAI-compatible, Anthropic, Gemini, Bedrock) y tres
formas de cargar tools externas sin escribir Java: subprocess, HTTP proxy
y **MCP**.

Esta es la pieza clave del taller: `mcp_server.py` no tiene ninguna
dependencia de LangChain, LangGraph ni de este agente Python en
particular — es un servidor MCP estándar. Cualquier runtime que hable el
protocolo MCP lo puede usar, incluyendo uno escrito en otro lenguaje.

## Cómo se conecta

ether-brain descubre tools externas leyendo un `tools.json` al arrancar.
[`tools.json.example`](../tools.json.example) en este proyecto declara
nuestro servidor como una tool de tipo `mcp`:

```json
[
  {
    "type": "mcp",
    "server_name": "agente-cp",
    "command": [
      "uv", "run", "--directory", "/ruta/absoluta/a/agente-cp",
      "python", "-m", "agente_cp.mcp_server"
    ]
  }
]
```

Al arrancar, ether-brain ejecuta ese `command` como subproceso (igual que
hace `MultiServerMCPClient` en `agente_langgraph.py`), le habla MCP por
stdio, y descubre automáticamente las 4 tools (`buscar_cp`,
`validar_direccion`, `descargar_estado`, `geocodificar_direccion`) — sin
que nadie tenga que describirlas a mano en Java.

## Pasos para probarlo

```bash
cd /ruta/a/ether-brain/ether-brain
cp /ruta/a/agente-cp/tools.json.example tools.json
# edita tools.json: pon la ruta absoluta real a agente-cp

export LLM_TYPE=openai
export LLM_URL=https://api.groq.com
export LLM_TOKEN=<tu GROQ_API_KEY>
export LLM_MODEL=llama-3.3-70b-versatile

java -jar ether-brain-cli.jar "¿La colonia Tlaxcala Cento corresponde al CP 90001?"
```

`LLM_TYPE=openai` no significa que estés usando OpenAI — es el nombre que
ether-brain le da al *formato* de API que usa Groq (y Cerebras, Deepseek,
Mistral, OpenRouter, Together AI...): el 80%+ del mercado de proveedores
LLM expone una API compatible con el formato de `/v1/chat/completions` de
OpenAI, así que ether-brain tiene un solo codec (`OpenAiCodec`) para todos
ellos. `LLM_URL` es la URL base sin path — el codec añade
`/v1/chat/completions` automáticamente.

## La lección de fondo

El mismo conjunto de tools — la misma lógica de scraping, la misma cascada
SQLite/red/fixture, la misma corrección de direcciones — sirve para dos
runtimes completamente distintos (un grafo LangGraph en Python, un loop de
agente en Java) sin duplicar una sola línea de lógica de negocio. MCP es
el contrato que lo hace posible: mientras el servidor hable el protocolo,
no importa qué tan diferente sea el código de quien lo construyó ni el de
quien lo consume.

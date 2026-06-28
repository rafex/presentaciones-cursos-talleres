# Documentación de `agente-clima-etherbrain`

El [README](../README.md) del proyecto cubre instalación y uso. Estos
documentos explican el **cómo** y el **por qué** de cada pieza.

| Documento | Contenido |
|---|---|
| [tools.md](./tools.md) | Cómo `tools.json` y el tipo `"http"` de ether-brain convierten una API pública en una tool, sin escribir Java |
| [secretos.md](./secretos.md) | age + sops a fondo: por qué este patrón, qué cifra y qué no, cómo se usa en CI/CD |
| [ether-brain-build.md](./ether-brain-build.md) | Por qué se compila desde el código fuente, qué módulo produce el jar, y un bug real de documentación que encontramos al probarlo |

## Este proyecto vs. `agente-cp`

| | `agente-clima-etherbrain` | [`agente-cp`](../../agente-cp) |
|---|---|---|
| Runtime | ether-brain (Java) | LangGraph (Python) |
| Cómo se definen las tools | `tools.json` declarativo, **sin código** | Servidor MCP en Python |
| Fuente de datos | Open-Meteo (API pública en vivo) | SQLite local + scraping + fixture |
| LLM | Groq | Groq |
| Manejo de secretos | age + sops | `.env` (variable de entorno simple) |

Dos caminos distintos hacia la misma idea: un agente con objetivo,
herramientas y ciclo de decisión. Este proyecto es deliberadamente el más
simple de los dos — útil como primer contacto antes de entrar a MCP.

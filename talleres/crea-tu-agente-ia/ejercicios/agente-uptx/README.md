# Agente informativo UPTx

Ejercicio final del taller `Construye tu Agente IA en 120 minutos`. El agente
usa el loop OpenAI-compatible de Groq para decidir cuándo consultar una tool de
clima o una base local de conocimiento sobre la Universidad Politécnica de
Tlaxcala.

El ciclo es explícito: Groq recibe la pregunta y los schemas, solicita una
tool, el programa ejecuta la función, devuelve el resultado a Groq y el modelo
redacta la respuesta final. Esto evita depender de una herramienta sintética
`final_answer` que no funciona con todos los modelos compatibles.

## Cómo está organizado el código

Cada archivo tiene una responsabilidad pequeña para que el flujo sea fácil de
leer, probar y extender:

```text
main.py       Entrada CLI y loop de function calling.
model.py      Cliente de Groq y configuración desde .env.
tools.py      Clima, búsqueda local y extracción de fuentes oficiales.
retriever.py  Búsqueda local por intención dentro de knowledge/uptx.md.
knowledge/    Snapshot institucional revisado y sus fuentes oficiales.
tests/        Pruebas del retriever y del loop sin consumir la API.
```

El recorrido de una pregunta es:

```text
pregunta
  -> Groq elige una tool
  -> main.py despacha a FUNCTIONS
  -> tools.py consulta Open-Meteo, retriever.py o una fuente oficial
  -> el resultado vuelve a Groq
  -> Groq redacta la respuesta final
```

### Consulta de una fuente oficial

`consultar_uptx` localiza fragmentos en `knowledge/uptx.md`. Si un fragmento
incluye una línea `Fuente: https://uptlax.edu.mx/...`, el modelo puede llamar a
`consultar_fuente_uptx` con esa URL. La segunda tool descarga la página, elimina
elementos que no son contenido y devuelve los párrafos relevantes para la
pregunta original.

La tool sólo permite HTTPS en `uptlax.edu.mx` y sus subdominios. No consulta el
API externo del RAG ni acepta URLs arbitrarias. Si el enlace apunta a un PDF o
la página no responde, devuelve un aviso para que el agente conserve la fuente
sin inventar el contenido.

Para modificar el agente, empieza por `INSTRUCTIONS` en `main.py`. Para añadir
una herramienta, implementa la función en `tools.py`, agrega su schema a
`TOOLS` y registra el mismo nombre en `FUNCTIONS`. Para mejorar las preguntas
institucionales, actualiza `knowledge/uptx.md` o las expansiones de intención
en `retriever.py`.

## Requisitos

- Python 3.11 o posterior.
- [`uv`](https://docs.astral.sh/uv/).
- Una API key de Groq.

## Configuración

```bash
cp .env.example .env
```

Edita `.env` y agrega sólo tu clave:

```dotenv
GROQ_API_KEY=gsk_...
```

El archivo `.env` está protegido por `.gitignore`.

## Ejecutar

```bash
uv sync
uv run python main.py "¿Qué carreras ofrece la UPTx?"
uv run python main.py "¿Cuántas horas de servicio social pide el reglamento?"
uv run python main.py "¿Qué clima hay en Tepeyanco?"
```

Desde la raíz del repositorio también puedes usar:

```bash
uv run --project talleres/crea-tu-agente-ia/ejercicios/agente-uptx \
  python talleres/crea-tu-agente-ia/ejercicios/agente-uptx/main.py \
  "¿Qué carreras ofrece la UPTx?"
```

## Probar sin consumir Groq

```bash
uv run pytest
```

Las pruebas cubren la recuperación de carreras, reglamento y ciclos, además
del ciclo `tool_choice="required"` seguido de `tool_choice="auto"`.

## Actualizar información del sitio

El archivo [`knowledge/uptx.md`](./knowledge/uptx.md) es el snapshot revisado
que usa el agente. Para obtener un snapshot técnico de las páginas públicas:

```bash
uv run python scripts/refresh_uptx_knowledge.py
```

Revisa los cambios antes de reemplazar la base revisada. Las convocatorias y
los calendarios requieren confirmar siempre la fecha y la fuente oficial.

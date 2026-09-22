# Agente informativo UPTx

Ejercicio final del taller `Construye tu Agente IA en 120 minutos`. El agente
usa el loop OpenAI-compatible de Groq para decidir cuándo consultar una tool de
clima o una base local de conocimiento sobre la Universidad Politécnica de
Tlaxcala.

El ciclo es explícito: Groq recibe la pregunta y los schemas, solicita una
tool, el programa ejecuta la función, devuelve el resultado a Groq y el modelo
redacta la respuesta final. Esto evita depender de una herramienta sintética
`final_answer` que no funciona con todos los modelos compatibles.

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

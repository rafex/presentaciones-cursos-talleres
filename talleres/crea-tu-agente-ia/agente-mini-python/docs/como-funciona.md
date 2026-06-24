# Cómo funciona el ciclo del agente

Los tres agentes con tool (`agente-clima/clima.py`, `agente-pokemon/pokemon.py`,
`agente-consejos/consejos.py`) repiten exactamente la misma estructura. Si
entiendes uno, entiendes los tres. Esta página explica esa estructura
usando `agente-clima/clima.py` como ejemplo, y al final compara contra
`agente-sin-tool/` y `agente-orquestador/`.

## Las cuatro piezas

### 1. Las funciones de Python normales

```python
def obtener_coordenadas(ciudad: str) -> dict:
    resp = requests.get("https://geocoding-api.open-meteo.com/v1/search", ...)
    ...

def obtener_clima(latitud: float, longitud: float) -> dict:
    resp = requests.get("https://api.open-meteo.com/v1/forecast", ...)
    ...
```

No tienen nada de "IA". Son funciones de Python normales que llaman a una
API pública con `requests` y devuelven un `dict`. Podrías probarlas solas,
sin agente ni LLM de por medio:

```bash
uv run --with requests python3 -c "
from clima import obtener_coordenadas
print(obtener_coordenadas('Tlaxcala'))
"
```

### 2. La descripción de esas funciones para el modelo

```python
HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_coordenadas",
            "description": "Convierte el nombre de una ciudad en latitud/longitud.",
            "parameters": {
                "type": "object",
                "properties": {"ciudad": {"type": "string", ...}},
                "required": ["ciudad"],
            },
        },
    },
    ...
]
```

El modelo de Groq (o cualquier LLM con "function calling") no ejecuta
código directamente. Lo único que puede hacer es **leer esta descripción**
y decidir, en su respuesta, algo como: "quiero que llames a
`obtener_coordenadas` con `ciudad='Tlaxcala'`". El nombre, la descripción
y los parámetros son las únicas pistas que tiene — por eso una buena
`description` importa tanto como el código de la función misma.

### 3. El diccionario que conecta nombre → función real

```python
FUNCIONES = {"obtener_coordenadas": obtener_coordenadas, "obtener_clima": obtener_clima}
```

Cuando el modelo responde "quiero `obtener_coordenadas`", este diccionario
es lo que permite pasar de ese string a la función de Python que
realmente se ejecuta.

### 4. El ciclo (el corazón del agente)

```python
mensajes = [
    {"role": "system", "content": "Eres un agente que responde sobre el clima..."},
    {"role": "user", "content": pregunta},
]

for _ in range(5):
    respuesta = cliente.chat.completions.create(model=MODELO, messages=mensajes, tools=HERRAMIENTAS)
    mensaje = respuesta.choices[0].message
    mensajes.append(mensaje)

    if not mensaje.tool_calls:
        return mensaje.content          # el modelo ya tiene la respuesta final

    for llamada in mensaje.tool_calls:
        funcion = FUNCIONES[llamada.function.name]
        argumentos = json.loads(llamada.function.arguments)
        resultado = funcion(**argumentos)
        mensajes.append({"role": "tool", "tool_call_id": llamada.id, "content": json.dumps(resultado)})
```

Paso a paso, para la pregunta `"¿qué clima hay en Tlaxcala?"`:

1. Se le manda al modelo la pregunta + la lista de herramientas
   disponibles.
2. El modelo responde: "necesito `obtener_coordenadas(ciudad='Tlaxcala')`"
   — no da una respuesta final todavía (`tool_calls` no está vacío).
3. El código ejecuta esa función de verdad, contra la API real, y le
   manda el resultado al modelo como un mensaje nuevo (`role: "tool"`).
4. El modelo, ya con las coordenadas en su contexto, vuelve a responder:
   ahora pide `obtener_clima(latitud=..., longitud=...)`.
5. El código ejecuta esa segunda función, le manda el resultado.
6. El modelo ya tiene todo lo que necesita — responde con texto normal
   (`tool_calls` vacío) y el ciclo termina.

**El `for _ in range(5)` es un tope de seguridad**: sin él, un modelo que
se queda pidiendo herramientas en bucle (por un error de la API, una
descripción ambigua, etc.) correría para siempre. Cinco vueltas son de
sobra para los ejemplos de este taller.

## Por qué esto es "un agente" y no "un chatbot"

Un chatbot responde con texto a partir de texto. Este programa **decide
por sí mismo** cuántas veces y en qué orden necesita consultar datos
externos reales antes de responder — ese ciclo de "pensar → actuar →
observar → repetir" es la definición práctica de agente que usa este
taller completo (ver la diapositiva "Ciclo básico" en
`crea-tu-agente-ia.md`).

## Qué cambia entre los tres agentes con tool

Nada del ciclo. Solo cambian:

* Qué funciones existen (`HERRAMIENTAS` y `FUNCIONES`).
* A qué API pública le pegan esas funciones.
* El mensaje de `system` que le da contexto al modelo.

Eso es justo lo que hace fácil pasar de "entendí `clima.py`" a "puedo
escribir mi propio script con otra API pública" — que es el reto natural
después de este ejercicio.

## `agente-sin-tool`: el control del experimento

`agente-sin-tool/sin_tool.py` llama al mismo modelo, con la misma
pregunta tipo ("¿qué clima hay en Tlaxcala en este momento?"), pero **sin
el parámetro `tools`** en la llamada:

```python
respuesta = cliente.chat.completions.create(
    model=MODELO,
    messages=[...],
    # Sin "tools": el modelo no tiene ninguna forma de consultar datos reales.
)
```

Sin `tools`, el modelo nunca puede pedir `tool_calls` — directamente no
existe esa opción para él. Va a responder con texto, en el mismo tono
seguro de siempre, pero construido solo a partir de lo que aprendió en su
entrenamiento (que tiene una fecha de corte, y de todos modos nunca tuvo
"el clima de Tlaxcala en este instante" en ningún libro). El resultado
casi siempre es una de dos cosas: una respuesta inventada que suena
correcta, o el modelo admitiendo que no tiene esa información.

Esta comparación, lado a lado con `agente-clima/clima.py`, es la
demostración más directa de para qué sirve una tool: no es que el modelo
"sea más inteligente" con una tool conectada, es que tiene acceso a datos
que de otra forma no existen en su conocimiento.

## `agente-orquestador`: una sola lista, varias tools

`agente-orquestador/orquestador.py` no tiene nada de nuevo en el ciclo —
es exactamente el mismo `for` de arriba. Lo único que cambia es que
`HERRAMIENTAS` y `FUNCIONES` ahora incluyen las cinco funciones de los
tres agentes anteriores (`obtener_coordenadas`, `obtener_clima`,
`obtener_pokemon`, `obtener_consejo_aleatorio`, `buscar_consejo`) en la
misma lista.

Nadie en el código le dice al modelo "esta pregunta es de clima" o "esta
es de Pokemon" — el modelo lee las cinco descripciones disponibles y
decide, según la pregunta, cuál o cuáles necesita. Para una pregunta como
`"¿qué clima hay en Tlaxcala y cuánto pesa pikachu?"`, el modelo va a
pedir `obtener_coordenadas` → `obtener_clima` → `obtener_pokemon` en una
sola conversación, sin que el código tenga ninguna lógica de "if
pregunta tiene la palabra clima". Esa decisión — qué herramienta usar, en
qué orden, cuántas veces — es exactamente lo que vuelve "orquestador" a
este agente: el mismo ciclo simple, con más opciones para elegir.

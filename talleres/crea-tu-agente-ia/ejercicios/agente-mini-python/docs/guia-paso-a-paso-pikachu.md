# Guía paso a paso: del POST crudo al agente de Pikachu

Esta guía es para explicar en clase, línea por línea, cómo se construyen
dos de los scripts de `agente-mini-python/`:

1. [`llm-directo/llm_directo.py`](../llm-directo/llm_directo.py) — hablarle
   a un LLM sin SDK y sin framework, solo HTTP.
2. [`agente-pokemon/pokemon.py`](../agente-pokemon/pokemon.py) — el mismo
   LLM, ahora con una herramienta conectada a PokeAPI, capaz de responder
   con datos reales (ej. cuánto pesa Pikachu).

La idea pedagógica: cada parte nueva de código resuelve un problema
concreto del paso anterior. Si en algún punto un alumno pregunta "¿y esto
para qué sirve?", la respuesta está en la sección de ese paso.

Para la comparación contra `agente-sin-tool/sin_tool.py` (el control del
experimento) ver [`como-funciona.md`](./como-funciona.md) — esta guía se
enfoca en construir el código desde cero, no en comparar resultados.

## Qué vamos a construir, en orden

| Paso | Script | Qué resuelve | Qué le falta todavía |
|---|---|---|---|
| 1 | `llm_directo.py` | Hablarle a un LLM, sin nada de por medio | No tiene forma de consultar datos reales — solo lo que el modelo ya sabe |
| 2 | `pokemon.py` | Darle al modelo una herramienta para consultar PokeAPI | — (este es el agente completo) |

## Antes de empezar

* Necesitas una `GROQ_API_KEY` (gratis en https://console.groq.com/keys).
  Ver [`../README.md`](../README.md#variable-secreta-groq_api_key) para
  las formas de configurarla.
* No necesitas instalar nada a mano — cada script declara sus propias
  dependencias en su encabezado y `uv` las instala solo.

---

## Parte 1: `llm-directo` — hablarle a un LLM sin nada de por medio

Antes de usar ningún SDK, vale la pena ver qué es, en el fondo, "hablarle
a un LLM": un servidor HTTP que recibe un POST con una lista de mensajes
en JSON, y contesta con otro JSON. Nada más. Vamos a escribir eso a mano,
usando solo la librería estándar de Python (sin instalar nada).

### Paso 1.1 — El encabezado PEP 723

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

**Qué hace:** le dice a `uv run` qué versión de Python necesita este
script y qué paquetes debe instalar antes de correrlo.

**Por qué `dependencies = []` (vacío):** porque este script no usa nada
fuera de la librería estándar de Python — ni `openai`, ni `requests`. Esa
es justo la lección de esta parte: no necesitas ningún paquete externo
para hablarle a un LLM, porque "hablarle a un LLM" es solo HTTP.

### Paso 1.2 — Los imports

```python
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
```

**Qué hace cada uno:**
- `json` — convertir el diccionario de Python a texto JSON (para mandarlo)
  y el texto JSON de la respuesta de vuelta a diccionario (para leerla).
- `os` — leer y escribir variables de entorno (`os.environ`).
- `subprocess` — poder llamar al comando `sops` desde Python, para
  descifrar la API key si está cifrada.
- `sys` — leer los argumentos de la línea de comandos (`sys.argv`).
- `urllib.request` — la pieza clave: hacer la petición HTTP, sin instalar
  ningún paquete externo (viene incluida en Python).
- `Path` — construir rutas de archivos de forma segura entre sistemas
  operativos, en vez de concatenar strings con `/`.

### Paso 1.3 — Cargar la configuración (`_cargar_configuracion`)

```python
def _cargar_configuracion() -> None:
    raiz = Path(__file__).resolve().parent
    archivo_env = raiz / ".env"
    if archivo_env.exists():
        for linea in archivo_env.read_text().splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            os.environ.setdefault(clave.strip(), valor.strip())

    api_key = os.environ.get("GROQ_API_KEY", "")
    if api_key and not api_key.startswith("gsk_REEMPLAZA"):
        return

    archivo_cifrado = raiz.parent / "secrets" / "groq.enc.env"
    if not archivo_cifrado.exists():
        return
    try:
        resultado = subprocess.run(
            ["sops", "--decrypt", "--extract", '["GROQ_API_KEY"]', str(archivo_cifrado)],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        return
    if resultado.returncode == 0 and resultado.stdout.strip():
        os.environ["GROQ_API_KEY"] = resultado.stdout.strip()
```

**Qué hace:** busca la `GROQ_API_KEY` en tres lugares, en este orden, y
se detiene en el primero que encuentre con un valor real:

1. **Variable de entorno ya exportada** (`export GROQ_API_KEY=...` en la
   terminal) — si ya está ahí, ni siquiera toca el `.env`.
2. **Archivo `.env` de esta misma carpeta** — lo lee línea por línea a
   mano (sin librerías como `python-dotenv`) y carga cada `CLAVE=valor`
   con `os.environ.setdefault`, que solo asigna si la clave todavía no
   existe (así nunca pisa una variable ya exportada).
3. **`../secrets/groq.enc.env` cifrado con sops+age** — si ninguna de las
   dos anteriores tenía una key real (revisa que no sea el placeholder
   `gsk_REEMPLAZA...`), llama al comando `sops` para descifrar solo esa
   clave, en memoria, sin escribir nada a disco.

**Por qué existen los `try/except` y los `if` de salida temprana:** cada
uno cubre un caso donde esa fuente simplemente no aplica (no hay `.env`,
no hay secreto cifrado, no está instalado `sops`) — en ningún caso es un
error del programa, así que la función simplemente sigue buscando en la
siguiente fuente, o se queda callada si ya encontró algo.

**Por qué es una función con cuidado, en vez de una línea:** porque el
objetivo es que un estudiante pueda copiar y pegar el comando del taller
sin tener que recordar exportar nada — el script se encarga solo.

### Paso 1.4 — Llamar a esa función y leer la configuración no secreta

```python
_cargar_configuracion()

GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODELO = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
```

**Qué hace:** primero corre la búsqueda de la key (tiene que pasar
*antes* de leer cualquier otra variable, porque puede venir del mismo
`.env`). Después lee dos variables que no son secretas — la URL del
endpoint de Groq y el modelo a usar — con un valor por default si no
están definidas, así el script funciona sin configurar nada extra.

**Por qué estas dos líneas están a nivel de módulo (no dentro de una
función):** porque se necesitan una sola vez, cuando el script arranca, y
el resto del archivo las usa como constantes globales.

### Paso 1.5 — La función que hace el POST (`preguntar_sin_sdk`)

```python
def preguntar_sin_sdk(pregunta: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("gsk_REEMPLAZA"):
        raise SystemExit(
            "No encontre una GROQ_API_KEY valida. Exportala, ponla en .env, o "
            "configurala cifrada con ../scripts/configurar_secreto.sh"
        )
```

**Qué hace:** revisa que de verdad haya una API key válida antes de
intentar nada. **Por qué:** sin esto, el error que vería un alumno sería
un `403`/`401` de Groq, mucho menos claro que este mensaje explicando
exactamente qué hacer.

```python
    cuerpo = json.dumps({
        "model": MODELO,
        "messages": [{"role": "user", "content": pregunta}],
    }).encode("utf-8")
```

**Qué hace:** construye el cuerpo de la petición HTTP a mano: un
diccionario de Python con el modelo a usar y la lista de mensajes de la
conversación (aquí, un solo mensaje del usuario). `json.dumps(...)` lo
convierte a texto JSON, y `.encode("utf-8")` lo convierte a bytes, porque
así es como se manda el cuerpo de una petición HTTP.

**Por qué `"messages": [...]` es una lista, no un solo string:** porque
así funciona la API de chat completions — siempre espera una secuencia de
mensajes con un rol (`system`, `user`, `assistant`, `tool`), no un texto
suelto. Aquí solo hay un mensaje porque no hay conversación previa ni
herramientas, pero la forma es la misma que usan los agentes con tools.

```python
    peticion = urllib.request.Request(
        url=f"{GROQ_BASE_URL}/chat/completions",
        data=cuerpo,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "llm-directo/1.0",
        },
    )
```

**Qué hace:** arma el objeto de la petición HTTP completa.

- `url=f"{GROQ_BASE_URL}/chat/completions"` — la URL completa del
  endpoint. `GROQ_BASE_URL` ya termina en `/openai/v1`, así que la URL
  final queda como `https://api.groq.com/openai/v1/chat/completions`.
- `data=cuerpo` — los bytes JSON de arriba, van en el cuerpo del POST.
- `method="POST"` — explícito, porque `urllib` por default usaría `GET`
  si no se lo indicas (o lo infiere mal si solo le pasas `data`).
- `headers["Authorization"]` — así se autentica cualquier API compatible
  con OpenAI: un *bearer token* con tu API key.
- `headers["Content-Type"]` — le dice al servidor que el cuerpo es JSON,
  no texto plano ni un formulario.
- `headers["User-Agent"]` — **el único header que no es obvio.** Sin él,
  Groq responde `403 Forbidden`: algunos proveedores filtran el
  User-Agent por default de `urllib` (`Python-urllib/3.11`), así que hay
  que poner uno propio para que la petición pase.

```python
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        datos = json.loads(respuesta.read())

    return datos["choices"][0]["message"]["content"]
```

**Qué hace:** envía la petición (`urlopen`), lee la respuesta completa
(`.read()`, que regresa bytes), y la convierte de JSON a diccionario de
Python (`json.loads`). El `timeout=30` evita que el script se quede
colgado para siempre si Groq no responde.

**Por qué `datos["choices"][0]["message"]["content"]`:** porque así viene
estructurada la respuesta de cualquier API de chat completions —
`choices` es una lista (puede pedir varias respuestas alternativas a la
vez, casi siempre solo usamos la primera, índice `0`), y dentro de cada
opción hay un `message` con el `content` (el texto de la respuesta).

### Paso 1.6 — El bloque principal

```python
if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or "¿Que es un agente de IA?"
    print(preguntar_sin_sdk(pregunta))
```

**Qué hace:** toma todos los argumentos de la línea de comandos después
del nombre del script (`sys.argv[1:]`) y los une con espacios, para que
no haga falta poner la pregunta entre comillas con cuidado de escapes.
Si no se pasó ninguna pregunta, usa una por default.

**Por qué `if __name__ == "__main__":`:** para que esta parte solo corra
cuando ejecutas el archivo directamente (`uv run llm_directo.py ...`), no
si alguien lo importa como módulo desde otro script.

### Lo que esta parte deja claro

El SDK de `openai` (que usan los demás scripts) no hace nada mágico:
construye este mismo JSON, le pone estos mismos headers, y te devuelve un
objeto en vez de un `dict` crudo. Quitar el SDK de en medio ayuda a que
ningún framework que venga después (el SDK mismo, LangGraph, ether-brain)
se sienta como una caja negra — todos terminan en esta misma llamada
HTTP.

**Lo que todavía le falta a este script:** no tiene ninguna forma de
consultar datos reales. Si le preguntas "¿cuánto pesa Pikachu?", el
modelo va a responder solo con lo que aprendió en su entrenamiento — sin
poder confirmarlo contra ninguna fuente. Ese es el problema que resuelve
la Parte 2.

---

## Parte 2: `agente-pokemon` — el agente de Pikachu

Ahora sí: vamos a darle al modelo una herramienta real, conectada a
[PokeAPI](https://pokeapi.co/), para que pueda responder con datos
verificables en vez de inventar. Esto sí usa el SDK de `openai` (apuntado
al endpoint de Groq) porque el ciclo de *tool calling* que viene abajo
sería mucho más código de manejar a mano con `urllib`.

### Paso 2.1 — El encabezado y los imports

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["openai", "requests"]
# ///
```

**Qué cambia respecto a `llm_directo.py`:** ahora sí hay dos dependencias
externas. `openai` es el cliente que habla con el endpoint de Groq (en
vez de armar el POST a mano), y `requests` es para llamar a PokeAPI
dentro de la herramienta.

```python
import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from openai import OpenAI
```

`json`, `os`, `subprocess`, `sys` y `Path` cumplen el mismo papel que en
`llm_directo.py`. Lo nuevo es `requests` (para PokeAPI) y `OpenAI` (el
cliente del SDK).

### Paso 2.2 — `_cargar_configuracion`, `GROQ_BASE_URL` y `MODELO`

Son exactamente las mismas que en `llm_directo.py` (ver Pasos 1.3 y 1.4)
— el mecanismo de buscar la API key no cambia entre scripts, así que el
código es intencionalmente idéntico, no se comparte vía un módulo común
(cada script de esta carpeta se puede leer solo, de arriba a abajo, sin
saltar a ningún otro archivo).

### Paso 2.3 — La función que sí hace algo real: `obtener_pokemon`

```python
def obtener_pokemon(nombre: str) -> dict:
    """Busca datos de un Pokemon por nombre en PokeAPI."""
    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}", timeout=10)
    if resp.status_code != 200:
        return {"error": f"No encontre un Pokemon llamado '{nombre}'"}
    datos = resp.json()
    return {
        "nombre": datos["name"],
        "altura_decimetros": datos["height"],
        "peso_hectogramos": datos["weight"],
        "tipos": [t["type"]["name"] for t in datos["types"]],
    }
```

**Qué hace:** es una función de Python completamente normal, sin nada de
IA. Llama a PokeAPI con el nombre del Pokemon, y si lo encuentra, regresa
un diccionario simple con nombre, altura, peso y tipos.

**Por qué `nombre.lower()`:** PokeAPI espera el nombre en minúsculas
(`pikachu`, no `Pikachu`) — esto evita que el modelo tenga que acordarse
de ese detalle.

**Por qué regresa un `dict` con `"error"` en vez de lanzar una
excepción:** porque este diccionario se le va a regresar al modelo como
si fuera el resultado de la herramienta — si el Pokemon no existe, es
mejor que el modelo *vea* el error y pueda explicárselo al usuario, en
vez de que el programa se caiga.

**Cómo probarla sola, sin agente ni LLM de por medio:**

```bash
uv run --with requests python3 -c "
from pokemon import obtener_pokemon
print(obtener_pokemon('pikachu'))
"
```

### Paso 2.4 — Describir esa función para el modelo: `HERRAMIENTAS`

```python
HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_pokemon",
            "description": "Busca altura, peso y tipos de un Pokemon por su nombre.",
            "parameters": {
                "type": "object",
                "properties": {"nombre": {"type": "string", "description": "Nombre del Pokemon, ej. 'pikachu'"}},
                "required": ["nombre"],
            },
        },
    },
]
```

**Qué hace:** el modelo nunca ve el código de `obtener_pokemon` — solo ve
esta descripción en JSON. Es como una "ficha técnica" de la función:

- `"name"` — tiene que ser exactamente igual al nombre real de la función
  en Python, porque así es como el agente la va a buscar después.
- `"description"` — texto en lenguaje natural que el modelo lee para
  decidir *cuándo* le conviene usar esta herramienta. Mientras más clara
  y específica, mejor decide el modelo.
- `"parameters"` — un JSON Schema que describe los argumentos que la
  función necesita: aquí, un solo argumento `nombre` de tipo `string`,
  obligatorio (`"required": ["nombre"]`).

**Por qué este formato exacto (`"type": "function"`, `"function": {...}`)
y no algo más simple:** porque es el formato que define la API de
OpenAI para *function calling*, y Groq lo replica tal cual en su endpoint
de compatibilidad — no es una invención de este script.

### Paso 2.5 — El diccionario nombre → función real: `FUNCIONES`

```python
FUNCIONES = {"obtener_pokemon": obtener_pokemon}
```

**Qué hace:** conecta el `"name"` que usó el modelo (un string) con la
función de Python real que hay que ejecutar. Cuando el modelo dice "quiero
usar `obtener_pokemon`", el código hace `FUNCIONES["obtener_pokemon"]` y
obtiene la función de verdad, lista para llamar.

**Por qué hace falta este diccionario aparte de `HERRAMIENTAS`:** porque
`HERRAMIENTAS` es para que el *modelo* lea la descripción — no contiene
la función ejecutable. `FUNCIONES` es para que el *código* la encuentre y
la ejecute. Son dos cosas distintas que comparten el mismo nombre.

### Paso 2.6 — El corazón del agente: `preguntar_al_agente`

```python
def preguntar_al_agente(pregunta: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key.startswith("gsk_REEMPLAZA"):
        raise SystemExit(
            "No encontre una GROQ_API_KEY valida. Exportala, ponla en .env, o "
            "configurala cifrada con ../scripts/configurar_secreto.sh"
        )
    cliente = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
```

**Qué hace:** misma validación de la key que en `llm_directo.py`, y
después crea el cliente del SDK de `openai`, apuntándolo al
`base_url` de Groq en vez del de OpenAI — así es como cualquier API
"compatible con OpenAI" funciona: mismo cliente, distinta URL.

```python
    mensajes = [
        {"role": "system", "content": "Eres un agente experto en Pokemon. Usa las herramientas cuando las necesites."},
        {"role": "user", "content": pregunta},
    ]
```

**Qué hace:** arma la lista de mensajes inicial — un mensaje `system`
(instrucciones generales para el modelo, invisibles para el usuario) y un
mensaje `user` (la pregunta real). Esta lista va a ir creciendo dentro
del ciclo.

```python
    for _ in range(5):  # tope de seguridad: maximo 5 vueltas del ciclo
        respuesta = cliente.chat.completions.create(model=MODELO, messages=mensajes, tools=HERRAMIENTAS)
        mensaje = respuesta.choices[0].message
        mensajes.append(mensaje)
```

**Qué hace:** aquí está la diferencia clave contra `sin_tool.py` y
`llm_directo.py` — esta llamada sí manda `tools=HERRAMIENTAS`. Eso le da
al modelo la *opción* de pedir usar una herramienta en vez de responder
directo. La respuesta del modelo (sea texto, sea una petición de tool) se
agrega a `mensajes`, porque la próxima vuelta del ciclo necesita ver toda
la conversación hasta ahora.

**Por qué `for _ in range(5)` y no un `while True`:** es un tope de
seguridad. Si por alguna razón el modelo se queda pidiendo herramientas
en bucle sin nunca dar una respuesta final, el script no se cuelga para
siempre — corta después de 5 vueltas.

```python
        if not mensaje.tool_calls:
            return mensaje.content
```

**Qué hace:** si el modelo *no* pidió ninguna herramienta esta vez
(`tool_calls` viene vacío o `None`), es porque ya tiene su respuesta
final — el ciclo termina aquí y se regresa ese texto.

```python
        for llamada in mensaje.tool_calls:
            funcion = FUNCIONES[llamada.function.name]
            # Groq a veces manda {"": {}} para tools sin parametros -- se descarta esa clave vacia.
            argumentos = {k: v for k, v in json.loads(llamada.function.arguments).items() if k}
            resultado = funcion(**argumentos)
            print(f"  -> el agente uso {llamada.function.name}({argumentos})")
            mensajes.append({
                "role": "tool",
                "tool_call_id": llamada.id,
                "content": json.dumps(resultado),
            })
```

**Qué hace, paso por paso, si el modelo SÍ pidió una herramienta:**

1. `FUNCIONES[llamada.function.name]` — busca la función real de Python
   usando el nombre que mandó el modelo (este es el momento en que el
   diccionario `FUNCIONES` del Paso 2.5 se usa).
2. `json.loads(llamada.function.arguments)` — los argumentos que pidió el
   modelo vienen como un *string* JSON (ej. `'{"nombre": "pikachu"}'`),
   hay que convertirlos a diccionario de Python antes de poder usarlos.
   El filtro `if k` descarta cualquier clave vacía — un detalle real que
   se encontró probando: Groq a veces manda `{"": {}}` para herramientas
   sin parámetros, y eso rompería la llamada si no se filtrara.
3. `funcion(**argumentos)` — ejecuta la función real, pasándole los
   argumentos como keyword arguments (`**` los "desempaqueta" del
   diccionario). Aquí es donde de verdad se llama a PokeAPI.
4. `print(...)` — esta es la línea que el alumno ve en la terminal como
   `-> el agente uso obtener_pokemon({'nombre': 'pikachu'})`: hace visible
   que el modelo decidió, por sí mismo, qué herramienta usar y con qué
   argumentos.
5. Se agrega un mensaje con `"role": "tool"` a `mensajes`, con el
   resultado de la función convertido de vuelta a JSON
   (`json.dumps(resultado)`). El `tool_call_id` conecta esta respuesta con
   la petición específica que la originó (importante cuando el modelo
   pide varias herramientas a la vez).

**Qué pasa después de este `for`:** el ciclo principal (`for _ in
range(5)`) vuelve a empezar, y se manda otra vez `cliente.chat.completions.create(...)`
— ahora con el resultado de la herramienta ya incluido en `mensajes`. El
modelo ve ese resultado y, normalmente, ya puede responder con texto
final (entonces el `if not mensaje.tool_calls` de arriba va a ser cierto
en la siguiente vuelta).

```python
    return "No pude resolverlo en el numero de intentos permitido."
```

**Qué hace:** si después de 5 vueltas el modelo sigue sin dar una
respuesta final, se regresa este mensaje en vez de quedarse colgado. En
la práctica, casi nunca se llega aquí — el modelo normalmente resuelve en
1 o 2 vueltas.

### Paso 2.7 — El bloque principal

```python
if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or "¿Cuanto pesa pikachu?"
    print(preguntar_al_agente(pregunta))
```

Igual que en `llm_directo.py` (Paso 1.6), pero con una pregunta por
default sobre Pikachu — la pregunta que da nombre a este ejercicio.

### Por qué esto ya es "un agente" y no solo "una llamada a un LLM"

La diferencia no es que el modelo "sea más inteligente" — es el mismo
modelo en los tres scripts de esta guía. La diferencia es el ciclo: el
modelo puede pedir información intermedia (`tool_calls`), el código se la
da, y el modelo decide con esa información qué hacer después. Nadie en el
código le dice "usa `obtener_pokemon`" — el modelo lee la descripción en
`HERRAMIENTAS` y decide solo, según la pregunta, si la necesita.

---

## Cómo corren estos dos scripts, lado a lado

```bash
cd llm-directo      && uv run llm_directo.py "¿cuanto pesa pikachu?"
cd ../agente-pokemon && uv run pokemon.py "¿cuanto pesa pikachu?"
```

La primera respuesta es texto inventado por el modelo, sin forma de
verificarlo. La segunda muestra la línea `-> el agente uso
obtener_pokemon(...)` y responde con el peso real que regresa PokeAPI.
Esa diferencia, vista en vivo, es el punto de toda esta guía.

## Siguiente paso

Una vez que esto se entiende, los demás agentes de esta carpeta
(`agente-clima/`, que encadena dos herramientas; `agente-consejos/`, que
agrega búsqueda por palabra clave; y `agente-orquestador/`, que junta
varias herramientas en una sola lista) usan exactamente el mismo ciclo de
`preguntar_al_agente` — ver [`como-funciona.md`](./como-funciona.md) para
los detalles de cada uno.

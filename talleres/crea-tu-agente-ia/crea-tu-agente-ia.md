---
marp: true
theme: default
paginate: true
size: 16:9
format: pdf

title: Cómo crear tu propio agente de IA usando solo software libre
description: Taller práctico para construir un agente de IA con herramientas Open Source.
header: Cómo crear tu propio agente de IA usando solo software libre
footer: Raúl González - rafex@rafex.dev
author: Raúl Eduardo González Argote by rafex@rafex.dev
date: 24 junio 2026
---

<!--
Taller: 10:00 - 13:00
Foro de Tecnologías de la Información y Software Libre 2026
Universidad Politécnica de Tlaxcala
Objetivo: que cada asistente entienda y construya un agente funcional con software libre.
-->

# Cómo crear tu propio agente de IA

## usando solo software libre

Raúl Eduardo González Argote

---

## Resultado del taller

Al final vas a tener, corriendo en tu máquina:

* Un programa que llama al LLM **sin** herramientas
* El mismo programa, pero con **una** herramienta conectada a una API real
* Claridad sobre por qué esos dos programas responden distinto
* Tu propia API key de Groq, guardada de forma segura (cifrada)

---

## La regla del taller

No venimos a mirar IA.

Venimos a construir con IA.

---

## Stack propuesto

* Linux, macOS o Windows con WSL
* Python 3.11+ con [uv](https://docs.astral.sh/uv/) (no se instala nada más a mano)
* API key de [Groq](https://console.groq.com/keys) (gratis)
* [age](https://github.com/FiloSottile/age) + [sops](https://github.com/getsops/sops) (cifrar la API key)
* Git

---

## Requisitos técnicos

Antes del taller:

* Laptop
* Git, `uv`, `age`, `sops` instalados
* Editor de código
* Cuenta gratuita en https://console.groq.com/keys
* Internet estable

---

## Instalación base

```bash
git --version
uv --version
age --version
sops --version
```

```bash
git clone https://github.com/rafex/presentaciones-cursos-talleres
cd presentaciones-cursos-talleres/talleres/crea-tu-agente-ia/agente-mini-python
```

Sin `pip install`: cada script declara sus dependencias en su propio
encabezado y `uv` las instala solo, la primera vez que lo corres.

---

## Agenda

* 10:00 - 10:20 | Qué es un agente
* 10:20 - 10:40 | Configurar tu API key (de forma segura)
* 10:40 - 11:10 | El experimento: sin tool vs con tool
* 11:10 - 11:40 | Cómo funciona el ciclo, línea por línea
* 11:40 - 12:20 | Práctica guiada: cambia la tool, rompe el agente, arréglalo
* 12:20 - 13:00 | Retos, demo final y cierre

---

## 1. Qué es un agente

Un agente no es un chatbot.

Un agente tiene objetivo, herramientas y ciclo de decisión.

---

## Ciclo básico

Usuario

↓

Pregunta

↓

Modelo (Groq)

↓

¿Necesita herramienta? → Tool → vuelve al modelo

↓

Respuesta

Hoy vas a ver este ciclo en su versión más pequeña posible: un solo
archivo de Python, sin frameworks.

---

## 2. Tu API key, sin subirla por accidente a git

Un secreto en texto plano en un repo es un accidente esperando a pasar.

[age](https://github.com/FiloSottile/age): llaves simples, sin
infraestructura.

[sops](https://github.com/getsops/sops): cifra los *valores* de un
archivo, las claves quedan legibles — los diffs de PR siguen siendo
útiles.

```bash
./scripts/configurar_secreto.sh
```

Pide tu `GROQ_API_KEY` (sin mostrarla en pantalla) y deja
`secrets/groq.enc.env` cifrado automáticamente.

---

## Cómo la encuentra el código

Cada script busca la key en este orden, solo:

1. Variable de entorno ya exportada
2. `.env` local de esa carpeta
3. `secrets/groq.enc.env` cifrado — el script lo descifra solo, en
   memoria, llamando a `sops`

No hace falta envolver el comando con nada para que funcione.

---

## 3. El experimento: misma pregunta, dos agentes

Pregunta para los dos: **"¿cuánto pesa pikachu?"**

```
agente-sin-tool/sin_tool.py   →  solo el LLM, sin acceso a datos reales
agente-pokemon/pokemon.py     →  el LLM + una tool conectada a PokeAPI
```

Vamos a correr los dos, en vivo, y comparar las respuestas.

---

## `agente-sin-tool`: el LLM puro

```python
def preguntar_sin_herramientas(pregunta: str) -> str:
    cliente = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    respuesta = cliente.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Responde lo mejor que puedas."},
            {"role": "user", "content": pregunta},
        ],
        # Sin "tools": el modelo no tiene forma de consultar datos reales.
    )
    return respuesta.choices[0].message.content
```

```bash
cd agente-sin-tool
uv run sin_tool.py "¿cuánto pesa pikachu?"
```

---

## Qué responde `agente-sin-tool`

El modelo va a inventar un número, con el mismo tono seguro de siempre —
o, con suerte, admitir que no está seguro.

No es que "no sea inteligente": literalmente no tiene ninguna forma de
verificar ese dato. Solo tiene lo que aprendió en su entrenamiento.

Esa es la pregunta que el resto del taller responde: ¿cómo le damos
acceso a datos reales?

---

## `agente-pokemon`: el LLM + una tool

```python
def obtener_pokemon(nombre: str) -> dict:
    """Busca datos de un Pokemon por nombre en PokeAPI."""
    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}")
    datos = resp.json()
    return {
        "nombre": datos["name"],
        "peso_hectogramos": datos["weight"],
        "tipos": [t["type"]["name"] for t in datos["types"]],
    }
```

Una función de Python normal. Nada de IA todavía — solo `requests`
contra una API pública y gratuita, sin API key.

---

## Decirle al modelo que esa función existe

```python
HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_pokemon",
            "description": "Busca peso y tipos de un Pokemon por su nombre.",
            "parameters": {
                "type": "object",
                "properties": {"nombre": {"type": "string"}},
                "required": ["nombre"],
            },
        },
    },
]
```

El modelo no ejecuta código: solo **lee esta descripción** y decide si
la necesita.

---

## Correrlo

```bash
cd agente-pokemon
uv run pokemon.py "¿cuánto pesa pikachu?"
```

```
  -> el agente uso obtener_pokemon({'nombre': 'pikachu'})
Pikachu pesa 6.0 kg (60 hectogramos) y es de tipo eléctrico.
```

La línea `-> el agente uso ...` es el modelo decidiendo, por sí mismo,
qué herramienta necesita y con qué argumento — eso es lo que lo hace un
agente y no solo una llamada a un chatbot.

---

## 4. El ciclo, línea por línea

```python
mensajes = [{"role": "system", "content": "..."}, {"role": "user", "content": pregunta}]

for _ in range(5):                              # tope de seguridad
    respuesta = cliente.chat.completions.create(
        model=MODELO, messages=mensajes, tools=HERRAMIENTAS
    )
    mensaje = respuesta.choices[0].message
    mensajes.append(mensaje)

    if not mensaje.tool_calls:
        return mensaje.content                  # ya tiene la respuesta final

    for llamada in mensaje.tool_calls:
        funcion = FUNCIONES[llamada.function.name]
        resultado = funcion(**json.loads(llamada.function.arguments))
        mensajes.append({"role": "tool", "tool_call_id": llamada.id,
                          "content": json.dumps(resultado)})
```

---

## Paso a paso

1. Se manda la pregunta + la lista de herramientas disponibles.
2. El modelo responde: "necesito `obtener_pokemon(nombre='pikachu')`" —
   no da respuesta final todavía (`tool_calls` no está vacío).
3. El código ejecuta esa función de verdad, contra la API real, y le
   manda el resultado al modelo (`role: "tool"`).
4. El modelo, ya con el dato real en su contexto, responde con texto
   normal — el ciclo termina.

El `for _ in range(5)` evita que un modelo en bucle corra para siempre.

---

## Por qué esto es "un agente" y no "un chatbot"

Un chatbot responde con texto a partir de texto.

Este programa **decide por sí mismo** cuántas veces y en qué orden
necesita consultar datos externos reales antes de responder — ese ciclo
de "pensar → actuar → observar → repetir" es la definición práctica de
agente que usa todo este taller.

---

## 5. Práctica guiada

* Cambia la pregunta — prueba con otro Pokemon, o uno que no existe
* Quita el parámetro `tools=HERRAMIENTAS` de `pokemon.py` — ¿qué cambia?
* Lee `agente-sin-tool/sin_tool.py` y `agente-pokemon/pokemon.py` lado a
  lado: ¿cuál es la única diferencia real entre los dos?
* Rompe a propósito la `description` de la tool — ¿el modelo sigue
  encontrándola?

---

## Protección contra subir una API key por accidente

`.gitignore` en la raíz del proyecto y otro dentro de cada carpeta de
agente — protegen cualquier `.env` en texto plano. Solo
`secrets/*.enc.env` (cifrado) y `secrets/*.example.env` (plantilla sin
secretos) están exceptuados.

```bash
git check-ignore -v agente-pokemon/.env       # debe estar ignorado
git check-ignore -v secrets/groq.enc.env      # NO debe estar ignorado
```

---

## Retos extra

* `agente-clima/` — la misma idea, con una API de clima encadenando dos
  tools (`geocodificar` → `clima`)
* `agente-consejos/` — la misma idea, con una API de consejos al azar
* `agente-orquestador/` — las tres tools anteriores juntas: el modelo
  decide cuál o cuáles necesita, sin que el código le diga nada
* Agrega tu propia tool con otra [API pública](https://github.com/public-apis/public-apis)

---

## Producto final

Cada asistente entrega:

* Su `GROQ_API_KEY` configurada y cifrada con `age` + `sops`
* `agente-sin-tool/sin_tool.py` y `agente-pokemon/pokemon.py` corriendo
* Una explicación, en sus palabras, de por qué responden distinto
* (Bonus) una tool propia agregada a alguno de los agentes

---

## Rúbrica rápida

Funciona.

Usa software libre.

Explica sus decisiones.

Se puede mejorar.

---

## Cierre

No necesitas permiso para empezar.

Necesitas curiosidad, criterio y práctica.

---

## Siguiente paso

Publica tu agente.

Explícalo.

Compártelo.

Mejóralo.

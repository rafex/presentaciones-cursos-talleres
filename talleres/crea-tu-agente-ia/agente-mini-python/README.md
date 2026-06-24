# agente-mini-python

La versión más pequeña posible de un agente de IA: un solo archivo por
agente, sin frameworks, sin proyecto que instalar. Pensada para un grupo
universitario que ve esto por primera vez.

## Qué hay aquí

Cada agente vive en su propia carpeta, autocontenido:

| Carpeta | Qué hace | API que usa |
|---|---|---|
| [`agente-sin-tool/`](./agente-sin-tool/) | El "antes": el mismo modelo, sin ninguna herramienta | — (ninguna) |
| [`agente-clima/`](./agente-clima/) | Responde preguntas sobre el clima de una ciudad | [Open-Meteo](https://open-meteo.com/) (gratis, sin API key) |
| [`agente-pokemon/`](./agente-pokemon/) | Responde preguntas sobre Pokemon (peso, altura, tipo) | [PokeAPI](https://pokeapi.co/) (gratis, sin API key) |
| [`agente-consejos/`](./agente-consejos/) | Da consejos al azar o buscados por palabra clave | [Advice Slip API](https://api.adviceslip.com/) (gratis, sin API key) |
| [`agente-orquestador/`](./agente-orquestador/) | Combina las tres tools anteriores y decide cuál(es) usar | Las tres de arriba |

Empieza por `agente-sin-tool/`, sigue con `agente-clima/`,
`agente-pokemon/` y `agente-consejos/` en cualquier orden, y termina con
`agente-orquestador/`. Ese orden cuenta una historia completa: sin
herramientas el modelo solo inventa → con una herramienta el modelo
resuelve un problema concreto → con varias herramientas el modelo decide
cuál necesita en cada caso.

Cada script se puede leer de arriba a abajo sin saltar a ningún otro
archivo (excepto el orquestador, que junta las tools de los otros tres a
propósito, como punto de llegada).

## Requisitos

* [uv](https://docs.astral.sh/uv/) instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
* Una API key gratuita de Groq: https://console.groq.com/keys

No se necesita `pip install` nada a mano — cada script declara sus
dependencias en su propio encabezado (`# /// script ... ///`) y `uv` las
instala solo, en un entorno temporal, la primera vez que lo corres.

## Cómo correrlo

Necesitas tu `GROQ_API_KEY` disponible como variable de entorno. Hay dos
formas — usa la que te quede más cómoda:

### Opción rápida: export manual

```bash
export GROQ_API_KEY=gsk_...

cd agente-sin-tool       && uv run sin_tool.py "¿que clima hay en Tlaxcala en este momento?"
cd ../agente-clima       && uv run clima.py "¿que clima hay en Tlaxcala?"
cd ../agente-pokemon     && uv run pokemon.py "¿cuanto pesa pikachu?"
cd ../agente-consejos    && uv run consejos.py "dame un consejo sobre el amor"
cd ../agente-orquestador && uv run orquestador.py "¿que clima hay en Tlaxcala y cuanto pesa pikachu?"
```

### Opción segura: age + sops (recomendada si vas a compartir tu API key)

Este repo trae un secreto cifrado de ejemplo en
[`secrets/groq.enc.env`](./secrets/groq.enc.env) — solo quien tenga la
llave privada age correspondiente puede descifrarlo. Para usar tu propia
API key, corre el script interactivo:

```bash
./scripts/configurar_secreto.sh
```

Te va a pedir la `GROQ_API_KEY` (sin mostrarla en pantalla) y va a dejar
`secrets/groq.enc.env` cifrado automáticamente — no hay que editar nada a
mano ni acordarse del comando de `sops`. Si el archivo ya existe, pregunta
antes de sobrescribirlo.

Equivalente manual, por si prefieres hacerlo paso a paso:

```bash
cp secrets/groq.example.env secrets/groq.enc.env
$EDITOR secrets/groq.enc.env             # pega tu GROQ_API_KEY real
sops --encrypt --in-place secrets/groq.enc.env
```

Para usar la API key ya cifrada:

```bash
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt   # ruta de tu llave privada age

cd agente-clima
sops exec-env ../secrets/groq.enc.env "uv run clima.py '¿que clima hay en Tlaxcala?'"
```

`sops exec-env` descifra el archivo en memoria, exporta `GROQ_API_KEY`
solo para ese proceso, y nunca escribe el secreto sin cifrar a disco — el
mismo patrón que usa
[`agente-clima-etherbrain`](../agente-clima-etherbrain/docs/secretos.md).
El archivo `secrets/groq.enc.env` resultante es seguro de commitear: solo
las claves quedan legibles, los valores quedan cifrados.

Sin argumentos, cada script usa una pregunta de ejemplo por default.

## Qué vas a ver en la terminal

Con una tool (`agente-clima`):

```
  -> el agente uso obtener_coordenadas({'ciudad': 'Tlaxcala'})
  -> el agente uso obtener_clima({'latitud': 19.31777, 'longitud': -98.23846})
En Tlaxcala hace 13.1°C con viento de 6.7 km/h.
```

Cada línea `-> el agente uso ...` es el agente decidiendo, por sí mismo,
qué herramienta necesita y con qué argumentos — esa es la parte que lo
hace un agente y no solo una llamada a un chatbot.

Sin ninguna tool (`agente-sin-tool`), el modelo va a responder algo
igual de seguro en tono, pero inventado o desactualizado — no tiene forma
de saber el clima de ahora mismo. Esa comparación, lado a lado, es el
punto del ejercicio.

## Protección contra subir una API key por accidente

Hay un `.gitignore` en la raíz de `agente-mini-python/` (protege
`secrets/*.env` sin cifrar y cualquier llave `*.agekey`) y otro `.gitignore`
dentro de cada carpeta de agente (protege un `.env` local si decides usar
la opción rápida ahí). Solo `secrets/*.enc.env` y `secrets/*.example.env`
están exceptuados — son los únicos que deben llegar a git.

## Documentación

Ver [`docs/como-funciona.md`](./docs/como-funciona.md) para una
explicación línea por línea del ciclo que comparten estos agentes, y por
qué `agente-sin-tool` no puede resolverlo.

## Siguiente paso

Si esto se entendió bien, el taller completo (`crea-tu-agente-ia.md`, en
la carpeta de arriba) usa el mismo ciclo pero con frameworks reales
(LangGraph, MCP) y un runtime en otro lenguaje (ether-brain, Java) — útil
para ver el mismo patrón en herramientas de nivel producción.

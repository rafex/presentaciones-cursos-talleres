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

Al final tendrás **dos** agentes que pueden:

* Recibir una tarea
* Razonar un plan corto
* Usar herramientas — declarativas (`tools.json`) o vía MCP
* Consultar datos reales
* Entregar una respuesta verificable

---

## La regla del taller

No venimos a mirar IA.

Venimos a construir con IA.

---

## Stack propuesto

* Linux, macOS o Windows con WSL
* Java 21 + Maven (para [ether-brain](https://github.com/rafex/ether-brain))
* Python 3.11+ con [uv](https://docs.astral.sh/uv/)
* API key de [Groq](https://console.groq.com/keys) (gratis)
* [age](https://github.com/FiloSottile/age) + [sops](https://github.com/getsops/sops) (cifrar la API key)
* LangGraph + MCP (Model Context Protocol)
* Git

<!-- notes:
Si el laboratorio no tiene internet estable, llevar API keys de respaldo y
el fixture local del repo como plan B para la demo de SEPOMEX.
-->

---

## Requisitos técnicos

Antes del taller:

* Laptop
* Git, Java 21, Maven, `uv` instalados
* `age` y `sops` instalados (`brew install age sops` / `apt install age sops`)
* Editor de código
* Cuenta gratuita en https://console.groq.com/keys
* Internet estable

---

## Instalación base

```bash
git --version
java -version
mvn --version
uv --version
age --version
sops --version
```

```bash
git clone https://github.com/rafex/presentaciones-cursos-talleres
git clone https://github.com/rafex/ether-brain
```

---

## Agenda

* 10:00 - 10:15 | Qué es un agente
* 10:15 - 10:45 | Ejercicio 1: clima con ether-brain, sin código
* 10:45 - 11:10 | Secretos con age + sops
* 11:10 - 11:45 | Ejercicio 2: LangGraph + MCP
* 11:45 - 12:30 | El caso: direcciones con SEPOMEX
* 12:30 - 13:00 | Demo final, retos y cierre

---

## 1. Qué es un agente

Un agente no es un chatbot.

Un agente tiene objetivo, herramientas y ciclo de decisión.

---

## Ciclo básico

Usuario

↓

Objetivo

↓

Modelo (Groq)

↓

¿Necesita herramienta? → Tool → vuelve al modelo

↓

Respuesta

Este ciclo es el mismo sin importar si el runtime es Java o Python — lo
vas a ver dos veces hoy, con dos implementaciones distintas.

---

## Ejercicio 1: el agente más simple posible

Objetivo: un agente que responda "¿qué clima hay en \<ciudad\>?" sin
escribir una sola línea de código — solo declarando herramientas.

Runtime: [ether-brain](https://github.com/rafex/ether-brain), Java 21,
arquitectura hexagonal, sin frameworks pesados.

```bash
cd ether-brain/ether-brain
./mvnw -q -pl ether-brain-transport-cli -am package -DskipTests
```

Código completo: `agente-clima-etherbrain/`

---

## ether-brain no está en Maven Central (todavía)

Se compila desde el código fuente — es software libre, el código *es* la
distribución.

```bash
export ETHER_BRAIN_JAR=.../ether-brain-transport-cli/target/ether-brain-cli.jar
```

<!-- notes:
Confirmado buscando en search.maven.org/solrsearch -- numFound: 0.
-->

---

## Las tools, sin código: `tools.json`

```json
{
  "type":        "http",
  "name":        "clima_actual",
  "endpoint":    "https://api.open-meteo.com/v1/forecast?current_weather=true&timezone=auto",
  "method":      "GET",
  "input_schema": {
    "type": "object",
    "properties": {
      "latitude":  {"type": "number"},
      "longitude": {"type": "number"}
    },
    "required": ["latitude", "longitude"]
  }
}
```

ether-brain reenvía los argumentos del modelo como query params. Dos
tools así (`geocodificar_ciudad` + `clima_actual`) y el modelo las
encadena solo.

---

## Probarlo sin gastar una llamada al LLM

```bash
cd agente-clima-etherbrain
LLM_TYPE=demo java -jar "$ETHER_BRAIN_JAR" "hola"
```

```
[EtherBrain] tool http: geocodificar_ciudad → https://geocoding-api.open-meteo.com/...
[EtherBrain] tool http: clima_actual → https://api.open-meteo.com/...
[EtherBrain] 2 tool(s) externas cargadas desde tools.json
```

`LLM_TYPE=demo` confirma que `tools.json` se parseó bien, sin tocar Groq.

---

## 2. Secretos: nada de `.env` en texto plano

Un secreto en texto plano en un repo es un accidente esperando a pasar.

[age](https://github.com/FiloSottile/age): llaves simples, sin
infraestructura.

[sops](https://github.com/getsops/sops): cifra los *valores* de un
archivo, las claves quedan legibles — los diffs de PR siguen siendo
útiles.

```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
# Public key: age1...
```

---

## `.sops.yaml`: quién puede descifrar qué

```yaml
creation_rules:
  - path_regex: secrets/.*\.enc\.env$
    age: age1kyupq4um57pmddeuaxm4dtwah9hhmxv3ty5tvjr7detgzlrfl9zsdte4zj
```

```bash
cp secrets/groq.example.env secrets/groq.enc.env
$EDITOR secrets/groq.enc.env        # pega tu LLM_TOKEN real
sops --encrypt --in-place secrets/groq.enc.env
```

A partir de aquí, `secrets/groq.enc.env` es seguro de commitear.

---

## Correr el agente con el secreto descifrado en memoria

```bash
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt

sops exec-env secrets/groq.enc.env \
  "java -jar $ETHER_BRAIN_JAR '¿qué clima hay en Tlaxcala?'"
```

`sops exec-env` descifra, exporta las variables solo para ese proceso, y
nunca escribe el secreto sin cifrar a disco.

---

## Un bug real que encontramos probando esto

La documentación de ether-brain dice `LLM_URL=https://api.groq.com`.

```bash
curl -X POST https://api.groq.com/v1/chat/completions          # 404
curl -X POST https://api.groq.com/openai/v1/chat/completions   # 401 (correcto)
```

La URL real de Groq necesita el prefijo `/openai`. Reportado al proyecto;
mientras tanto, `secrets/groq.example.env` ya trae la URL corregida.

Probar en vivo encuentra cosas que la documentación no.

---

## Ejercicio 2: ahora con código — LangGraph

Objetivo:

Construir un grafo explícito: el modelo decide, y si pide una
herramienta, el grafo la ejecuta y vuelve a preguntarle al modelo.

```python
grafo.add_node("llamar_modelo", llamar_modelo)
grafo.add_node("ejecutar_tools", ToolNode(tools))
grafo.add_conditional_edges(
    "llamar_modelo", hay_tool_calls,
    {"ejecutar_tools": "ejecutar_tools", END: END},
)
grafo.add_edge("ejecutar_tools", "llamar_modelo")
```

Código completo: `agente-cp/src/agente_cp/agente_langgraph.py`

---

## Setup de `agente-cp`

```bash
cd presentaciones-cursos-talleres/talleres/crea-tu-agente-ia/agente-cp
uv sync
cp .env.example .env   # pega tu GROQ_API_KEY
uv run agente-cp "¿Quién eres?"
```

(Todavía sin herramientas — solo el modelo respondiendo.)

---

## Herramientas con MCP

Un agente se vuelve útil cuando puede hacer cosas — y MCP es la forma
estándar de exponer esas cosas sin atarlas a un solo runtime.

```
mcp_server.py  ──→  cualquier agente que hable MCP
```

El mismo servidor MCP de este taller lo puede usar:

* El agente LangGraph (Python) que acabamos de armar.
* [ether-brain](https://github.com/rafex/ether-brain) del Ejercicio 1 —
  vía `tools.json` tipo `"mcp"`, sin escribir una línea de Java.

---

## Caso del taller: direcciones mexicanas

Correos de México (SEPOMEX) publica el catálogo nacional de Códigos
Postales. Lo convertimos una sola vez a **SQLite** (158k registros, 20 MB) —
el taller corre sin depender de que un sitio gubernamental esté arriba.

Construimos un agente que:

* Consulta el catálogo nacional, local y al instante.
* Busca las colonias de un CP.
* Detecta cuando una dirección está mal escrita.
* Sugiere la corrección — "repara" la dirección.

---

## La tool `buscar_cp`

```python
@mcp.tool()
def buscar_cp(cp: str, estado: str) -> dict:
    """Busca un CP en el catalogo oficial de SEPOMEX."""
    ...
```

Pruébala sola, sin LLM, con el inspector de MCP:

```bash
npx @modelcontextprotocol/inspector \
  uv run python -m agente_cp.mcp_server
```

---

## Datos reales, no solo el prompt

La IA sin datos propios responde generalidades.

Con el catálogo de SEPOMEX puede confirmar o corregir una dirección real.

```bash
uv run agente-cp "¿La colonia Tlaxcala Cento corresponde al CP 90001?"
```

El agente debe detectar el typo y sugerir "Tlaxcala Centro".

---

## De XML a SQLite, una sola vez

```bash
uv run python scripts/xml_a_sqlite.py /ruta/a/CPdescarga.xml
```

158,539 filas, 20 MB, en menos de 2 segundos. `data/sepomex.sqlite` ya
queda commiteado — nadie en el taller necesita regenerarlo.

---

## Si no hubiera SQLite (plan B y C)

`sepomex.py` tiene cascada: si falta `data/sepomex.sqlite`, intenta
**scraping en vivo** del formulario de Correos de México; si tampoco hay
red, cae a un **fixture local** de Tlaxcala.

Cada respuesta declara `origen_datos` (`sqlite`, `red`, `cache` o
`fixture`) — mismo patrón que usarías en producción con una API externa
frágil.

---

## MCP en la práctica: dos runtimes, un contrato

```json
{
  "type": "mcp",
  "server_name": "agente-cp",
  "command": ["uv", "run", "--directory", "/ruta/a/agente-cp",
              "python", "-m", "agente_cp.mcp_server"]
}
```

Modelos y runtimes diferentes.

Herramientas reutilizables — el mismo contrato que vimos con `tools.json`
tipo `"http"` en el Ejercicio 1.

---

## Demo guiada

Agente de direcciones, de extremo a extremo:

* Recibe una dirección con un posible error
* Consulta SEPOMEX vía MCP
* Detecta la inconsistencia
* Sugiere la colonia correcta
* (Bonus) geocodifica con OpenStreetMap si el CP no alcanza

---

## Producto final

Cada equipo entrega:

* `agente-clima-etherbrain` corriendo con su propia API key cifrada
* `agente-cp` corriendo (`uv run agente-cp "..."`)
* Al menos una tool propia o modificada (`tools.json` o MCP)
* Demo de un caso donde el agente corrige una dirección mal escrita

---

## Rúbrica rápida

Funciona.

Usa software libre.

Explica sus decisiones.

Se puede mejorar.

---

## Retos extra

* Agregar una tercera tool de clima (pronóstico a varios días) en `agente-clima-etherbrain`
* Agregar una tool con una [API pública](https://github.com/public-apis/public-apis)
  en `agente-cp` y combinarla con `buscar_cp`
* Conectar `mcp_server.py` a ether-brain vía `tools.json` tipo `"mcp"`
* Soportar más de un estado a la vez
* Cambiar de proveedor LLM (Groq → Cerebras/OpenAI/Ollama) sin tocar el agente

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

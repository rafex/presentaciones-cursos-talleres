# Compilar ether-brain desde el código fuente

## No está en Maven Central (todavía)

[ether-brain](https://github.com/rafex/ether-brain) no tiene artefactos
publicados en Maven Central — se confirmó buscando
`https://search.maven.org/solrsearch/select?q=ether-brain&wt=json` y el
resultado es `"numFound": 0`. Coherente con su propio `Makefile`, que ya
trae configurado un `groupId` (`dev.rafex.ether.brain`) y objetivos de
deploy, pero apunta a un repositorio de "build-helpers" externo todavía no
usado para publicar. Por ahora, "instalar ether-brain" significa
clonarlo y compilarlo — consistente con el espíritu de software libre del
taller: el código fuente es la distribución.

## El build

```bash
git clone https://github.com/rafex/ether-brain
cd ether-brain/ether-brain
./mvnw -q -pl ether-brain-transport-cli -am package -DskipTests
```

- `-pl ether-brain-transport-cli`: solo construye ese módulo... pero
- `-am` ("also make"): y todos los módulos de los que depende
  (`ether-brain-core`, `ether-brain-tools-local`, los codecs de
  `ether-brain-infra-http`, etc.) — sin tener que listarlos a mano.
- `-DskipTests`: para el taller no hace falta correr la suite completa
  (incluye pruebas de arquitectura con ArchUnit); quítalo si quieres
  verificar que el runtime pasa sus propias reglas hexagonales.

El resultado relevante:

```
ether-brain-transport-cli/target/ether-brain-cli.jar
```

Es un *fat jar* (~2.5 MB) — incluye todas las dependencias necesarias
(Jackson, los codecs de proveedores, los tipos de tool) en un solo
archivo ejecutable con `java -jar`.

## Por qué `ether-brain-transport-cli` y no otro módulo

ether-brain tiene tres transportes independientes: CLI, HTTP (Jetty) y
MQTT. Para este ejercicio del taller, donde cada asistente corre el
agente desde su terminal y le hace una pregunta a la vez, el transporte
CLI es el más directo — equivalente a `agente-cp` corriendo por línea de
comandos en el otro proyecto del taller. `ether-brain-transport-http`
sería la opción si quisiéramos exponer el agente como servicio
(`POST /sessions/{id}/run`), útil para el reto extra de quien quiera ir
más allá.

## Bug real encontrado al probarlo: la URL de Groq

La documentación de ether-brain (`docs/proveedores.md`) lista:

```
LLM_URL=https://api.groq.com
```

Al probarlo en vivo, esa URL produce error:

```
HTTP 404: {"error":{"message":"Unknown request URL: POST /v1/chat/completions ..."}}
```

La API real de Groq vive bajo el prefijo `/openai`:

```bash
curl -X POST https://api.groq.com/v1/chat/completions          # 404
curl -X POST https://api.groq.com/openai/v1/chat/completions   # 401 (URL correcta, falta auth)
```

La URL correcta es:

```
LLM_URL=https://api.groq.com/openai
```

`OpenAiCodec.endpoint()` en ether-brain ya soporta este caso (su propio
javadoc documenta el patrón `https://my-proxy.com/openai →
.../openai/v1/chat/completions`), así que no hace falta ningún cambio de
código — solo corregir el ejemplo en la documentación. Es el valor que
usa este proyecto en [`secrets/groq.example.env`](../secrets/groq.example.env).

Este es exactamente el tipo de cosa que conviene descubrir probando en
vivo antes de un taller, no durante: una URL "casi correcta" en la
documentación de una herramienta de terceros puede costarte 10 minutos de
debugging en vivo frente a 30 asistentes.

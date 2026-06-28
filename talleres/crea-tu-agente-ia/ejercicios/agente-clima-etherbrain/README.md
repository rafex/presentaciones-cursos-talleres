# agente-clima-etherbrain

Primer ejercicio del taller **"Cómo crear tu propio agente de IA usando solo
software libre"** (Foro de Tecnologías de la Información y Software Libre
2026, UPTLAX).

Un agente que responde "¿qué clima hay en \<ciudad\>?" encadenando dos
herramientas públicas (geocodificación + clima), corriendo sobre
[ether-brain](https://github.com/rafex/ether-brain) — un runtime de agentes
en **Java**, sin frameworks pesados — con **Groq** como proveedor del LLM.

A diferencia del otro proyecto del taller ([`agente-cp`](../agente-cp), en
Python/LangGraph), aquí **no se escribe ningún código**: las tools se
declaran en un `tools.json` y ether-brain las descubre solo. Es el ejemplo
más simple posible de "MCP/tools para que el agente resuelva problemas".

## 0. ether-brain no está en Maven Central — se compila desde el código

```bash
git clone https://github.com/rafex/ether-brain
cd ether-brain/ether-brain
./mvnw -q -pl ether-brain-transport-cli -am package -DskipTests
```

Esto genera `ether-brain-transport-cli/target/ether-brain-cli.jar` (fat jar,
~2.5 MB). Guarda la ruta — la usamos en todos los comandos de abajo.

```bash
export ETHER_BRAIN_JAR=/ruta/a/ether-brain/ether-brain/ether-brain-transport-cli/target/ether-brain-cli.jar
```

## 1. Las tools: `tools.json`

Dos tools tipo `"http"` (ether-brain las reenvía como GET con los
argumentos del modelo como query params — cero código):

- `geocodificar_ciudad` → [Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api) (nombre de ciudad → lat/lon)
- `clima_actual` → [Open-Meteo Forecast](https://open-meteo.com/en/docs) (lat/lon → clima actual)

Ambas son APIs públicas, sin API key. Ver [`tools.json`](./tools.json) y el
detalle en [`docs/tools.md`](./docs/tools.md).

Probar que cargan, sin gastar ninguna llamada a Groq (modo demo, sin LLM real):

```bash
cd agente-clima-etherbrain
LLM_TYPE=demo java -jar "$ETHER_BRAIN_JAR" "hola"
# debe imprimir: [EtherBrain] 2 tool(s) externas cargadas desde tools.json
```

## 2. El secreto: age + sops, no `.env` en texto plano

`LLM_TOKEN` (tu API key de Groq) nunca se escribe sin cifrar dentro del
repo. Se cifra con [age](https://github.com/FiloSottile/age) (llaves
simples, sin infraestructura) a través de [sops](https://github.com/getsops/sops)
(cifra solo los *valores* de un archivo, las claves quedan legibles).

```bash
# 1. Genera tu llave age una sola vez (privada -- NUNCA va al repo)
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
# imprime algo como: Public key: age1...

# 2. Pon esa clave publica en .sops.yaml (ya tiene la del taller; agrega la tuya)
#    .sops.yaml -> creation_rules -> age: age1...

# 3. Copia la plantilla y pon tu API key real de https://console.groq.com/keys
cp secrets/groq.example.env secrets/groq.enc.env
$EDITOR secrets/groq.enc.env

# 4. Cifra in-place -- a partir de aqui el archivo es seguro de commitear
sops --encrypt --in-place secrets/groq.enc.env
```

`secrets/groq.enc.env` cifrado se ve así (los valores son ilegibles, las
claves no):

```
LLM_TOKEN=ENC[AES256_GCM,data:JPYSnVCI...,iv:...,tag:...,type:str]
```

## 3. Correr el agente

```bash
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt   # portable Linux/macOS

sops exec-env secrets/groq.enc.env \
  "java -jar $ETHER_BRAIN_JAR '¿qué clima hay en Tlaxcala?'"
```

`sops exec-env` descifra el archivo en memoria, exporta cada clave como
variable de entorno **solo para el proceso hijo**, y nunca escribe el
secreto en disco sin cifrar. ether-brain arranca, descubre las 2 tools,
y el modelo decide encadenarlas: primero `geocodificar_ciudad("Tlaxcala")`,
luego `clima_actual(lat, lon)` con el resultado.

## Estructura

```
tools.json              # las 2 tools http -- sin código
.sops.yaml               # qué llaves age pueden descifrar qué archivos
secrets/
  groq.example.env        # plantilla sin secretos, segura de commitear
  groq.enc.env             # tu secreto real, cifrado con sops -- sí se commitea así
docs/
  tools.md                  # cómo funciona el tipo "http" de ether-brain
  secretos.md                # age + sops explicado a fondo
```

## Reto extra

Agrega una tercera tool (otra API pública sin key) y haz que el agente la
encadene con las dos anteriores -- por ejemplo, una API de pronóstico a
varios días, o una que sugiera actividades según la temperatura.

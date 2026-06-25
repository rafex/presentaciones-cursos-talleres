#!/usr/bin/env bash
# Prueba agente-clima-etherbrain: el mismo ciclo de tool-calling, pero sin
# escribir codigo -- las tools se declaran en tools.json y corren sobre
# ether-brain (runtime de agentes en Java). Ya no esta en la presentacion
# actual, pero sigue siendo parte del repo.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

DIR_AGENTE="$DIR_TALLER/agente-clima-etherbrain"

# Busca el jar en ETHER_BRAIN_JAR, o en un par de rutas comunes donde
# alguien pudo haber clonado y compilado ether-brain.
localizar_jar() {
    if [ -n "${ETHER_BRAIN_JAR:-}" ] && [ -f "$ETHER_BRAIN_JAR" ]; then
        echo "$ETHER_BRAIN_JAR"
        return 0
    fi
    local candidato
    for candidato in \
        "$DIR_TALLER/../ether-brain/ether-brain/ether-brain-transport-cli/target/ether-brain-cli.jar" \
        "/private/tmp/ether-brain/ether-brain/ether-brain-transport-cli/target/ether-brain-cli.jar"
    do
        [ -f "$candidato" ] && { echo "$candidato"; return 0; }
    done
    return 1
}

titulo "agente-clima-etherbrain: tools.json sin codigo, sobre ether-brain (Java)"

if ! command -v java >/dev/null 2>&1; then
    advertencia "java no esta instalado -- instala Java 21+ para correr este agente"
    exit 0
fi

jar="$(localizar_jar)" || {
    advertencia "no encontre ether-brain-cli.jar. Para compilarlo:"
    echo "    git clone https://github.com/rafex/ether-brain"
    echo "    cd ether-brain/ether-brain"
    echo "    ./mvnw -q -pl ether-brain-transport-cli -am package -DskipTests"
    echo "  y exporta ETHER_BRAIN_JAR=/ruta/al/ether-brain-cli.jar"
    exit 0
}

paso "cd agente-clima-etherbrain && LLM_TYPE=demo java -jar $jar 'hola'"
(cd "$DIR_AGENTE" && LLM_TYPE=demo java -jar "$jar" "hola")

archivo_cifrado="$DIR_AGENTE/secrets/groq.enc.env"

if ! command -v sops >/dev/null 2>&1; then
    advertencia "sops no esta instalado -- me quedo con la prueba en modo demo de arriba"
    exit 0
fi
if [ ! -f "$archivo_cifrado" ]; then
    advertencia "no encontre $archivo_cifrado -- me quedo con la prueba en modo demo de arriba"
    exit 0
fi

paso "cd agente-clima-etherbrain && sops exec-env secrets/groq.enc.env \"java -jar $jar '¿qué clima hay en Tlaxcala?'\""
if ! (cd "$DIR_AGENTE" && sops exec-env secrets/groq.enc.env "java -jar $jar '¿qué clima hay en Tlaxcala?'"); then
    advertencia "la corrida real contra Groq fallo -- revisa que secrets/groq.enc.env tenga una LLM_TOKEN valida"
    exit 0
fi

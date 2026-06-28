#!/usr/bin/env bash
# Administra GROQ_BASE_URL y GROQ_MODEL (config no secreta, va en .env,
# no en secrets/) para los agentes de agente-mini-python.
#
# Uso:
#   ./scripts/configurar_env.sh crear              # crea/actualiza el .env de cada agente
#   source scripts/configurar_env.sh cargar         # exporta esas variables al shell actual
#
# El modo "cargar" tiene que invocarse con 'source' (o '.') -- si lo
# ejecutas normalmente (./scripts/...), las variables se exportan en un
# proceso hijo que termina de inmediato y no le sirven a tu shell.
set -euo pipefail

GROQ_BASE_URL_DEFAULT="https://api.groq.com/openai/v1"
GROQ_MODEL_DEFAULT="openai/gpt-oss-120b"

AGENTES=(agente-sin-tool agente-clima agente-pokemon agente-consejos agente-orquestador llm-directo)

# resolver la ruta del script funciona igual si se ejecuta o si se hace 'source'
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    DIR_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    DIR_SCRIPT="$(cd "$(dirname "$0")" && pwd)"
fi
DIR_RAIZ="$(cd "$DIR_SCRIPT/.." && pwd)"

fallar() {
    echo "Error: $1" >&2
    return 1
}

# Asegura que CLAVE=VALOR exista en el archivo $1 -- si la clave ya
# existe (con cualquier valor) no la toca; si no existe, la agrega.
asegurar_variable() {
    local archivo="$1" clave="$2" valor_default="$3"
    if grep -q "^${clave}=" "$archivo" 2>/dev/null; then
        return 0
    fi
    printf '%s=%s\n' "$clave" "$valor_default" >> "$archivo"
}

modo_crear() {
    echo "Configurando GROQ_BASE_URL y GROQ_MODEL en el .env de cada agente..."
    echo

    for agente in "${AGENTES[@]}"; do
        local_dir="$DIR_RAIZ/$agente"
        archivo_env="$local_dir/.env"
        archivo_ejemplo="$local_dir/.env.example"
        archivo_gitignore="$local_dir/.gitignore"

        [ -d "$local_dir" ] || { echo "  (omitido) $agente no existe"; continue; }

        if ! grep -q '^\.env$' "$archivo_gitignore" 2>/dev/null; then
            echo "  Aviso: $archivo_gitignore no tiene una línea '.env' -- agregándola."
            printf '.env\n' >> "$archivo_gitignore"
        fi

        if [ ! -f "$archivo_env" ]; then
            if [ -f "$archivo_ejemplo" ]; then
                cp "$archivo_ejemplo" "$archivo_env"
            else
                touch "$archivo_env"
            fi
            echo "  $agente/.env creado"
        fi

        asegurar_variable "$archivo_env" "GROQ_BASE_URL" "$GROQ_BASE_URL_DEFAULT"
        asegurar_variable "$archivo_env" "GROQ_MODEL" "$GROQ_MODEL_DEFAULT"
        asegurar_variable "$archivo_env" "GROQ_API_KEY" "gsk_REEMPLAZA_CON_TU_API_KEY_REAL"

        echo "  $agente/.env listo:"
        sed 's/^/    /' "$archivo_env"
        echo
    done

    echo "GROQ_API_KEY queda como placeholder en .env -- usa ./scripts/configurar_secreto.sh"
    echo "para manejar la API key real de forma cifrada (age + sops), no en texto plano."
}

modo_cargar() {
    local agente_actual archivo_env
    agente_actual="$(basename "$PWD")"
    archivo_env="$PWD/.env"

    if [[ ! " ${AGENTES[*]} " == *" $agente_actual "* ]]; then
        echo "Aviso: '$agente_actual' no es una carpeta de agente conocida." >&2
        echo "Corre esto desde dentro de agente-clima/, agente-pokemon/, etc." >&2
    fi

    [ -f "$archivo_env" ] || { fallar "no encontré $archivo_env -- corre primero 'configurar_env.sh crear'"; return 1; }

    set -a
    # shellcheck disable=SC1090
    source "$archivo_env"
    set +a

    echo "Variables cargadas en este shell desde $archivo_env:"
    echo "  GROQ_BASE_URL=${GROQ_BASE_URL:-}"
    echo "  GROQ_MODEL=${GROQ_MODEL:-}"
    if [ -n "${GROQ_API_KEY:-}" ]; then
        echo "  GROQ_API_KEY=(definida, oculta)"
    else
        echo "  GROQ_API_KEY=(vacía)"
    fi
}

modo="${1:-}"

case "$modo" in
    crear)
        modo_crear
        ;;
    cargar)
        if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
            echo "Aviso: este modo necesita 'source', si no las variables no le quedan a tu shell." >&2
            echo "Usa:  source scripts/configurar_env.sh cargar" >&2
        fi
        modo_cargar
        ;;
    *)
        echo "Uso:"
        echo "  $0 crear              -- crea/actualiza el .env de cada agente"
        echo "  source $0 cargar      -- exporta esas variables al shell actual (desde dentro de una carpeta de agente)"
        return 1 2>/dev/null || exit 1
        ;;
esac

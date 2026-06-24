#!/usr/bin/env bash
# Funciones compartidas por los demas scripts de tests/.
# No se ejecuta solo -- cada test_*.sh hace `source commons.sh`.

DIR_TESTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR_AGENTES="$(cd "$DIR_TESTS/../agente-mini-python" && pwd)"

AZUL=$'\033[0;34m'
AMARILLO=$'\033[1;33m'
ROJO=$'\033[0;31m'
SIN_COLOR=$'\033[0m'

titulo() {
    echo
    echo "${AZUL}== $1 ==${SIN_COLOR}"
}

paso() {
    echo "${AMARILLO}-> $1${SIN_COLOR}"
}

error() {
    echo "${ROJO}[ERROR] $1${SIN_COLOR}" >&2
}

verificar_uv() {
    command -v uv >/dev/null 2>&1 || { error "uv no esta instalado -- ver https://docs.astral.sh/uv/"; exit 1; }
}

# Corre un agente desde su propia carpeta y muestra el comando antes de
# ejecutarlo, igual que lo verias copiando y pegando en tu terminal.
# Uso: correr_agente <carpeta-del-agente> <script.py> <pregunta...>
correr_agente() {
    local carpeta="$1" script="$2"
    shift 2
    local pregunta="$*"

    paso "cd agente-mini-python/$carpeta && uv run $script \"$pregunta\""
    (cd "$DIR_AGENTES/$carpeta" && uv run "$script" "$pregunta")
}

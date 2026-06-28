#!/usr/bin/env bash
# Prueba agente-clima: dos tools encadenadas (geocodificar -> clima actual).
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

titulo "agente-clima: dos tools encadenadas (geocodificar -> clima)"
verificar_uv

correr_agente "agente-clima" "clima.py" "¿que clima hay en Tlaxcala?"

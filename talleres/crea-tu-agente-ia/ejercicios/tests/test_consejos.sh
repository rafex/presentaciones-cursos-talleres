#!/usr/bin/env bash
# Prueba agente-consejos: una tool con argumento opcional (busqueda por
# palabra clave) y otra sin argumentos (consejo al azar).
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

titulo "agente-consejos: tool con busqueda por palabra clave"
verificar_uv

correr_agente "agente-consejos" "consejos.py" "dame un consejo sobre el amor"
echo
correr_agente "agente-consejos" "consejos.py" "dame un consejo al azar"

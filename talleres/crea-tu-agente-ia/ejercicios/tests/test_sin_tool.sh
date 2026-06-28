#!/usr/bin/env bash
# Prueba agente-sin-tool: el mismo modelo, sin ninguna tool conectada.
# Es el control del experimento -- ver test_pokemon.sh para el contraste.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

titulo "agente-sin-tool: el LLM puro, sin ninguna tool"
verificar_uv

correr_agente "agente-sin-tool" "sin_tool.py" "¿cuanto pesa pikachu?"

#!/usr/bin/env bash
# Prueba agente-pokemon: el mismo modelo, con una tool conectada a PokeAPI.
# Corre la misma pregunta que test_sin_tool.sh -- compara las dos respuestas.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

titulo "agente-pokemon: el LLM + una tool conectada a PokeAPI"
verificar_uv

correr_agente "agente-pokemon" "pokemon.py" "¿cuanto pesa pikachu?"
echo
correr_agente "agente-pokemon" "pokemon.py" "¿de que tipo es charizard?"

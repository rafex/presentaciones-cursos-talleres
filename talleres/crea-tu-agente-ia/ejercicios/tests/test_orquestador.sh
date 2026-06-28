#!/usr/bin/env bash
# Prueba agente-orquestador: las tools de clima, pokemon y consejos juntas
# en una sola lista -- el modelo decide cual o cuales necesita.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

titulo "agente-orquestador: el modelo elige entre varias tools a la vez"
verificar_uv

correr_agente "agente-orquestador" "orquestador.py" "¿que clima hay en Tlaxcala y cuanto pesa pikachu?"

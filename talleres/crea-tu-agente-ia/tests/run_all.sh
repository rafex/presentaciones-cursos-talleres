#!/usr/bin/env bash
# Corre todos los tests en el mismo orden que cuenta la presentacion:
# primero el control (sin tool), despues cada agente con tool, al final el
# orquestador que los combina.
set -euo pipefail
DIR_TESTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR_TESTS/commons.sh"

verificar_uv

for script in test_sin_tool.sh test_pokemon.sh test_clima.sh test_consejos.sh test_orquestador.sh; do
    bash "$DIR_TESTS/$script"
done

titulo "Listo"
echo "Los 5 agentes corrieron. Compara la respuesta de agente-sin-tool contra"
echo "la de agente-pokemon para la misma pregunta -- esa diferencia es el"
echo "punto del taller."

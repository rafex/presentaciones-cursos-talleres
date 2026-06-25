#!/usr/bin/env bash
# Corre todos los tests: primero los scripts de agente-mini-python, en
# el orden que cuenta la presentacion (POST a mano -> control sin tool ->
# cada agente con tool -> orquestador), y al final los dos ejercicios que ya no estan en
# la presentacion pero siguen en el repo (ether-brain y agente-cp). Estos
# dos ultimos pueden quedar en [SKIP] si falta una dependencia externa
# (el jar de ether-brain, o una GROQ_API_KEY para agente-cp) -- no es un
# error, solo significa que esta maquina no los tiene configurados.
set -euo pipefail
DIR_TESTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR_TESTS/commons.sh"

verificar_uv

for script in test_llm_directo.sh test_sin_tool.sh test_pokemon.sh test_clima.sh test_consejos.sh test_orquestador.sh test_etherbrain.sh test_agente_cp.sh; do
    bash "$DIR_TESTS/$script"
done

titulo "Listo"
echo "Los scripts de agente-mini-python corrieron. Compara la respuesta de"
echo "llm-directo y agente-sin-tool contra la de agente-pokemon para la"
echo "misma pregunta -- esa diferencia es el punto del taller."

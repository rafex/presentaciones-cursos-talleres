#!/usr/bin/env bash
# Prueba agente-cp: LangGraph + MCP + SEPOMEX. El ejercicio mas avanzado
# del taller -- ya no esta en la presentacion actual, pero sigue siendo
# parte del repo.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

DIR_AGENTE="$DIR_TALLER/agente-cp"

titulo "agente-cp: LangGraph + MCP + SEPOMEX"
verificar_uv

paso "cd agente-cp && uv sync"
(cd "$DIR_AGENTE" && uv sync --quiet)

paso "buscar_por_cp('90001', 'Tlaxcala') directo contra el sqlite, sin LLM"
(cd "$DIR_AGENTE" && uv run python3 -c "
from agente_cp.sepomex import buscar_por_cp
coincidencias, origen = buscar_por_cp('90001', 'Tlaxcala')
print(f'origen_datos={origen}')
for asentamiento in coincidencias[:3]:
    print(f'  {asentamiento.colonia} ({asentamiento.tipo}) -- {asentamiento.municipio}')
")

archivo_env="$DIR_AGENTE/.env"
tiene_key=0
if [ -n "${GROQ_API_KEY:-}" ]; then
    tiene_key=1
elif [ -f "$archivo_env" ] && grep -q '^GROQ_API_KEY=gsk_' "$archivo_env" \
        && ! grep -q '^GROQ_API_KEY=gsk_tu_api_key' "$archivo_env"; then
    tiene_key=1
fi

if [ "$tiene_key" -ne 1 ]; then
    advertencia "no encontre GROQ_API_KEY (ni exportada ni en agente-cp/.env) -- omito la corrida con LLM"
    echo "    cp agente-cp/.env.example agente-cp/.env"
    echo "    \$EDITOR agente-cp/.env   # pega tu key de https://console.groq.com/keys"
    exit 0
fi

paso 'cd agente-cp && uv run agente-cp "¿La colonia Tlaxcala Centro corresponde al CP 90001?"'
if ! (cd "$DIR_AGENTE" && uv run agente-cp "¿La colonia Tlaxcala Centro corresponde al CP 90001?"); then
    advertencia "la corrida real contra Groq fallo -- revisa que GROQ_API_KEY sea valida"
    exit 0
fi

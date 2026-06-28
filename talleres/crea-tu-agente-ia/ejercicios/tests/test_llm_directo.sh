#!/usr/bin/env bash
# Prueba llm-directo: ni SDK, ni tools, ni ciclo de agente -- un POST a
# mano contra el endpoint de chat completions de Groq. Sirve para
# contrastar contra agente-sin-tool (que ya usa el SDK de openai) y
# agente-pokemon (SDK + ciclo de tool-calling).
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/commons.sh"

titulo "llm-directo: el mismo LLM, sin SDK y sin framework de agentes"
verificar_uv

correr_agente "llm-directo" "llm_directo.py" "¿que es un agente de IA en una frase?"

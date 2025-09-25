#!/usr/bin/env bash
set -euo pipefail

# Activar entorno virtual
if [[ -d ".venv" ]]; then
  source .venv/bin/activate
  pip install --upgrade pip
else
  echo "❌ Entorno virtual .venv no encontrado. Crea uno con: python3 -m venv .venv"
  exit 1
fi

# Instalar dependencias si existe requirements.txt
if [[ -f "requirements.txt" ]]; then
  echo "📦 Instalando dependencias de requirements.txt..."
  pip install -r requirements.txt
fi

# Ejecutar el script Python con los argumentos que reciba
./generate_qr.py "$@"
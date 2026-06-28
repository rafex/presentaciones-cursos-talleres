#!/usr/bin/env bash
#
# Resuelve el nombre de una presentación o taller a su ruta absoluta,
# buscando en presentaciones/ y talleres/. Si el mismo nombre existe en
# ambas carpetas, exige desambiguar con -t/--type.
#
# Uso:
#   ./scripts/resolve-target.sh <nombre> [-t|--type presentation|taller]
#
# Imprime la ruta absoluta resuelta en stdout. Cualquier mensaje informativo
# o de error va a stderr, para poder hacer `dir=$(resolve-target.sh ...)`.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat >&2 <<EOF
Uso: $(basename "$0") <nombre> [-t|--type presentation|taller]
EOF
  exit 1
}

NAME=""
TYPE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--type)
      [[ $# -ge 2 ]] || usage
      TYPE="$2"
      shift 2
      ;;
    -t=*|--type=*)
      TYPE="${1#*=}"
      shift
      ;;
    -*)
      echo "Error: opción desconocida '$1'." >&2
      usage
      ;;
    *)
      if [[ -z "$NAME" ]]; then
        NAME="$1"
      else
        echo "Error: argumento inesperado '$1'." >&2
        usage
      fi
      shift
      ;;
  esac
done

[[ -n "$NAME" ]] || usage

normalize_type() {
  case "$1" in
    p|presentation|presentacion|presentaciones) echo "presentation" ;;
    t|taller|talleres|workshop) echo "taller" ;;
    "") echo "" ;;
    *)
      echo "Error: --type debe ser 'presentation' o 'taller' (recibido: '$1')." >&2
      exit 1
      ;;
  esac
}

TYPE="$(normalize_type "$TYPE")"

PRES_PATH="$REPO_ROOT/presentaciones/$NAME"
TALLER_PATH="$REPO_ROOT/talleres/$NAME"
PRES_EXISTS=0; [[ -d "$PRES_PATH" ]] && PRES_EXISTS=1
TALLER_EXISTS=0; [[ -d "$TALLER_PATH" ]] && TALLER_EXISTS=1

if [[ -n "$TYPE" ]]; then
  if [[ "$TYPE" == "presentation" ]]; then
    [[ "$PRES_EXISTS" -eq 1 ]] || { echo "Error: no existe la presentación '$NAME' en presentaciones/." >&2; exit 1; }
    echo "$PRES_PATH"
  else
    [[ "$TALLER_EXISTS" -eq 1 ]] || { echo "Error: no existe el taller '$NAME' en talleres/." >&2; exit 1; }
    echo "$TALLER_PATH"
  fi
  exit 0
fi

if [[ "$PRES_EXISTS" -eq 1 && "$TALLER_EXISTS" -eq 1 ]]; then
  echo "Error: '$NAME' existe tanto en presentaciones/ como en talleres/. Especifica -t/--type presentation|taller." >&2
  exit 1
elif [[ "$PRES_EXISTS" -eq 1 ]]; then
  echo "$PRES_PATH"
elif [[ "$TALLER_EXISTS" -eq 1 ]]; then
  echo "$TALLER_PATH"
else
  echo "Error: no se encontró '$NAME' ni en presentaciones/ ni en talleres/." >&2
  exit 1
fi

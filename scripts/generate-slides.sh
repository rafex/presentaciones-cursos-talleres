#!/usr/bin/env bash
#
# Genera PDF/ODP a partir de los .md de una carpeta de presentación o taller,
# usando el Marp CLI instalado en presentaciones/node_modules (no se duplica
# por carpeta). Pensado para invocarse vía `just generate ...`.
#
# Uso:
#   ./scripts/generate-slides.sh <carpeta> [pdf|odp|all]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MARPCLI="$REPO_ROOT/presentaciones/node_modules/.bin/marp"

usage() {
  cat >&2 <<EOF
Uso: $(basename "$0") <carpeta> [pdf|odp|all]
EOF
  exit 1
}

[[ $# -ge 1 ]] || usage

INPUT_DIR="$1"
FORMAT_ARG="${2:-all}"

if [[ -d "$INPUT_DIR" ]]; then
  TARGET_DIR="$(cd "$INPUT_DIR" && pwd)"
elif [[ -d "$REPO_ROOT/$INPUT_DIR" ]]; then
  TARGET_DIR="$(cd "$REPO_ROOT/$INPUT_DIR" && pwd)"
else
  echo "Error: no existe la carpeta '$INPUT_DIR'." >&2
  exit 1
fi

if [[ ! -x "$MARPCLI" ]]; then
  echo "Error: no se encontró Marp CLI en $MARPCLI. Ejecuta 'npm install' dentro de presentaciones/." >&2
  exit 1
fi

case "$FORMAT_ARG" in
  pdf|odp) formats=("$FORMAT_ARG") ;;
  all) formats=(pdf odp) ;;
  *)
    echo "Aviso: formato desconocido '$FORMAT_ARG'. Usando 'pdf' y 'odp'." >&2
    formats=(pdf odp)
    ;;
esac

md_files=("$TARGET_DIR"/*.md)
if [[ ! -e "${md_files[0]}" ]]; then
  echo "Error: no hay archivos .md en '$TARGET_DIR'." >&2
  exit 1
fi

theme="$TARGET_DIR/assets/css/theme.css"
GENERATED=0
for md in "${md_files[@]}"; do
  base="${md##*/}"
  name="${base%.*}"
  for fmt in "${formats[@]}"; do
    [[ -f "$theme" ]] || { echo "  → No se encontró $theme, salteando $md."; continue; }
    out="$TARGET_DIR/${name}.${fmt}"
    echo "Generando $out..."
    "$MARPCLI" "$md" --theme "$theme" --allow-local-files -o "$out"
    GENERATED=1
  done
done

[[ "$GENERATED" -eq 1 ]] || echo "Aviso: no se generó ningún archivo (¿falta assets/css/theme.css?)." >&2

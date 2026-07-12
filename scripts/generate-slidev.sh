#!/usr/bin/env bash
#
# Ejecuta o exporta un proyecto Slidev de forma opt-in. El flujo Marp de
# generate-slides.sh sigue siendo el predeterminado para PDF/ODP y releases.
#
# Uso:
#   ./scripts/generate-slidev.sh <slides.md> dev
#   ./scripts/generate-slidev.sh <slides.md> pdf|pptx|png|md
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SLIDEV="$REPO_ROOT/presentaciones/node_modules/.bin/slidev"

usage() {
  cat >&2 <<EOF
Uso: $(basename "$0") <slides.md> dev|pdf|pptx|png|md
EOF
  exit 1
}

[[ $# -ge 1 ]] || usage
SOURCE="$1"
MODE="${2:-dev}"

if [[ -f "$SOURCE" ]]; then
  SLIDES_FILE="$(cd "$(dirname "$SOURCE")" && pwd)/$(basename "$SOURCE")"
elif [[ -f "$REPO_ROOT/$SOURCE" ]]; then
  SLIDES_FILE="$(cd "$REPO_ROOT/$(dirname "$SOURCE")" && pwd)/$(basename "$SOURCE")"
else
  echo "Error: no existe el archivo Slidev '$SOURCE'." >&2
  exit 1
fi

if [[ ! -x "$SLIDEV" ]]; then
  echo "Error: no se encontró Slidev en $SLIDEV. Ejecuta 'npm install' dentro de presentaciones/." >&2
  exit 1
fi

PROJECT_DIR="$(dirname "$SLIDES_FILE")"
SLIDES_NAME="$(basename "$SLIDES_FILE")"
SLIDES_STEM="${SLIDES_NAME%.*}"

case "$MODE" in
  dev)
    cd "$PROJECT_DIR"
    exec "$SLIDEV" "$SLIDES_NAME"
    ;;
  pdf|pptx|png|md)
    OUT_DIR="$REPO_ROOT/dist/slidev"
    mkdir -p "$OUT_DIR"
    if [[ "$MODE" == "png" ]]; then
      OUT="$OUT_DIR/${SLIDES_STEM}-png"
    else
      OUT="$OUT_DIR/${SLIDES_STEM}.${MODE}"
    fi
    echo "Generando $OUT..."
    cd "$PROJECT_DIR"
    "$SLIDEV" export "$SLIDES_NAME" --format "$MODE" --output "$OUT"
    echo "✅ Exportación Slidev generada: $OUT"
    ;;
  *)
    usage
    ;;
esac

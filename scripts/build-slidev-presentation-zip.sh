#!/usr/bin/env bash
#
# Empaqueta un proyecto Slidev transportable para InsightBloom.
# El ZIP conserva la fuente Slidev y una build estática de Slidev; no lo
# convierte a Marp ni a una colección de imágenes.
#
# Uso:
#   ./scripts/build-slidev-presentation-zip.sh <slides.md> [salida.zip]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SLIDEV="$REPO_ROOT/presentaciones/node_modules/.bin/slidev"
ROOT_PACKAGE="$REPO_ROOT/presentaciones/package.json"

usage() {
  cat >&2 <<EOF
Uso: $(basename "$0") <slides.md> [salida.zip]

  <slides.md>       Archivo Slidev. Puede ser relativo al repo o absoluto.
  [salida.zip]      ZIP de salida. Por defecto: dist/<presentacion>-slidev.zip
EOF
  exit 1
}

[[ $# -ge 1 ]] || usage
SOURCE="$1"
OUT_ARG="${2:-}"

if [[ -f "$SOURCE" ]]; then
  SLIDES_FILE="$(cd "$(dirname "$SOURCE")" && pwd)/$(basename "$SOURCE")"
elif [[ -f "$REPO_ROOT/$SOURCE" ]]; then
  SLIDES_FILE="$(cd "$REPO_ROOT/$(dirname "$SOURCE")" && pwd)/$(basename "$SOURCE")"
else
  echo "Error: no existe el archivo Slidev '$SOURCE'." >&2
  exit 1
fi

[[ -x "$SLIDEV" ]] || {
  echo "Error: no se encontró Slidev en $SLIDEV. Ejecuta 'npm install --prefix presentaciones'." >&2
  exit 1
}
[[ -f "$ROOT_PACKAGE" ]] || {
  echo "Error: no se encontró $ROOT_PACKAGE." >&2
  exit 1
}

PROJECT_DIR="$(dirname "$SLIDES_FILE")"
SLIDES_NAME="$(basename "$SLIDES_FILE")"
PROJECT_NAME="$(basename "$PROJECT_DIR")"
[[ "$PROJECT_NAME" == "slidev" ]] && PROJECT_NAME="$(basename "$(dirname "$PROJECT_DIR")")"

SLIDEV_VERSION="$(node -p "require('$ROOT_PACKAGE').devDependencies['@slidev/cli']")"
SERIPH_VERSION="$(node -p "require('$ROOT_PACKAGE').devDependencies['@slidev/theme-seriph']")"
PLAYWRIGHT_VERSION="$(node -p "require('$ROOT_PACKAGE').devDependencies['playwright-chromium']")"

STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT
mkdir -p "$STAGING/source" "$STAGING/dist"

echo "📦 Copiando fuente Slidev..."

# Copiar el proyecto sin caches ni dependencias instaladas. El enlace public
# del repositorio se materializa como una carpeta real dentro del ZIP.
while IFS= read -r entry; do
  name="$(basename "$entry")"
  case "$name" in
    node_modules|.slidev|dist|.git|.DS_Store) continue ;;
  esac
  if [[ "$name" == "public" ]]; then
    mkdir -p "$STAGING/source/public"
    cp -R "$PROJECT_DIR/public/." "$STAGING/source/public/"
  else
    cp -R "$entry" "$STAGING/source/"
  fi
done < <(find "$PROJECT_DIR" -mindepth 1 -maxdepth 1 -print | sort)

cat > "$STAGING/source/package.json" <<EOF
{
  "name": "${PROJECT_NAME}-slidev",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "slidev ${SLIDES_NAME}",
    "build": "slidev build ${SLIDES_NAME}",
    "export": "slidev export ${SLIDES_NAME}"
  },
  "dependencies": {
    "@slidev/cli": "${SLIDEV_VERSION}",
    "@slidev/theme-seriph": "${SERIPH_VERSION}",
    "playwright-chromium": "${PLAYWRIGHT_VERSION}"
  }
}
EOF

cat > "$STAGING/slidev.project.json" <<EOF
{
  "format": "slidev",
  "formatVersion": 1,
  "entry": "${SLIDES_NAME}",
  "sourceDir": "source",
  "staticDir": "dist",
  "packageManager": "npm",
  "buildCommand": "npm run build"
}
EOF

echo "🏗️  Generando build estática Slidev..."
(
  cd "$PROJECT_DIR"
  "$SLIDEV" build "$SLIDES_NAME" --out "$STAGING/dist" --base ./
)

[[ -f "$STAGING/dist/index.html" ]] || {
  echo "Error: Slidev no produjo dist/index.html." >&2
  exit 1
}

cat > "$STAGING/README.md" <<EOF
# ${PROJECT_NAME}

Paquete Slidev transportable.

- Fuente: source/${SLIDES_NAME}
- Manifiesto: slidev.project.json
- Build estática lista para servir: dist/index.html
- Para reconstruir: cd source && npm install && npm run build
EOF

OUT_DIR="$REPO_ROOT/dist"
mkdir -p "$OUT_DIR"
OUT_ZIP="${OUT_ARG:-$OUT_DIR/${PROJECT_NAME}-slidev.zip}"
[[ "$OUT_ZIP" = /* ]] || OUT_ZIP="$PWD/$OUT_ZIP"
mkdir -p "$(dirname "$OUT_ZIP")"
rm -f "$OUT_ZIP"
(cd "$STAGING" && zip -rq "$OUT_ZIP" .)

SIZE_HUMAN="$(du -h "$OUT_ZIP" | cut -f1)"
echo "✅ ZIP Slidev transportable: $OUT_ZIP ($SIZE_HUMAN)"
echo
echo "Contenido: source/ + dist/index.html + slidev.project.json"
echo "Subir con curl:"
echo "  curl -F file=@\"$OUT_ZIP\" https://insightbloom.v1.rafex.cloud/api/presentations/api/v1/conferences/{conferenceId}/presentation"

#!/bin/bash

# build-slidev-insightbloom-fat-zip.sh
# 
# Genera un paquete ZIP FAT para InsightBloom con dist/ compilado, manifiesto y hashes.
# 
# Uso:
#   ./build-slidev-insightbloom-fat-zip.sh <nombre-o-ruta> [-t tipo] [salida.zip]
#
# Ejemplos:
#   ./build-slidev-insightbloom-fat-zip.sh slidev-en-10-minutos
#   ./build-slidev-insightbloom-fat-zip.sh slidev-en-10-minutos -t presentation dist/custom.zip
#   ./build-slidev-insightbloom-fat-zip.sh presentaciones/mi-presentacion/slidev

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de ayuda
die() {
  echo -e "${RED}❌ Error: $*${NC}" >&2
  exit 1
}

info() {
  echo -e "${GREEN}✓ $*${NC}"
}

warn() {
  echo -e "${YELLOW}⚠ $*${NC}"
}

# Obtener versión de Slidev
get_slidev_version() {
  local npm_cmd="$1"
  if [[ -f "package.json" ]]; then
    $npm_cmd list @slidev/cli 2>/dev/null | grep @slidev/cli | head -1 | sed 's/.*@slidev\/cli@//' | sed 's/ .*//' || echo "unknown"
  else
    echo "unknown"
  fi
}

# Generar SHA256 de un archivo
get_file_hash() {
  local file="$1"
  if [[ -f "$file" ]]; then
    sha256sum "$file" | awk '{print $1}'
  else
    echo ""
  fi
}

# Parsear argumentos
FIRST_ARG="${1:-}"
TYPE=""
OUTPUT_ZIP=""
shift || true

# Procesar argumentos restantes
while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--type)
      TYPE="$2"
      shift 2
      ;;
    *)
      # Si es .zip, es OUTPUT_ZIP; si no, error
      if [[ "$1" == *.zip ]]; then
        OUTPUT_ZIP="$1"
        shift
      else
        die "Argumento desconocido: $1"
      fi
      ;;
  esac
done

[[ -n "$FIRST_ARG" ]] || die "Uso: $0 <nombre-o-ruta> [-t tipo] [salida.zip]"

# Detectar si es nombre (sin /) o ruta completa
if [[ "$FIRST_ARG" == */* ]]; then
  # Es una ruta (completa o relativa)
  if [[ -d "$FIRST_ARG" ]]; then
    PROJECT_DIR="$(cd "$FIRST_ARG" && pwd)"
  elif [[ -d "$REPO_ROOT/$FIRST_ARG" ]]; then
    PROJECT_DIR="$(cd "$REPO_ROOT/$FIRST_ARG" && pwd)"
  else
    die "Ruta no encontrada: $FIRST_ARG"
  fi
  NAME=$(basename "$PROJECT_DIR" | sed 's/\.md$//')
else
  # Es un nombre, resolver con resolve-target.sh
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  
  if [[ -n "$TYPE" ]]; then
    TARGET_DIR=$("$SCRIPT_DIR/resolve-target.sh" "$FIRST_ARG" -t "$TYPE")
  else
    TARGET_DIR=$("$SCRIPT_DIR/resolve-target.sh" "$FIRST_ARG")
  fi
  
  [[ -n "$TARGET_DIR" ]] || die "No se pudo resolver: $FIRST_ARG"
  
  # El target es presentaciones/<nombre> o talleres/<nombre>. Buscamos slidev/ dentro.
  if [[ -d "$TARGET_DIR/slidev" ]]; then
    PROJECT_DIR="$TARGET_DIR/slidev"
  else
    die "No se encontró carpeta 'slidev' dentro de '$TARGET_DIR'"
  fi
  
  NAME="$FIRST_ARG"
fi

# Determinar OUTPUT_ZIP si no se especificó
if [[ -z "$OUTPUT_ZIP" ]]; then
  OUTPUT_ZIP="dist/${NAME}-insightbloom-fat.zip"
fi

# Normalizar OUTPUT_ZIP (convertir a ruta absoluta si es relativa)
if [[ ! "$OUTPUT_ZIP" = /* ]]; then
  OUTPUT_ZIP="$PWD/$OUTPUT_ZIP"
fi

# Crear directorio de salida si no existe
mkdir -p "$(dirname "$OUTPUT_ZIP")"

# Verificar que existe slides.md
[[ -f "$PROJECT_DIR/slides.md" ]] || die "No se encontró slides.md en '$PROJECT_DIR'"
info "Encontrado: slides.md"

# Directorio de trabajo temporal
WORK_DIR="$(mktemp -d /tmp/slidev-fat-build.XXXXXX)"
trap "rm -rf '$WORK_DIR'" EXIT

BUILD_DIR="$WORK_DIR/build"
STAGING_DIR="$WORK_DIR/staging"

mkdir -p "$BUILD_DIR" "$STAGING_DIR"

info "Directorio fuente: $PROJECT_DIR"
info "Directorio de build: $BUILD_DIR"

# Detectar npm/pnpm/yarn
NPM_CMD="npm"
if [[ -f "$PROJECT_DIR/pnpm-lock.yaml" ]]; then
  NPM_CMD="pnpm"
elif [[ -f "$PROJECT_DIR/yarn.lock" ]]; then
  NPM_CMD="yarn"
fi
info "Gestor de paquetes: $NPM_CMD"

# Copiar proyecto a BUILD_DIR
cp -R "$PROJECT_DIR"/* "$BUILD_DIR/" 2>/dev/null || true

# Validar que exista slides.md
[[ -f "$BUILD_DIR/slides.md" ]] || die "No se encontró slides.md en $PROJECT_DIR"
info "Encontrado: slides.md"

# Instalar dependencias si es necesario
if [[ -f "$BUILD_DIR/package.json" ]]; then
  cd "$BUILD_DIR"
  info "Instalando dependencias..."
  case "$NPM_CMD" in
    pnpm) pnpm install --frozen-lockfile 2>/dev/null || pnpm install ;;
    yarn) yarn install --frozen-lockfile 2>/dev/null || yarn install ;;
    npm) npm ci 2>/dev/null || npm install ;;
  esac
  cd - > /dev/null
fi

# Ejecutar slidev build
cd "$BUILD_DIR"
info "Compilando con Slidev..."
# Intentar ejecutar slidev - preferentemente con npm run, sino con npx
if grep -q '"slidev"' package.json 2>/dev/null || grep -q '@slidev/cli' package.json 2>/dev/null; then
  # Si está en package.json, usar el gestor de paquetes
  case "$NPM_CMD" in
    pnpm) pnpm exec slidev build ;;
    yarn) yarn exec slidev build ;;
    npm) npx slidev build ;;
  esac
else
  # Fallback: usar npx directamente
  npx slidev build
fi
cd - > /dev/null

# Validar que existe dist/
[[ -d "$BUILD_DIR/dist" ]] || die "Build falló: no se generó dist/"
info "Build completado: dist/ generado"

# Copiar dist/ a staging
cp -R "$BUILD_DIR/dist" "$STAGING_DIR/dist"
info "Copiado: dist/"

# Copiar exports/ si existe
if [[ -d "$BUILD_DIR/exports" ]]; then
  cp -R "$BUILD_DIR/exports" "$STAGING_DIR/exports"
  info "Copiado: exports/"
fi

# Copiar previews/ si existe
if [[ -d "$BUILD_DIR/previews" ]]; then
  cp -R "$BUILD_DIR/previews" "$STAGING_DIR/previews"
  info "Copiado: previews/"
fi

# Generar manifiesto slidev-artifact.json
MANIFEST_FILE="$STAGING_DIR/slidev-artifact.json"
SLIDEV_VERSION=$(cd "$BUILD_DIR" && get_slidev_version "$NPM_CMD")
BUILD_ID="${CI_PIPELINE_ID:-local-$(date +%s)}"

# Construir objeto JSON de archivos con sus hashes
FILES_JSON="{"
FIRST=true

# Funciones auxiliares para encontrar archivos recursivamente
find_and_hash_files() {
  local base_path="$1"
  local prefix="$2"
  
  if [[ ! -d "$base_path" ]]; then
    return
  fi
  
  find "$base_path" -type f ! -name "*.map" ! -name ".DS_Store" | sort | while read -r file; do
    # Ruta relativa desde staging
    rel_path="${file#$STAGING_DIR/}"
    hash=$(get_file_hash "$file")
    
    if [[ -n "$FIRST" ]]; then
      FILES_JSON+="\"$rel_path\": \"sha256:$hash\""
      FIRST=false
    else
      FILES_JSON+=", \"$rel_path\": \"sha256:$hash\""
    fi
  done
}

# Recopilar hashes en un archivo temporal para evitar problemas con subshells
HASHES_FILE="$WORK_DIR/hashes.txt"
> "$HASHES_FILE"

find "$STAGING_DIR" -type f ! -name "*.map" ! -name ".DS_Store" | sort | while read -r file; do
  rel_path="${file#$STAGING_DIR/}"
  hash=$(get_file_hash "$file")
  echo "\"$rel_path\": \"sha256:$hash\"" >> "$HASHES_FILE"
done

# Construir JSON de archivos
if [[ -s "$HASHES_FILE" ]]; then
  # BSD paste (macOS) requiere indicar explícitamente stdin con "-".
  FILES_JSON=$(paste -sd ',' - < "$HASHES_FILE" | sed 's/,/, /g')
  FILES_JSON="{$FILES_JSON}"
else
  FILES_JSON="{}"
fi

# Crear manifiesto
cat > "$MANIFEST_FILE" <<EOF
{
  "engine": "slidev",
  "engineVersion": "$SLIDEV_VERSION",
  "artifactFormat": "static",
  "base": "relative",
  "buildId": "$BUILD_ID",
  "files": $FILES_JSON
}
EOF

info "Generado: slidev-artifact.json (buildId: $BUILD_ID)"

# Validar estructura antes de empaquetar
echo "Estructura del paquete:"
find "$STAGING_DIR" -type f | sed "s|^$STAGING_DIR/|  |" | sort

# Verificar que no haya archivos prohibidos
echo ""
echo "Validando archivos prohibidos..."

PROHIBITED_PATTERNS=(
  'node_modules'
  'package\.json'
  'package-lock\.json'
  'npm-shrinkwrap\.json'
  'vite\.config\.'
  'webpack\.config\.'
  'slidev\.config\.'
  '\.map$'
  'slides\.md$'
  'source/'
)

FOUND_PROHIBITED=0
for pattern in "${PROHIBITED_PATTERNS[@]}"; do
  if find "$STAGING_DIR" -type f | grep -E "$pattern" > /dev/null; then
    warn "Encontrado archivo prohibido: $pattern"
    FOUND_PROHIBITED=1
  fi
done

if [[ $FOUND_PROHIBITED -eq 1 ]]; then
  warn "El ZIP contiene archivos que deberían haber sido filtrados"
fi

# Crear ZIP
info "Creando ZIP: $OUTPUT_ZIP"
(cd "$STAGING_DIR" && zip -q -r "$OUTPUT_ZIP" .)

# Validar integridad
if unzip -t "$OUTPUT_ZIP" > /dev/null 2>&1; then
  info "ZIP íntegro"
else
  die "ZIP corrupto"
fi

# Reportar información final
COMPRESSED_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)
FILE_COUNT=$(unzip -l "$OUTPUT_ZIP" | tail -1 | awk '{print $(NF-1)}')

echo ""
echo "=========================================="
echo "✅ ZIP FAT generado exitosamente"
echo "=========================================="
echo "Archivo:    $OUTPUT_ZIP"
echo "Tamaño:     $COMPRESSED_SIZE"
echo "Archivos:   $FILE_COUNT"
echo "Engine:     slidev@$SLIDEV_VERSION"
echo "BuildId:    $BUILD_ID"
echo ""
echo "Contenido:"
echo "  ✓ dist/           (compilado)"
if [[ -d "$STAGING_DIR/exports" ]]; then
  echo "  ✓ exports/        (exportaciones)"
fi
if [[ -d "$STAGING_DIR/previews" ]]; then
  echo "  ✓ previews/       (previsualizaciones)"
fi
echo "  ✓ slidev-artifact.json (manifiesto)"
echo ""
echo "⚠ Este ZIP es experimental y requiere auditoría de InsightBloom antes de servirse"

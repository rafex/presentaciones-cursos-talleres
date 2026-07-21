#!/usr/bin/env bash
#
# Crea un ZIP compatible con el MVP de Slidev de InsightBloom.
#
# El ZIP contiene solo slides.md + assets permitidos (CSS, imágenes, fuentes).
# No incluye dist/, node_modules/, package.json, .vue, .ts, .js, etc.
#
# Uso (con nombre de proyecto — busca en presentaciones/ y talleres/):
#   ./scripts/build-slidev-insightbloom-zip.sh <nombre> [-t|--type presentation|taller] [salida.zip]
#
# Uso (con ruta completa):
#   ./scripts/build-slidev-insightbloom-zip.sh presentaciones/mi-presentacion/slidev [salida.zip]
#   ./scripts/build-slidev-insightbloom-zip.sh presentaciones/mi-presentacion/slidev dist/mi-presentacion.zip
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat >&2 <<EOF
Uso: $(basename "$0") <nombre> [-t|--type presentation|taller] [salida.zip]
  o: $(basename "$0") <ruta/slidev> [salida.zip]

Genera un ZIP compatible con InsightBloom (MVP Slidev).

Ejemplos:
  $(basename "$0") slidev-en-10-minutos                           # Resuelve automáticamente
  $(basename "$0") slidev-en-10-minutos -t presentation           # Desambigua si existe en ambos
  $(basename "$0") presentaciones/mi-presentacion/slidev          # Ruta completa
  $(basename "$0") mi-presentacion -t taller dist/mi-presentacion.zip

El ZIP contendrá solo:
  - slides.md (obligatorio)
  - assets/css/*.css
  - assets/images/*
  - assets/fonts/*
  - assets/videos/* (opcional)
  - assets/audio/* (opcional)

NO incluirá:
  - dist/, node_modules/, package.json
  - *.vue, *.ts, *.js, *.jsx, *.tsx
  - Configuraciones de build (vite.config, slidev.config, webpack.config, etc.)
  - Componentes Vue personalizados
  - Symlinks
EOF
  exit 1
}

[[ $# -ge 1 ]] || usage

# Parsear argumentos
FIRST_ARG="$1"
TYPE=""
OUTPUT_ZIP=""
shift

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
    *)
      if [[ -z "$OUTPUT_ZIP" ]]; then
        OUTPUT_ZIP="$1"
      else
        echo "Error: argumento inesperado '$1'." >&2
        usage
      fi
      shift
      ;;
  esac
done

# Detectar si es una ruta o un nombre de proyecto
if [[ "$FIRST_ARG" == */* ]]; then
  # Es una ruta (contiene /)
  PROJECT_PATH="$FIRST_ARG"
  if [[ -d "$PROJECT_PATH" ]]; then
    PROJECT_DIR="$(cd "$PROJECT_PATH" && pwd)"
  elif [[ -d "$REPO_ROOT/$PROJECT_PATH" ]]; then
    PROJECT_DIR="$(cd "$REPO_ROOT/$PROJECT_PATH" && pwd)"
  else
    echo "❌ Error: no existe la ruta '$PROJECT_PATH'." >&2
    exit 1
  fi
else
  # Es un nombre de proyecto — resolver con resolve-target.sh
  if [[ -n "$TYPE" ]]; then
    if ! TARGET_DIR=$("$SCRIPT_DIR/resolve-target.sh" "$FIRST_ARG" -t "$TYPE" 2>&1); then
      echo "❌ Error: $TARGET_DIR" >&2
      exit 1
    fi
  else
    if ! TARGET_DIR=$("$SCRIPT_DIR/resolve-target.sh" "$FIRST_ARG" 2>&1); then
      echo "❌ Error: $TARGET_DIR" >&2
      exit 1
    fi
  fi
  # El target es presentaciones/<nombre> o talleres/<nombre>. Buscamos slidev/slides.md dentro.
  if [[ -d "$TARGET_DIR/slidev" ]]; then
    PROJECT_DIR="$TARGET_DIR/slidev"
  else
    echo "❌ Error: no se encontró carpeta 'slidev' dentro de '$TARGET_DIR'." >&2
    exit 1
  fi
fi

# Verificar que existe slides.md
if [[ ! -f "$PROJECT_DIR/slides.md" ]]; then
  echo "❌ Error: no se encontró 'slides.md' en '$PROJECT_DIR'." >&2
  exit 1
fi

# Nombre del proyecto para el ZIP
PROJECT_NAME=$(basename "$(dirname "$PROJECT_DIR")")

# Directorio de salida: dist/
OUT_DIR="$REPO_ROOT/dist"
mkdir -p "$OUT_DIR"
if [[ -z "$OUTPUT_ZIP" ]]; then
  OUTPUT_ZIP="$OUT_DIR/${PROJECT_NAME}-insightbloom.zip"
else
  # Convertir a ruta absoluta si es relativa
  if [[ ! "$OUTPUT_ZIP" = /* ]]; then
    OUTPUT_ZIP="$REPO_ROOT/$OUTPUT_ZIP"
  fi
  # Crear el directorio padre si no existe
  mkdir -p "$(dirname "$OUTPUT_ZIP")"
fi

# Crear directorio temporal
STAGING_DIR=$(mktemp -d /tmp/slidev-insightbloom-XXXXXX)
trap "rm -rf '$STAGING_DIR'" EXIT

echo "📦 Preparando ZIP para InsightBloom..."
echo "   Proyecto: $PROJECT_DIR"
echo "   Salida: $OUTPUT_ZIP"
echo

# Copiar slides.md
cp "$PROJECT_DIR/slides.md" "$STAGING_DIR/slides.md"
echo "✅ Copiado: slides.md"

# Copiar assets permitidos (solo directorios específicos)
ASSETS_ALLOWED=("css" "images" "fonts" "videos" "audio")
if [[ -d "$PROJECT_DIR/assets" ]]; then
  mkdir -p "$STAGING_DIR/assets"
  
  for asset_type in "${ASSETS_ALLOWED[@]}"; do
    if [[ -d "$PROJECT_DIR/assets/$asset_type" ]]; then
      cp -R "$PROJECT_DIR/assets/$asset_type" "$STAGING_DIR/assets/"
      # Contar archivos
      count=$(find "$STAGING_DIR/assets/$asset_type" -type f | wc -l)
      echo "✅ Copiado: assets/$asset_type/ ($count archivos)"
    fi
  done
fi

# Validar que no hay archivos prohibidos en STAGING_DIR
echo
echo "🔍 Validando contenido..."

PROHIBITED_PATTERNS=(
  "dist/"
  "node_modules/"
  "package.json"
  "package-lock.json"
  "npm-shrinkwrap.json"
  "vite.config"
  "slidev.config"
  "webpack.config"
  ".vue$"
  ".ts$"
  ".tsx$"
  ".jsx$"
  ".js$"
  ".mjs$"
  ".cjs$"
  ".sh$"
)

FOUND_PROHIBITED=0
while IFS= read -r file; do
  for pattern in "${PROHIBITED_PATTERNS[@]}"; do
    if [[ "$file" =~ $pattern ]]; then
      echo "❌ Archivo prohibido encontrado: $file"
      FOUND_PROHIBITED=1
      break
    fi
  done
done < <(find "$STAGING_DIR" -type f)

if [[ $FOUND_PROHIBITED -eq 1 ]]; then
  echo "❌ Error: el staging contiene archivos prohibidos." >&2
  exit 1
fi

# Crear el ZIP desde el directorio de staging
echo "📝 Creando ZIP..."
(cd "$STAGING_DIR" && zip -q -r "$OUTPUT_ZIP" slides.md assets -x '*.DS_Store')

# Validaciones finales
echo
echo "✓ Validando ZIP..."

# 1. Verificar integridad
if ! unzip -t "$OUTPUT_ZIP" >/dev/null 2>&1; then
  echo "❌ Error: ZIP corrupto o inválido." >&2
  exit 1
fi
echo "  ✓ ZIP íntegro"

# 2. Verificar que existe slides.md
if ! unzip -l "$OUTPUT_ZIP" | grep -q "slides.md"; then
  echo "❌ Error: slides.md no encontrado en el ZIP." >&2
  exit 1
fi
echo "  ✓ slides.md presente"

# 3. Verificar que no hay archivos prohibidos
HAS_PROHIBITED=0
for pattern in "${PROHIBITED_PATTERNS[@]}"; do
  if unzip -l "$OUTPUT_ZIP" 2>/dev/null | grep -v "^Archive:" | grep -E "$pattern" >/dev/null 2>&1; then
    echo "  ✗ Encontrado patrón prohibido: $pattern"
    HAS_PROHIBITED=1
  fi
done

if [[ $HAS_PROHIBITED -eq 1 ]]; then
  echo "❌ Error: el ZIP contiene archivos prohibidos." >&2
  exit 1
fi
echo "  ✓ Sin archivos prohibidos"

# Obtener información del ZIP
ZIP_SIZE=$(du -sh "$OUTPUT_ZIP" | awk '{print $1}')
ZIP_SIZE_BYTES=$(stat -f%z "$OUTPUT_ZIP" 2>/dev/null || stat -c%s "$OUTPUT_ZIP" 2>/dev/null)
FILE_COUNT=$(unzip -l "$OUTPUT_ZIP" 2>/dev/null | grep -E "^-" | wc -l)

echo
echo "✅ ZIP generado exitosamente"
echo
echo "📊 Resumen:"
echo "   Archivo: $OUTPUT_ZIP"
echo "   Tamaño: $ZIP_SIZE ($ZIP_SIZE_BYTES bytes)"
echo
echo "📋 Contenido del ZIP:"
unzip -l "$OUTPUT_ZIP" 2>/dev/null | grep -v "^Archive:" | grep -v "Length" | grep -v "^--------" | awk 'NF {print "   " $0}'
echo
echo "✓ Compatible con InsightBloom MVP (Slidev)"

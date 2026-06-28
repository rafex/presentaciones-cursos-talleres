#!/usr/bin/env bash
#
# Genera un ZIP de una presentación Marp (o taller) listo para subir a
# InsightBloom (microservicio insightbloom-presentations,
# POST /api/v1/conferences/:id/presentation).
#
# Pensado para invocarse vía `just zip ...` desde la raíz del repo (que ya
# resuelve la carpeta correcta entre presentaciones/ y talleres/), pero
# también funciona en standalone pasando una ruta relativa o absoluta.
#
# Uso:
#   ./scripts/build-presentation-zip.sh <carpeta> [archivo.md] [salida.zip]
#
# Ejemplos:
#   ./scripts/build-presentation-zip.sh presentaciones/boost-desarrollo-con-ia-con-opensource
#   ./scripts/build-presentation-zip.sh talleres/crea-tu-agente-ia
#   ./scripts/build-presentation-zip.sh presentaciones/desarrollando-con-ia desarrollando_con_ia-corta.md
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat >&2 <<EOF
Uso: $(basename "$0") <carpeta> [archivo.md] [salida.zip]

  <carpeta>                Ruta a la carpeta de la presentación/taller,
                           relativa al repo o absoluta.
  [archivo.md]             Nombre del .md a empaquetar, si la carpeta tiene
                           más de uno (ej: desarrollando_con_ia.md). Opcional
                           si solo hay un .md.
  [salida.zip]              Ruta del zip de salida. Por defecto:
                           dist/<carpeta>.zip
EOF
  exit 1
}

[[ $# -ge 1 ]] || usage

INPUT_DIR="$1"
MD_ARG="${2:-}"
OUT_ARG="${3:-}"

# --- Resolver carpeta de la presentación/taller ---
if [[ -d "$INPUT_DIR" ]]; then
  PRES_DIR="$(cd "$INPUT_DIR" && pwd)"
elif [[ -d "$REPO_ROOT/$INPUT_DIR" ]]; then
  PRES_DIR="$(cd "$REPO_ROOT/$INPUT_DIR" && pwd)"
else
  echo "Error: no existe la carpeta '$INPUT_DIR'." >&2
  exit 1
fi
PRES_NAME="$(basename "$PRES_DIR")"

is_excluded() {
  local rel="$1"
  case "$rel" in
    .git|.git/*|*/.git|*/.git/*) return 0 ;;
    node_modules|node_modules/*|*/node_modules|*/node_modules/*) return 0 ;;
    .DS_Store|*/.DS_Store) return 0 ;;
    *.pdf|*.odp) return 0 ;;
    *backup-*) return 0 ;;
  esac
  return 1
}

# Carpetas de primer nivel que son repos clonados/embebidos (tienen su propio
# .git) y no forman parte de la presentación Marp: se excluyen por completo.
EMBEDDED_REPO_EXCLUDES=()
while IFS= read -r d; do
  name="$(basename "$d")"
  is_excluded "$name" && continue
  if [[ -e "$d/.git" ]]; then
    EMBEDDED_REPO_EXCLUDES+=("$name")
  fi
done < <(find "$PRES_DIR" -mindepth 1 -maxdepth 1 -type d)

is_excluded_path() {
  local rel="$1"
  is_excluded "$rel" && return 0
  for ex in "${EMBEDDED_REPO_EXCLUDES[@]:-}"; do
    [[ -n "$ex" ]] || continue
    case "$rel" in
      "$ex"|"$ex"/*) return 0 ;;
    esac
  done
  return 1
}

# --- Encontrar .md candidatos hasta 4 niveles de profundidad ---
MD_FILES=()
while IFS= read -r f; do
  rel="${f#"$PRES_DIR"/}"
  is_excluded_path "$rel" && continue
  MD_FILES+=("$f")
done < <(find "$PRES_DIR" -maxdepth 4 -iname "*.md" | sort)

if [[ ${#MD_FILES[@]} -eq 0 ]]; then
  echo "Error: no se encontró ningún .md dentro de '$PRES_DIR' (hasta 4 niveles)." >&2
  exit 1
fi

if [[ -n "$MD_ARG" ]]; then
  MD_FILE=""
  for f in "${MD_FILES[@]}"; do
    [[ "$(basename "$f")" == "$MD_ARG" ]] && MD_FILE="$f"
  done
  if [[ -z "$MD_FILE" ]]; then
    echo "Error: '$MD_ARG' no es uno de los .md encontrados en '$PRES_NAME':" >&2
    for f in "${MD_FILES[@]}"; do echo "  - $(basename "$f")" >&2; done
    exit 1
  fi
elif [[ ${#MD_FILES[@]} -eq 1 ]]; then
  MD_FILE="${MD_FILES[0]}"
else
  echo "Error: hay varios .md en '$PRES_NAME'. Especifica cuál usar como 2º argumento:" >&2
  for f in "${MD_FILES[@]}"; do echo "  - $(basename "$f")" >&2; done
  exit 1
fi

MD_REL="${MD_FILE#"$PRES_DIR"/}"
echo "📄 Markdown: $MD_REL"

# --- Detectar tema personalizado (carpeta css/ con theme.css) ---
THEME_FILE=""
while IFS= read -r f; do
  rel="${f#"$PRES_DIR"/}"
  is_excluded_path "$rel" && continue
  THEME_FILE="$f"
  break
done < <(find "$PRES_DIR" -maxdepth 4 -path "*/css/theme.css" 2>/dev/null)
if [[ -n "$THEME_FILE" ]]; then
  echo "🎨 Tema: ${THEME_FILE#"$PRES_DIR"/}"
else
  echo "ℹ️  Sin theme.css en carpeta css/: se usará el tema por defecto de InsightBloom."
fi

# --- Recursos a incluir ---
# En vez de copiar toda la carpeta (que en talleres puede traer proyectos de
# código completos, tests, secretos, etc. ajenos a las slides), se copian
# solo el .md elegido, el tema (si existe) y los recursos que de verdad
# referencian, resueltos relativos al archivo que los referencia.
extract_refs() {
  # Extrae rutas de ![...](...) y url(...) de un archivo, ignorando
  # URLs absolutas, anclas y data URIs.
  local file="$1"
  grep -oE '!\[[^]]*\]\([^)]+\)|url\([^)]+\)' "$file" 2>/dev/null \
    | sed -E 's/.*\(([^)]+)\)/\1/' | tr -d '"'"'"'' \
    | while IFS= read -r ref; do
        case "$ref" in
          http://*|https://*|\#*|data:*) continue ;;
        esac
        ref="${ref%%\?*}"
        ref="${ref%%\#*}"
        [[ -n "$ref" ]] && echo "$ref"
      done
}

STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT

copy_into_staging() {
  # $1 = ruta relativa a PRES_DIR
  local rel="$1"
  [[ -e "$PRES_DIR/$rel" ]] || return 1
  mkdir -p "$STAGING/$(dirname "$rel")"
  cp -R "$PRES_DIR/$rel" "$STAGING/$rel"
  return 0
}

echo "📦 Copiando .md, tema y recursos referenciados..."
copy_into_staging "$MD_REL"

MISSING=0
MD_DIR_REL="$(dirname "$MD_REL")"
while IFS= read -r ref; do
  [[ -z "$ref" ]] && continue
  # Resolver relativo a la carpeta del .md
  if [[ "$MD_DIR_REL" == "." ]]; then
    rel_path="$ref"
  else
    rel_path="$MD_DIR_REL/$ref"
  fi
  if ! copy_into_staging "$rel_path"; then
    echo "  ⚠️  Recurso referenciado no encontrado: $ref"
    MISSING=1
  fi
done < <(extract_refs "$MD_FILE")

if [[ -n "$THEME_FILE" ]]; then
  THEME_REL="${THEME_FILE#"$PRES_DIR"/}"
  copy_into_staging "$THEME_REL"
  # Si el theme.css referencia fuentes locales (url(...)), incluirlas también.
  THEME_DIR_REL="$(dirname "$THEME_REL")"
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    rel_path="$THEME_DIR_REL/$ref"
    copy_into_staging "$rel_path" \
      || echo "  ⚠️  Recurso referenciado desde theme.css no encontrado: $ref"
  done < <(extract_refs "$THEME_FILE")
fi

if [[ "$MISSING" -eq 1 ]]; then
  echo "⚠️  Hay recursos referenciados que no se encontraron en el árbol de archivos. Revisa las rutas antes de subir el ZIP." >&2
else
  echo "✅ Todos los recursos referenciados desde el .md existen y se incluyeron en el ZIP."
fi

# --- Generar el ZIP (sin carpeta raíz envolvente) ---
OUT_DIR="$REPO_ROOT/dist"
mkdir -p "$OUT_DIR"
OUT_ZIP="${OUT_ARG:-$OUT_DIR/${PRES_NAME}.zip}"
[[ "$OUT_ZIP" = /* ]] || OUT_ZIP="$PWD/$OUT_ZIP"
mkdir -p "$(dirname "$OUT_ZIP")"
rm -f "$OUT_ZIP"

(cd "$STAGING" && zip -rq "$OUT_ZIP" .)

SIZE_HUMAN="$(du -h "$OUT_ZIP" | cut -f1)"
echo "✅ ZIP generado: $OUT_ZIP ($SIZE_HUMAN)"
echo
echo "Subir con curl:"
echo "  curl -F file=@\"$OUT_ZIP\" https://insightbloom.v1.rafex.cloud/api/presentations/api/v1/conferences/{conferenceId}/presentation"

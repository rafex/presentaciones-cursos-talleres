#!/usr/bin/env bash
#
# Crea una nueva presentación/ponencia bajo presentaciones/<nombre>/
# respetando la convención del repo (<nombre>.md + assets/css/theme.css +
# assets/images/), con el mismo frontmatter Marp que ya usan las charlas
# existentes.
#
# Uso interactivo:
#   ./scripts/new-presentacion.sh
#
# Uso no interactivo (para scripting/CI; si el título tiene espacios, mejor
# usar el modo interactivo o invocar el script directo, no vía `just`):
#   ./scripts/new-presentacion.sh <nombre> [titulo]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

NAME="${1:-}"
TITLE="${2:-}"

prompt() {
  local msg="$1" default="${2:-}" reply
  if [[ -n "$default" ]]; then
    read -r -p "$msg [$default]: " reply
    echo "${reply:-$default}"
  else
    read -r -p "$msg: " reply
    echo "$reply"
  fi
}

if [[ -z "$NAME" ]]; then
  NAME="$(prompt "Nombre de la presentación (carpeta, kebab-case)")"
fi
[[ -n "$NAME" ]] || { echo "Error: el nombre no puede estar vacío." >&2; exit 1; }
if ! [[ "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "Error: usa solo minúsculas, números y guiones (kebab-case). Recibido: '$NAME'" >&2
  exit 1
fi

PRES_DIR="$REPO_ROOT/presentaciones/$NAME"
if [[ -e "$PRES_DIR" ]]; then
  echo "Error: 'presentaciones/$NAME' ya existe." >&2
  exit 1
fi

if [[ -z "$TITLE" ]]; then
  TITLE="$(prompt "Título de la charla" "$NAME")"
fi

MESES=(enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre)
DIA="$(date +%-d 2>/dev/null || date +%d)"
MES_NUM="$(date +%-m 2>/dev/null || date +%m)"
ANIO="$(date +%Y)"
FECHA="$DIA ${MESES[$((10#$MES_NUM - 1))]} $ANIO"

echo
echo "📁 Creando presentaciones/$NAME ..."
mkdir -p "$PRES_DIR/assets/css" "$PRES_DIR/assets/images"

sed -e "s/__TITULO__/$TITLE/g" -e "s/__FECHA__/$FECHA/g" \
  "$TEMPLATES_DIR/presentacion.md" > "$PRES_DIR/$NAME.md"

cp "$TEMPLATES_DIR/theme.css" "$PRES_DIR/assets/css/theme.css"
touch "$PRES_DIR/assets/images/.gitkeep"

echo "✅ Presentación creada en presentaciones/$NAME"
echo
echo "Estructura:"
find "$PRES_DIR" | sed "s|$REPO_ROOT/||" | sort
echo
echo "Próximos pasos:"
echo "  - Edita presentaciones/$NAME/$NAME.md"
echo "  - Personaliza presentaciones/$NAME/assets/css/theme.css"
echo "  - just generate $NAME -t presentation"
echo "  - Cuando esté lista para publicarse: crea presentaciones/$NAME/.release.yaml"
echo "    (ver presentaciones/boost-desarrollo-con-ia-con-opensource/.release.yaml como ejemplo)"

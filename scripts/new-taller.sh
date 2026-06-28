#!/usr/bin/env bash
#
# Crea un nuevo taller bajo talleres/<nombre>/ respetando la convención del
# repo (slides Marp en la raíz: <nombre>.md + assets/, código en ejercicios/)
# y genera un ejercicios/.gitignore combinando plantillas de seguridad +
# sistema operativo + IDE(s) + lenguaje(s) elegidos, para evitar subir
# secretos/tokens o ruido de entorno por error.
#
# Uso interactivo:
#   ./scripts/new-taller.sh
#
# Uso no interactivo (para scripting/CI):
#   ./scripts/new-taller.sh <nombre> [titulo] [langs separados por espacio/coma] [ides separados por espacio/coma]
#
# Ejemplo:
#   ./scripts/new-taller.sh mi-taller "Mi Taller" python,node ambos
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"
GITIGNORE_DIR="$TEMPLATES_DIR/gitignore"

NAME="${1:-}"
TITLE="${2:-}"
LANGS_ARG="${3:-}"
IDES_ARG="${4:-}"

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
  NAME="$(prompt "Nombre del taller (carpeta, kebab-case)")"
fi
[[ -n "$NAME" ]] || { echo "Error: el nombre no puede estar vacío." >&2; exit 1; }
if ! [[ "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "Error: usa solo minúsculas, números y guiones (kebab-case). Recibido: '$NAME'" >&2
  exit 1
fi

TALLER_DIR="$REPO_ROOT/talleres/$NAME"
if [[ -e "$TALLER_DIR" ]]; then
  echo "Error: 'talleres/$NAME' ya existe." >&2
  exit 1
fi

if [[ -z "$TITLE" ]]; then
  TITLE="$(prompt "Título para las slides" "$NAME")"
fi

# Lenguajes disponibles = cada plantilla en templates/gitignore/ que no sea
# de propósito especial (seguridad, SO, IDEs).
ALL_LANGS=()
for f in "$GITIGNORE_DIR"/*.gitignore; do
  base="$(basename "$f" .gitignore)"
  case "$base" in
    security|macos|vscode|jetbrains) continue ;;
  esac
  ALL_LANGS+=("$base")
done

if [[ -z "$LANGS_ARG" ]]; then
  echo "Lenguajes disponibles: ${ALL_LANGS[*]} (o 'ninguno')"
  LANGS_ARG="$(prompt "Lenguaje(s) a usar en ejercicios/ (separados por espacio o coma)" "ninguno")"
fi
LANGS_ARG="${LANGS_ARG//,/ }"

SELECTED_LANGS=()
for lang in $LANGS_ARG; do
  [[ "$lang" == "ninguno" || "$lang" == "none" ]] && continue
  valid=0
  for candidate in "${ALL_LANGS[@]}"; do
    [[ "$lang" == "$candidate" ]] && valid=1
  done
  if [[ "$valid" -eq 0 ]]; then
    echo "Aviso: lenguaje desconocido '$lang', se ignora. Disponibles: ${ALL_LANGS[*]}" >&2
    continue
  fi
  SELECTED_LANGS+=("$lang")
done

if [[ -z "$IDES_ARG" ]]; then
  IDES_ARG="$(prompt "IDEs a ignorar: vscode, jetbrains, ambos o ninguno" "ambos")"
fi
IDES_ARG="${IDES_ARG//,/ }"

SELECTED_IDES=()
for ide in $IDES_ARG; do
  case "$ide" in
    ambos|both|all) SELECTED_IDES+=("vscode" "jetbrains") ;;
    vscode|jetbrains) SELECTED_IDES+=("$ide") ;;
    ninguno|none) ;;
    *) echo "Aviso: IDE desconocido '$ide', se ignora." >&2 ;;
  esac
done

echo
echo "📁 Creando talleres/$NAME ..."
mkdir -p "$TALLER_DIR/assets/css" "$TALLER_DIR/assets/images" "$TALLER_DIR/ejercicios"

# --- slides ---
FECHA="$(date +%Y-%m-%d)"
sed -e "s/__TITULO__/$TITLE/g" -e "s/__FECHA__/$FECHA/g" \
  "$TEMPLATES_DIR/taller.md" > "$TALLER_DIR/$NAME.md"

cp "$TEMPLATES_DIR/theme.css" "$TALLER_DIR/assets/css/theme.css"
touch "$TALLER_DIR/assets/images/.gitkeep"

# --- ejercicios/.gitignore (seguridad + SO siempre, IDEs/lenguajes elegidos) ---
{
  echo "# Generado por scripts/new-taller.sh -- ajusta a mano si lo necesitas."
  echo
  cat "$GITIGNORE_DIR/security.gitignore"
  echo
  cat "$GITIGNORE_DIR/macos.gitignore"
  for ide in "${SELECTED_IDES[@]+"${SELECTED_IDES[@]}"}"; do
    echo
    cat "$GITIGNORE_DIR/$ide.gitignore"
  done
  for lang in "${SELECTED_LANGS[@]+"${SELECTED_LANGS[@]}"}"; do
    echo
    cat "$GITIGNORE_DIR/$lang.gitignore"
  done
} > "$TALLER_DIR/ejercicios/.gitignore"

touch "$TALLER_DIR/ejercicios/.gitkeep"

echo "✅ Taller creado en talleres/$NAME"
echo
echo "Estructura:"
find "$TALLER_DIR" | sed "s|$REPO_ROOT/||" | sort
echo
echo "Próximos pasos:"
echo "  - Edita talleres/$NAME/$NAME.md"
echo "  - Personaliza talleres/$NAME/assets/css/theme.css"
echo "  - Agrega tu código dentro de talleres/$NAME/ejercicios/"
echo "  - just generate $NAME -t taller"

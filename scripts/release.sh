#!/usr/bin/env bash
#
# Recorre presentaciones/ y talleres/ buscando archivos .release*.yaml.
# Cada uno describe un artefacto candidato a publicarse en un GitHub Release.
# Genera un zip para los que no estén publicados (o tengan republish: true),
# calcula su sha256, los deja en dist/ junto a un dist/checksums.txt, y
# actualiza el propio .release*.yaml marcándolo como publicado.
#
# Uso:
#   ./scripts/release.sh
#
# Formato de .release*.yaml (claves planas, sin anidar):
#   name: nombre-del-artefacto      # base del .zip, default: nombre de carpeta
#   md: archivo.md                  # opcional, solo si hay >1 .md en la carpeta
#   published: true|false
#   published_at: "2026-06-28T12:00:00Z"
#   sha256: "..."
#   republish: true|false           # forzar regeneración aunque ya esté publicado
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$REPO_ROOT/dist"

mkdir -p "$DIST_DIR"
CHECKSUMS_FILE="$DIST_DIR/checksums.txt"
: > "$CHECKSUMS_FILE"

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    sha256sum "$1" | awk '{print $1}'
  fi
}

get_yaml_value() {
  # Lee una clave plana "key: value" (sin anidar), quitando comillas.
  local file="$1" key="$2" value
  value="$(awk -F': ?' -v k="$key" '$1==k {sub(/^[^:]*: ?/,""); print; exit}' "$file")"
  value="${value%\"}"
  value="${value#\"}"
  echo "$value"
}

BUILT=0
SKIPPED=0
FAILED=0

while IFS= read -r release_file; do
  dir="$(dirname "$release_file")"
  folder_name="$(basename "$dir")"

  published="$(get_yaml_value "$release_file" "published")"
  republish="$(get_yaml_value "$release_file" "republish")"
  name="$(get_yaml_value "$release_file" "name")"
  md="$(get_yaml_value "$release_file" "md")"

  [[ -n "$name" ]] || name="$folder_name"

  if [[ "$published" == "true" && "$republish" != "true" ]]; then
    echo "⏭️  $name: ya publicado, se omite (republish: false)."
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  echo "📦 Generando zip para '$name' ($release_file)..."
  out_zip="$DIST_DIR/$name.zip"
  if ! "$REPO_ROOT/scripts/build-presentation-zip.sh" "$dir" "$md" "$out_zip"; then
    echo "❌ Falló la generación del zip para '$name'." >&2
    FAILED=$((FAILED + 1))
    continue
  fi

  sha="$(sha256_of "$out_zip")"
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  cat > "$release_file" <<EOF
name: $name
md: $md
published: true
published_at: "$now"
sha256: "$sha"
republish: false
EOF

  echo "$sha  $(basename "$out_zip")" >> "$CHECKSUMS_FILE"
  BUILT=$((BUILT + 1))
  echo "✅ $name -> $(basename "$out_zip") ($sha)"
done < <(find "$REPO_ROOT/presentaciones" "$REPO_ROOT/talleres" -maxdepth 2 -iname '.release*.yaml' 2>/dev/null | sort)

echo
echo "Resumen: $BUILT generado(s), $SKIPPED omitido(s), $FAILED fallido(s)."

if [[ "$BUILT" -eq 0 ]]; then
  rm -f "$CHECKSUMS_FILE"
  echo "Nada nuevo que publicar."
fi

[[ "$FAILED" -eq 0 ]] || exit 1

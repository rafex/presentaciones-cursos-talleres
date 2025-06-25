#!/usr/bin/env bash
set -euo pipefail

# Si pasas argumentos (pdf, odp o all), sólo genera esos; si no, genera ambos.
if [[ $# -ge 1 ]]; then
  formats=()
  for arg in "$@"; do
    case "$arg" in
      pdf|odp) formats+=("$arg") ;;
      all) formats=(pdf odp) ;;
      *)
        echo "Aviso: Formato desconocido '$arg'. Usando 'pdf' y 'odp'."
        formats=(pdf odp)
        ;;
    esac
  done
else
  formats=(pdf odp)
fi

# Recorre cada subcarpeta de 'presentaciones'
for dir in */ ; do
  [[ -d "$dir" ]] || continue

  # Busca archivos .md
  md_files=( "$dir"/*.md )
  [[ -e "${md_files[0]}" ]] || { echo "  → No hay MD en $dir, salteando."; continue; }

  for md in "${md_files[@]}"; do
    base="${md##*/}"
    name="${base%.*}"

    for fmt in "${formats[@]}"; do
      out="$dir/${name}.${fmt}"
      echo "Generando $out..."
      marp "$md" \
        --theme "$dir/assets/css/theme.css" \
        --allow-local-files \
        -o "$out"
    done
  done
done
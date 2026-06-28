# Orquesta los comandos de generación/empaquetado de presentaciones y
# talleres desde la raíz del repo, sin tener que entrar a cada carpeta.
#
# Como un nombre puede repetirse entre presentaciones/ y talleres/, ambos
# recipes aceptan -t/--type presentation|taller para desambiguar.
#
# Ejemplos:
#   just generate boost-desarrollo-con-ia-con-opensource
#   just generate crea-tu-agente-ia pdf -t taller
#   just zip desarrollando-con-ia desarrollando_con_ia-corta.md
#   just zip crea-tu-agente-ia -t taller
#   just list

default:
    @just --list

# Genera PDF/ODP de una presentación o taller.
# Uso: just generate <nombre> [pdf|odp|all] [-t|--type presentation|taller]
generate *args:
    #!/usr/bin/env bash
    set -euo pipefail
    args=({{args}})
    name=""
    format="all"
    type_flags=()
    i=0
    while [[ $i -lt ${#args[@]} ]]; do
      a="${args[$i]}"
      case "$a" in
        -t|--type)
          type_flags+=("$a" "${args[$((i+1))]}")
          i=$((i+2))
          ;;
        -t=*|--type=*)
          type_flags+=("$a")
          i=$((i+1))
          ;;
        pdf|odp|all)
          format="$a"
          i=$((i+1))
          ;;
        *)
          [[ -z "$name" ]] && name="$a"
          i=$((i+1))
          ;;
      esac
    done
    if [[ -z "$name" ]]; then
      echo "Uso: just generate <nombre> [pdf|odp|all] [-t presentation|taller]" >&2
      exit 1
    fi
    dir=$(./scripts/resolve-target.sh "$name" "${type_flags[@]+"${type_flags[@]}"}")
    ./scripts/generate-slides.sh "$dir" "$format"

# Genera el ZIP listo para subir a InsightBloom.
# Uso: just zip <nombre> [archivo.md] [salida.zip] [-t|--type presentation|taller]
zip *args:
    #!/usr/bin/env bash
    set -euo pipefail
    args=({{args}})
    positional=()
    type_flags=()
    i=0
    while [[ $i -lt ${#args[@]} ]]; do
      a="${args[$i]}"
      case "$a" in
        -t|--type)
          type_flags+=("$a" "${args[$((i+1))]}")
          i=$((i+2))
          ;;
        -t=*|--type=*)
          type_flags+=("$a")
          i=$((i+1))
          ;;
        *)
          positional+=("$a")
          i=$((i+1))
          ;;
      esac
    done
    name="${positional[0]:-}"
    md="${positional[1]:-}"
    out="${positional[2]:-}"
    if [[ -z "$name" ]]; then
      echo "Uso: just zip <nombre> [archivo.md] [salida.zip] [-t presentation|taller]" >&2
      exit 1
    fi
    dir=$(./scripts/resolve-target.sh "$name" "${type_flags[@]+"${type_flags[@]}"}")
    ./scripts/build-presentation-zip.sh "$dir" "$md" "$out"

# Genera los zips de release pendientes (omite los ya publicados, salvo
# que su .release*.yaml tenga republish: true). Deja todo en dist/ y
# actualiza los .release*.yaml con published/published_at/sha256.
release:
    ./scripts/release.sh

# Crea un nuevo taller en talleres/<nombre>/ (slides + assets/ + ejercicios/
# con .gitignore de seguridad+SO+IDE(s)+lenguaje(s)). Sin argumentos, pregunta
# interactivamente (recomendado si el título tiene espacios, ya que `just`
# no preserva comillas en *args). Uso no interactivo (título sin espacios o
# usa guiones, o mejor invoca ./scripts/new-taller.sh directo):
#   just new-taller <nombre> [titulo] [langs] [ides]
new-taller *args:
    ./scripts/new-taller.sh {{args}}

# Lista las presentaciones y talleres disponibles.
list:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Presentaciones:"
    find presentaciones -mindepth 1 -maxdepth 1 -type d -not -name node_modules -not -name scripts -exec basename {} \; | sort
    echo
    echo "Talleres:"
    find talleres -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort

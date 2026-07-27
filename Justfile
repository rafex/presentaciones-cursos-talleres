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
#   just zip red-soberana-de-ia --engine slidev
#   just slidev-zip presentaciones/red-soberana-de-ia/slidev/slides.md
#   just list

default:
    @just --list

# Genera la salida tradicional de Marp: PDF, ODP o ambos.
# `nombre` se resuelve en presentaciones/ o talleres/; usa `-t taller` si
# necesitas indicar explícitamente que el material vive en talleres/.
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

# Inicia Slidev en desarrollo; acepta curso-git o una ruta completa a slides.md.
slidev-dev source:
    ./scripts/generate-slidev.sh "{{source}}" dev

# Exporta Slidev a una salida estática: pdf, pptx o png. Acepta nombre o ruta.
slidev-export source format="pdf":
    ./scripts/generate-slidev.sh "{{source}}" "{{format}}"

# Empaqueta el proyecto Slidev completo para InsightBloom, con source/ y dist/.
slidev-zip source out="":
    ./scripts/build-slidev-presentation-zip.sh "{{source}}" "{{out}}"

# Empaqueta el proyecto Slidev mínimo para InsightBloom, sin dependencias.
# Uso: just slidev-insightbloom-zip <nombre> [-t presentation|taller] [salida.zip]
#      just slidev-insightbloom-zip slidev-en-10-minutos
#      just slidev-insightbloom-zip slidev-en-10-minutos -t presentation
#      just slidev-insightbloom-zip slidev-en-10-minutos dist/custom.zip
# Crea el ZIP MVP con slides.md y assets permitidos, sin node_modules ni dist/.
slidev-insightbloom-zip *args:
    #!/usr/bin/env bash
    set -euo pipefail
    args=({{args}})
    name=""
    out=""
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
          if [[ -z "$name" ]]; then
            name="$a"
          elif [[ -z "$out" ]]; then
            out="$a"
          else
            i=$((i+1))
          fi
          i=$((i+1))
          ;;
      esac
    done
    if [[ -z "$name" ]]; then
      echo "Uso: just slidev-insightbloom-zip <nombre> [-t presentation|taller] [salida.zip]" >&2
      exit 1
    fi
    ./scripts/build-slidev-insightbloom-zip.sh "$name" "${type_flags[@]+"${type_flags[@]}"}" "$out"

# Empaqueta un proyecto Slidev compilado para InsightBloom FAT (con dist/, manifiesto y hashes).
# Formato experimental que requiere auditoría de InsightBloom antes de servirse.
# Uso: just slidev-insightbloom-fat-zip <nombre> [-t presentation|taller] [salida.zip]
#      just slidev-insightbloom-fat-zip slidev-en-10-minutos
#      just slidev-insightbloom-fat-zip slidev-en-10-minutos -t presentation
#      just slidev-insightbloom-fat-zip slidev-en-10-minutos dist/custom.zip
# Crea el ZIP FAT con dist/, manifiesto y hashes; formato experimental.
slidev-insightbloom-fat-zip *args:
    #!/usr/bin/env bash
    set -euo pipefail
    args=({{args}})
    name=""
    out=""
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
          if [[ -z "$name" ]]; then
            name="$a"
          elif [[ -z "$out" ]]; then
            out="$a"
          else
            i=$((i+1))
          fi
          i=$((i+1))
          ;;
      esac
    done
    if [[ -z "$name" ]]; then
      echo "Uso: just slidev-insightbloom-fat-zip <nombre> [-t presentation|taller] [salida.zip]" >&2
      exit 1
    fi
    if [[ -n "$out" ]]; then
      ./scripts/build-slidev-insightbloom-fat-zip.sh "$name" "${type_flags[@]+"${type_flags[@]}"}" "$out"
    else
      ./scripts/build-slidev-insightbloom-fat-zip.sh "$name" "${type_flags[@]+"${type_flags[@]}"}"
    fi

# Construye el catálogo HTML de presentaciones Marp y Slidev.
portal-build:
    node ./scripts/build-portal.mjs

# Sirve el portal local en http://localhost:4173 y genera sus artefactos antes.
portal-dev:
    #!/usr/bin/env bash
    set -euo pipefail
    port="${PORT:-4173}"
    node ./scripts/build-portal.mjs
    listeners="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)"
    for pid in $listeners; do
        command_line="$(ps -p "$pid" -o command= 2>/dev/null || true)"
        if [[ "$command_line" == *"http.server $port --directory portal"* ]]; then
            if curl -fsS --max-time 2 "http://127.0.0.1:$port/" >/dev/null; then
                echo "Portal ya está disponible en http://localhost:$port/ (PID $pid)."
                exit 0
            fi
            echo "La instancia anterior del portal (PID $pid) no responde; se reiniciará." >&2
            kill "$pid" 2>/dev/null || true
        fi
    done
    for _ in 1 2 3 4 5; do
        listeners="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)"
        [[ -z "$listeners" ]] && break
        sleep 0.2
    done
    if [[ -n "$listeners" ]]; then
        echo "El puerto $port ya está ocupado por otro proceso (PID(s): $listeners)." >&2
        echo "Cierra ese proceso o ejecuta: PORT=4174 just portal-dev" >&2
        exit 1
    fi
    exec python3 -m http.server "$port" --directory portal

# Genera un ZIP listo para subir a InsightBloom.
# Por defecto usa Marp; agrega `--engine slidev` para empaquetar
# <directorio>/slidev/slides.md sin eliminar la fuente Marp.
# Uso: just zip <nombre> [archivo.md] [salida.zip] [-t|--type presentation|taller] [--engine marp|slidev]
zip *args:
    #!/usr/bin/env bash
    set -euo pipefail
    args=({{args}})
    positional=()
    type_flags=()
    engine="marp"
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
        -e|--engine)
          engine="${args[$((i+1))]}"
          i=$((i+2))
          ;;
        -e=*|--engine=*)
          engine="${a#*=}"
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
      echo "Uso: just zip <nombre> [archivo.md] [salida.zip] [-t presentation|taller] [--engine marp|slidev]" >&2
      exit 1
    fi
    dir=$(./scripts/resolve-target.sh "$name" "${type_flags[@]+"${type_flags[@]}"}")
    if [[ "$engine" == "slidev" ]]; then
      slidev_md="${md:-slidev/slides.md}"
      ./scripts/build-slidev-presentation-zip.sh "$dir/$slidev_md" "$out"
    elif [[ "$engine" == "marp" ]]; then
      ./scripts/build-presentation-zip.sh "$dir" "$md" "$out"
    else
      echo "Uso: --engine marp|slidev" >&2
      exit 1
    fi

# Genera los zips de release pendientes (omite los ya publicados, salvo
# que su .release*.yaml tenga republish: true). Deja todo en dist/ y
# actualiza los .release*.yaml con published/published_at/sha256.
release:
    ./scripts/release.sh

# Crea un nuevo taller en talleres/<nombre>/ (Marp + assets/ + ejercicios/).
# Slidev es opcional y se agrega como una fuente paralela con --engine slidev
# o --engine both; nunca reemplaza el Markdown Marp.
# Uso no interactivo:
#   just new-taller <nombre> [titulo] [langs] [ides] [--engine slidev]
new-taller *args:
    #!/usr/bin/env bash
    python3 ./scripts/new-taller.py "$@"

# Crea una nueva presentación en presentaciones/<nombre>/ (slides + assets/).
# 
# Modo interactivo (recomendado):
#   just new-presentacion
#
# Con argumentos (pasar nombre y título entre comillas):
#   python3 ./scripts/new-presentacion.py "red soberana de IA" "Reutiliza tus equipos..."
new-presentacion *args:
    #!/usr/bin/env bash
    python3 ./scripts/new-presentacion.py "$@"
list:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Presentaciones:"
    find presentaciones -mindepth 1 -maxdepth 1 -type d -not -name node_modules -not -name scripts -exec basename {} \; | sort
    echo
    echo "Talleres:"
    find talleres -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort

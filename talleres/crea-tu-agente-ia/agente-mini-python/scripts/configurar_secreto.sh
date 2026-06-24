#!/usr/bin/env bash
# Pide la GROQ_API_KEY de forma interactiva y deja secrets/groq.enc.env
# cifrado con sops+age, listo para commitear.
set -euo pipefail

DIR_RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVO_PLANTILLA="$DIR_RAIZ/secrets/groq.example.env"
ARCHIVO_CIFRADO="$DIR_RAIZ/secrets/groq.enc.env"

fallar() {
    echo "Error: $1" >&2
    exit 1
}

command -v sops >/dev/null 2>&1 || fallar "no encontré 'sops'. Instálalo: https://github.com/getsops/sops"
command -v age >/dev/null 2>&1 || fallar "no encontré 'age'. Instálalo: https://github.com/FiloSottile/age"
[ -f "$DIR_RAIZ/.sops.yaml" ] || fallar "no encontré $DIR_RAIZ/.sops.yaml — ese archivo define qué llave age usar"
[ -f "$ARCHIVO_PLANTILLA" ] || fallar "no encontré $ARCHIVO_PLANTILLA"

if [ -f "$ARCHIVO_CIFRADO" ]; then
    read -r -p "$ARCHIVO_CIFRADO ya existe. ¿Sobrescribirlo? [s/N] " respuesta
    case "$respuesta" in
        [sS]|[sS][iI]) ;;
        *) echo "Cancelado, no se modificó nada."; exit 0 ;;
    esac
fi

echo "Esto va a pedirte tu GROQ_API_KEY y dejarla cifrada en:"
echo "  $ARCHIVO_CIFRADO"
echo "(gratis en https://console.groq.com/keys — el valor no se mostrará en pantalla)"
echo

read -r -s -p "GROQ_API_KEY: " api_key
echo
[ -n "$api_key" ] || fallar "la API key no puede estar vacía"

case "$api_key" in
    gsk_*) ;;
    *) echo "Aviso: las API keys de Groq normalmente empiezan con 'gsk_'. Sigo de todas formas." ;;
esac

printf 'GROQ_API_KEY=%s\n' "$api_key" > "$ARCHIVO_CIFRADO"
unset api_key

sops --encrypt --in-place "$ARCHIVO_CIFRADO"

echo
echo "Listo. $ARCHIVO_CIFRADO quedó cifrado y es seguro de commitear:"
echo
grep '^GROQ_API_KEY=' "$ARCHIVO_CIFRADO"
echo
echo "Para usarla:"
echo "  export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt"
echo "  sops exec-env $ARCHIVO_CIFRADO \"uv run clima.py '...'\""

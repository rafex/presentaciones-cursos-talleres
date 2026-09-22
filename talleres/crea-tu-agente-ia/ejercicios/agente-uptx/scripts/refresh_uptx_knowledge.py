"""Actualiza una copia de texto de páginas públicas de la UPTx.

El Markdown principal se mantiene revisado y versionado. Este script sirve como
punto de partida para detectar cambios antes de editar la base de conocimiento.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URLS = {
    "Programas Educativos": "https://uptlax.edu.mx/programas-educativos/",
    "Oferta Educativa": "https://uptlax.edu.mx/oferta-educativa/",
    "Servicios Escolares": "https://uptlax.edu.mx/servicio-escolares/",
}


def extract_page(title: str, url: str) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    return f"## {title}\n\nFuente: {url}\n\n{text[:12000]}\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).parents[1] / "knowledge" / "uptx-site-snapshot.md")
    args = parser.parse_args()
    sections = [f"# Snapshot UPTx\n\nFecha de extracción: {date.today().isoformat()}\n"]
    for title, url in URLS.items():
        try:
            sections.append(extract_page(title, url))
        except requests.RequestException as error:
            sections.append(f"## {title}\n\nNo se pudo consultar {url}: {error}\n")
    args.output.write_text("\n".join(sections), encoding="utf-8")
    print(f"Snapshot guardado en {args.output}")


if __name__ == "__main__":
    main()

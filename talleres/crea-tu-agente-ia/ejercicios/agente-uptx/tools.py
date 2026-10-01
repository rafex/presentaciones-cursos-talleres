"""Herramientas del agente y sus esquemas de function calling.

Cada función de este archivo puede ejecutarse de forma independiente. La lista
``TOOLS`` describe esas funciones para Groq y ``FUNCTIONS`` permite convertir
el nombre que devuelve el modelo en una función Python real.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from retriever import STOPWORDS, UPTxRetriever, normalize

# Todas las rutas se resuelven desde el directorio del ejercicio para que el
# agente funcione igual desde aquí o desde la raíz del repositorio.
ROOT = Path(__file__).resolve().parent
retriever = UPTxRetriever(ROOT / "knowledge" / "uptx.md")
ALLOWED_UPTX_HOST = "uptlax.edu.mx"
PAGE_TIMEOUT = 20
MAX_SOURCE_CHARS = 9000


def _is_official_uptx_url(url: str) -> bool:
    """Indica si una URL pertenece al sitio oficial de la UPTx.

    La restricción evita que una respuesta del modelo convierta la tool en un
    navegador arbitrario. También se aplica después de las redirecciones para
    impedir que un enlace oficial termine consultando otro dominio.
    """

    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    return parsed.scheme == "https" and (
        hostname == ALLOWED_UPTX_HOST or hostname.endswith(f".{ALLOWED_UPTX_HOST}")
    )


def _clean_source_url(url: str) -> str:
    """Quita puntuación que suele quedar pegada a una URL en Markdown."""

    return url.strip().strip("<>[](){}.,;:)")


def _relevant_page_lines(lines: list[str], pregunta: str) -> list[str]:
    """Ordena líneas HTML por coincidencia con la pregunta del usuario."""

    query = set(normalize(pregunta)) - STOPWORDS
    if not query:
        return lines[:40]

    scored = [
        (len(query & set(normalize(line))), -index, line)
        for index, line in enumerate(lines)
    ]
    matching = [item for item in scored if item[0] > 0]
    if not matching:
        return lines[:40]

    matching.sort(reverse=True)
    selected_indexes = {item[1] for item in matching[:30]}
    return [line for index, line in enumerate(lines) if -index in selected_indexes]


def obtener_clima(ciudad: str) -> str:
    """Obtiene el clima actual de una ciudad usando Open-Meteo.

    Primero usa el servicio de geocodificación para traducir el nombre de la
    ciudad a coordenadas. Después consulta temperatura, sensación térmica,
    humedad y viento en el endpoint de pronóstico actual.
    """

    try:
        geocoding = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ciudad, "count": 1, "language": "es", "format": "json"},
            timeout=10,
        )
        geocoding.raise_for_status()
        results = geocoding.json().get("results", [])
        if not results:
            return f"No encontré coordenadas para {ciudad}."

        location = results[0]
        forecast = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=10,
        )
        forecast.raise_for_status()
        current = forecast.json().get("current", {})
    except requests.RequestException as error:
        return f"No pude consultar el clima de {ciudad}: {error}"

    return (
        f"Clima actual en {location.get('name', ciudad)}, {location.get('country', '')}: "
        f"{current.get('temperature_2m', 'sin dato')} °C, "
        f"sensación térmica {current.get('apparent_temperature', 'sin dato')} °C, "
        f"humedad {current.get('relative_humidity_2m', 'sin dato')} %, "
        f"viento {current.get('wind_speed_10m', 'sin dato')} km/h. "
        "Fuente: https://open-meteo.com/"
    )


def consultar_uptx(pregunta: str) -> str:
    """Busca información institucional en el Markdown local de la UPTx.

    El retriever no llama a otra API: divide ``knowledge/uptx.md`` en
    fragmentos y devuelve los que mejor coinciden con la intención de la
    pregunta. Si no hay coincidencias suficientes, la función lo comunica
    para que el modelo no invente una respuesta.
    """

    matches = retriever.search(pregunta)
    if not matches:
        return (
            "No encontré información suficiente en la base UPTx local. "
            "Consulta directamente las fuentes oficiales incluidas en el Markdown."
        )

    return "\n\n---\n\n".join(f"[{match.heading}]\n{match.text}" for match in matches)


def consultar_fuente_uptx(url: str, pregunta: str = "") -> str:
    """Visita una fuente oficial de la UPTx y extrae su contenido visible.

    Esta tool no consulta el API del RAG. Usa la URL que ``consultar_uptx``
    encontró en el campo ``Fuente:`` y descarga la página oficial para
    comprobar o ampliar la información. Sólo permite HTTPS en ``uptlax.edu.mx``
    y sus subdominios oficiales.

    Args:
        url: Enlace oficial encontrado en el conocimiento local.
        pregunta: Pregunta original, usada para priorizar párrafos relevantes.
    """

    source_url = _clean_source_url(url)
    if not _is_official_uptx_url(source_url):
        return (
            "No consulté la fuente porque la URL no pertenece al dominio oficial "
            "HTTPS de la UPTx."
        )

    try:
        response = requests.get(
            source_url,
            headers={"User-Agent": "agente-uptx/1.0 (consulta educativa)"},
            timeout=PAGE_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        return f"No pude consultar la fuente oficial {source_url}: {error}"

    final_url = _clean_source_url(response.url)
    if not _is_official_uptx_url(final_url):
        return "La fuente oficial redirigió a un dominio no permitido."

    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type and "text" not in content_type:
        return (
            f"La fuente {source_url} no es una página HTML. "
            "El agente conserva el enlace para consulta manual."
        )

    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "noscript", "svg", "nav", "footer", "form"]):
        element.decompose()

    container = soup.find("main") or soup.find("article") or soup.body or soup
    lines: list[str] = []
    for element in container.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = re.sub(r"\s+", " ", element.get_text(" ", strip=True)).strip()
        if text and text not in lines:
            lines.append(text)

    selected = _relevant_page_lines(lines, pregunta)
    if not selected:
        return f"La fuente {source_url} no contiene texto visible extraíble."

    extracted = "\n".join(selected)
    return (
        f"Fuente consultada: {final_url}\n"
        f"Contenido oficial extraído:\n{extracted[:MAX_SOURCE_CHARS]}"
    )


# Este esquema es el contrato que Groq ve. Debe mantenerse sincronizado con
# las firmas de ``obtener_clima`` y ``consultar_uptx``.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Obtiene las condiciones meteorológicas actuales de una ciudad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Ciudad o municipio que se desea consultar.",
                    }
                },
                "required": ["ciudad"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_uptx",
            "description": "Consulta carreras, admisión, ciclos, cursos y reglamento de la UPTx.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pregunta": {
                        "type": "string",
                        "description": "Pregunta sobre información institucional de la UPTx.",
                    }
                },
                "required": ["pregunta"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_fuente_uptx",
            "description": (
                "Visita una URL HTTPS oficial de la UPTx encontrada por "
                "consultar_uptx y extrae el contenido visible relevante."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL oficial que apareció en una línea Fuente:.",
                    },
                    "pregunta": {
                        "type": "string",
                        "description": "Pregunta original para priorizar el contenido relevante.",
                    },
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
]

# Este mapa es el dispatcher local: el nombre elegido por el modelo determina
# qué función Python se ejecuta en ``main._execute_tool``.
FUNCTIONS = {
    "obtener_clima": obtener_clima,
    "consultar_uptx": consultar_uptx,
    "consultar_fuente_uptx": consultar_fuente_uptx,
}

"""Servidor MCP del taller: expone las tools de direcciones mexicanas.

Corre por stdio, igual que cualquier servidor MCP estandar. Esto es lo que
permite reusar las mismas tools desde dos runtimes distintos sin duplicar
codigo:

  * El agente LangGraph del taller (agente_langgraph.py), via
    langchain-mcp-adapters.
  * EtherBrain (https://github.com/rafex/ether-brain), declarando este
    mismo comando en tools.json con "type": "mcp" -- ver tools.json.example.

Arrancar en solitario (para probar con un cliente MCP cualquiera):
    uv run python -m agente_cp.mcp_server
"""

from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

from agente_cp import sepomex

mcp = FastMCP("agente-cp")


@mcp.tool()
def buscar_cp(cp: str, estado: str) -> dict:
    """Busca un Codigo Postal mexicano en el catalogo oficial de SEPOMEX.

    Devuelve las colonias/asentamientos asociados a ese CP dentro del estado
    indicado, y de donde vinieron los datos: "sqlite" (catalogo nacional
    autocontenido, lo normal), o "red"/"cache"/"fixture" si no existe
    data/sepomex.sqlite y se cayo al scraping en vivo.
    """
    coincidencias, origen = sepomex.buscar_por_cp(cp, estado)
    colonias = sorted({a.colonia for a in coincidencias})
    return {
        "cp": cp,
        "estado": sepomex.ESTADOS[sepomex.resolver_codigo_estado(estado)],
        "origen_datos": origen,
        "colonias": colonias[:20],
        "total_colonias": len(colonias),
        "municipio": coincidencias[0].municipio if coincidencias else None,
    }


@mcp.tool()
def validar_direccion(cp: str, colonia: str, estado: str) -> dict:
    """Valida si una colonia corresponde a un Codigo Postal mexicano.

    Si no coincide, sugiere las colonias reales registradas para ese CP --
    util para que el agente "repare" direcciones mal escritas por el usuario.
    """
    return sepomex.validar_direccion(cp=cp, colonia=colonia, estado=estado)


@mcp.tool()
def descargar_estado(estado: str) -> dict:
    """Fuerza una descarga fresca del catalogo de un estado (ignora cache).

    Usa esta tool cuando el usuario pida explicitamente actualizar los datos.
    """
    contenido, origen = sepomex.obtener_catalogo_estado(estado, forzar_descarga=True)
    filas = sepomex.parsear_catalogo(contenido)
    return {
        "estado": sepomex.ESTADOS[sepomex.resolver_codigo_estado(estado)],
        "origen_datos": origen,
        "registros": len(filas),
    }


@mcp.tool()
def geocodificar_direccion(direccion: str) -> dict:
    """Reto extra: geocodifica una direccion en texto libre usando Nominatim
    (OpenStreetMap), una API publica sin api key -- ver public-apis/public-apis.

    Devuelve latitud, longitud y el nombre normalizado del lugar encontrado.
    Util para cruzar el resultado contra el catalogo de SEPOMEX.
    """
    respuesta = httpx.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": direccion, "format": "json", "limit": 1, "countrycodes": "mx"},
        headers={"User-Agent": "agente-cp-taller/1.0 (workshop UPTLAX 2026)"},
        timeout=10.0,
    )
    respuesta.raise_for_status()
    resultados = respuesta.json()
    if not resultados:
        return {"encontrado": False, "direccion_buscada": direccion}
    lugar = resultados[0]
    return {
        "encontrado": True,
        "direccion_buscada": direccion,
        "nombre_normalizado": lugar["display_name"],
        "lat": lugar["lat"],
        "lon": lugar["lon"],
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

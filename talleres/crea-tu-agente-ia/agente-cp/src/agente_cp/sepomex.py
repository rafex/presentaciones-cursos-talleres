"""Cliente del catalogo nacional de Codigos Postales (Correos de Mexico / SEPOMEX).

Tres fuentes de datos, en cascada, para que el taller nunca se quede sin
respuesta:

1. **SQLite local** (`data/sepomex.sqlite`) -- catalogo nacional completo
   (~158k registros), generado una sola vez con `scripts/xml_a_sqlite.py` a
   partir del XML que publica Correos de Mexico. Es la fuente principal:
   autocontenida, sin red, instantanea.
2. **Scraping en vivo** -- si no existe el .sqlite, se simula el postback del
   formulario ASP.NET en
   https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
   (toma __VIEWSTATE/__VIEWSTATEGENERATOR/__EVENTVALIDATION de un GET previo
   y los reenvia en un POST). Sirve tambien como ejercicio de "reto extra"
   para refrescar datos.
3. **Fixture local** -- si tampoco hay red, cae a un catalogo reducido de
   Tlaxcala embebido en el repo.
"""

from __future__ import annotations

import csv
import difflib
import io
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import httpx

EXPORT_URL = "https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx"

ESTADOS = {
    "01": "Aguascalientes", "02": "Baja California", "03": "Baja California Sur",
    "04": "Campeche", "05": "Coahuila de Zaragoza", "06": "Colima", "07": "Chiapas",
    "08": "Chihuahua", "09": "Ciudad de Mexico", "10": "Durango", "11": "Guanajuato",
    "12": "Guerrero", "13": "Hidalgo", "14": "Jalisco", "15": "Mexico",
    "16": "Michoacan de Ocampo", "17": "Morelos", "18": "Nayarit", "19": "Nuevo Leon",
    "20": "Oaxaca", "21": "Puebla", "22": "Queretaro", "23": "Quintana Roo",
    "24": "San Luis Potosi", "25": "Sinaloa", "26": "Sonora", "27": "Tabasco",
    "28": "Tamaulipas", "29": "Tlaxcala", "30": "Veracruz de Ignacio de la Llave",
    "31": "Yucatan", "32": "Zacatecas",
}
NOMBRE_A_CODIGO = {v.lower(): k for k, v in ESTADOS.items()}

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CACHE_DIR = Path.home() / ".cache" / "agente-cp" / "sepomex"
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "sepomex.sqlite"

CAMPOS = [
    "d_codigo", "d_asenta", "d_tipo_asenta", "D_mnpio", "d_estado", "d_ciudad",
    "d_CP", "c_estado", "c_oficina", "c_tipo_asenta", "c_mnpio",
    "id_asenta_cpcons", "d_zona", "c_cve_ciudad", "c_CP",
]


@dataclass
class Asentamiento:
    colonia: str
    tipo: str
    municipio: str
    estado: str
    ciudad: str
    cp: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Asentamiento":
        return cls(
            colonia=row["d_asenta"],
            tipo=row["d_tipo_asenta"],
            municipio=row["D_mnpio"],
            estado=row["d_estado"],
            ciudad=row["d_ciudad"],
            cp=row["d_CP"],
        )


class SepomexError(RuntimeError):
    """El sitio de Correos de Mexico no respondio el catalogo esperado."""


def resolver_codigo_estado(estado: str) -> str:
    estado = estado.strip()
    if estado in ESTADOS:
        return estado
    codigo = NOMBRE_A_CODIGO.get(estado.lower())
    if codigo is None:
        raise SepomexError(f"Estado desconocido: {estado!r}")
    return codigo


# ---------------------------------------------------------------------------
# Fuente 1: SQLite local (autocontenida)
# ---------------------------------------------------------------------------

def _consultar_sqlite(cp: str, codigo_estado: str) -> list[Asentamiento]:
    with sqlite3.connect(DB_PATH) as conexion:
        conexion.row_factory = sqlite3.Row
        filas = conexion.execute(
            "SELECT d_asenta, d_tipo_asenta, D_mnpio, d_estado, d_ciudad, d_CP "
            "FROM codigos_postales WHERE d_CP = ? AND c_estado = ?",
            (cp, codigo_estado),
        ).fetchall()
    return [
        Asentamiento(
            colonia=f["d_asenta"], tipo=f["d_tipo_asenta"], municipio=f["D_mnpio"],
            estado=f["d_estado"], ciudad=f["d_ciudad"], cp=f["d_CP"],
        )
        for f in filas
    ]


# ---------------------------------------------------------------------------
# Fuente 2: scraping en vivo del formulario ASP.NET
# ---------------------------------------------------------------------------

def _extraer_campo_oculto(html: str, nombre: str) -> str:
    patron = rf'id="{nombre}"\s+value="([^"]*)"'
    match = re.search(patron, html)
    if not match:
        raise SepomexError(f"No se encontro el campo {nombre} en el formulario")
    return match.group(1)


def _descargar_txt_remoto(codigo_estado: str, client: httpx.Client) -> str:
    pagina = client.get(EXPORT_URL)
    pagina.raise_for_status()
    html = pagina.content.decode("latin-1")

    datos = {
        "__VIEWSTATE": _extraer_campo_oculto(html, "__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": _extraer_campo_oculto(html, "__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": _extraer_campo_oculto(html, "__EVENTVALIDATION"),
        "cboEdo": codigo_estado,
        "rblTipo": "txt",
        "btnDescarga.x": "10",
        "btnDescarga.y": "10",
    }
    respuesta = client.post(EXPORT_URL, data=datos)
    respuesta.raise_for_status()
    contenido = respuesta.content.decode("latin-1")
    lineas = contenido.splitlines()
    if len(lineas) < 2 or "|" not in lineas[1]:
        raise SepomexError("La respuesta no parece un catalogo delimitado por '|'")
    return contenido


def _ruta_fixture(codigo_estado: str) -> Path:
    return FIXTURES_DIR / f"{codigo_estado}_{ESTADOS[codigo_estado].lower().replace(' ', '_')}.txt"


def _ruta_cache(codigo_estado: str) -> Path:
    return CACHE_DIR / f"{codigo_estado}.txt"


def obtener_catalogo_estado(estado: str, *, forzar_descarga: bool = False) -> tuple[str, str]:
    """Descarga (o lee de cache/fixture) el catalogo TXT de un estado.

    Esta funcion ignora deliberadamente el .sqlite local -- la usa la tool
    `descargar_estado` para refrescar datos via scraping, y sirve de fallback
    de `buscar_por_cp` cuando no existe `data/sepomex.sqlite`.

    origen es "cache", "red" o "fixture".
    """
    codigo = resolver_codigo_estado(estado)
    cache = _ruta_cache(codigo)

    if not forzar_descarga and cache.exists():
        return cache.read_text(encoding="utf-8"), "cache"

    try:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            contenido = _descargar_txt_remoto(codigo, client)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(contenido, encoding="utf-8")
        return contenido, "red"
    except (httpx.HTTPError, SepomexError):
        fixture = _ruta_fixture(codigo)
        if fixture.exists():
            return fixture.read_text(encoding="utf-8"), "fixture"
        raise


def parsear_catalogo(contenido_txt: str) -> list[dict[str, str]]:
    lineas = contenido_txt.splitlines()
    # La primera linea es el aviso legal; la segunda es el encabezado real.
    inicio_datos = 1 if lineas and lineas[0].split("|", 1)[0] != CAMPOS[0] else 0
    lector = csv.DictReader(io.StringIO("\n".join(lineas[inicio_datos:])), delimiter="|")
    return [fila for fila in lector if fila.get("d_CP")]


# ---------------------------------------------------------------------------
# API publica: cascada sqlite -> red/cache -> fixture
# ---------------------------------------------------------------------------

def buscar_por_cp(cp: str, estado: str) -> tuple[list[Asentamiento], str]:
    """Busca un CP. Devuelve (coincidencias, origen).

    origen: "sqlite" (autocontenido, catalogo nacional completo), "cache",
    "red" o "fixture" -- estos tres ultimos solo si no existe el .sqlite.
    """
    codigo = resolver_codigo_estado(estado)

    if DB_PATH.exists():
        return _consultar_sqlite(cp, codigo), "sqlite"

    contenido, origen = obtener_catalogo_estado(estado)
    filas = parsear_catalogo(contenido)
    coincidencias = [Asentamiento.from_row(f) for f in filas if f["d_CP"] == cp]
    return coincidencias, origen


def validar_direccion(cp: str, colonia: str, estado: str) -> dict:
    """Revisa si `colonia` corresponde al CP dado y sugiere alternativas si no.

    Esta es la tool de "reparar direcciones": el agente la usa para detectar
    cuando un usuario escribio mal la colonia o el CP no existe en el catalogo.
    """
    coincidencias, origen = buscar_por_cp(cp, estado)
    if not coincidencias:
        return {
            "valido": False,
            "razon": f"El CP {cp} no existe en el catalogo de {ESTADOS[resolver_codigo_estado(estado)]}",
            "sugerencias": [],
            "origen_datos": origen,
        }

    colonia_norm = colonia.strip().lower()
    exactas = [a for a in coincidencias if a.colonia.strip().lower() == colonia_norm]
    if exactas:
        return {
            "valido": True,
            "razon": "La colonia coincide con el CP",
            "sugerencias": [],
            "origen_datos": origen,
        }

    colonias_unicas = sorted({a.colonia for a in coincidencias})
    cercanas = difflib.get_close_matches(colonia, colonias_unicas, n=8, cutoff=0.3)
    return {
        "valido": False,
        "razon": f"El CP {cp} no tiene una colonia llamada '{colonia}'",
        "sugerencias": cercanas or colonias_unicas[:8],
        "total_colonias_en_cp": len(colonias_unicas),
        "origen_datos": origen,
    }

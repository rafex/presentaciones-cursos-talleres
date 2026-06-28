"""Convierte el catalogo nacional de Codigos Postales (XML de SEPOMEX/Correos
de Mexico) a una base SQLite autocontenida.

El XML se descarga manualmente desde
https://www.correosdemexico.gob.mx/SSLServicios/abcCP/actCPcons.aspx
("CPdescarga.xml", ~67 MB, ~158k registros). Es un dataset .NET ("NewDataSet")
de una sola linea: no cabe en memoria como DOM, asi que se parsea en streaming
con iterparse.

Uso:
    uv run python scripts/xml_a_sqlite.py /ruta/a/CPdescarga.xml
    uv run python scripts/xml_a_sqlite.py /ruta/a/CPdescarga.xml data/sepomex.sqlite
"""

from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path
from xml.etree.ElementTree import iterparse

CAMPOS = [
    "d_codigo", "d_asenta", "d_tipo_asenta", "D_mnpio", "d_estado", "d_ciudad",
    "d_CP", "c_estado", "c_oficina", "c_CP", "c_tipo_asenta", "c_mnpio",
    "id_asenta_cpcons", "d_zona", "c_cve_ciudad",
]

DDL = f"""
CREATE TABLE IF NOT EXISTS codigos_postales (
    {", ".join(f"{c} TEXT" for c in CAMPOS)}
);
CREATE INDEX IF NOT EXISTS idx_cp_d_cp ON codigos_postales (d_CP);
CREATE INDEX IF NOT EXISTS idx_cp_estado ON codigos_postales (c_estado);
"""

INSERT = f"""
INSERT INTO codigos_postales ({", ".join(CAMPOS)})
VALUES ({", ".join("?" for _ in CAMPOS)})
"""

LOTE = 5000


def filas_xml(ruta_xml: Path):
    """Genera un dict por cada <table> del NewDataSet, sin cargar todo a RAM."""
    fila: dict[str, str] = {}
    for evento, elem in iterparse(ruta_xml, events=("start", "end")):
        tag = elem.tag.rsplit("}", 1)[-1]  # quita el namespace "NewDataSet"
        if evento == "end" and tag in CAMPOS:
            fila[tag] = (elem.text or "").strip()
            elem.clear()
        elif evento == "end" and tag == "table":
            yield fila
            fila = {}
            elem.clear()


def convertir(ruta_xml: Path, ruta_db: Path) -> None:
    ruta_db.parent.mkdir(parents=True, exist_ok=True)
    if ruta_db.exists():
        ruta_db.unlink()

    conexion = sqlite3.connect(ruta_db)
    conexion.executescript(DDL)

    inicio = time.monotonic()
    lote: list[tuple] = []
    total = 0
    for fila in filas_xml(ruta_xml):
        lote.append(tuple(fila.get(c, "") for c in CAMPOS))
        if len(lote) >= LOTE:
            conexion.executemany(INSERT, lote)
            total += len(lote)
            lote.clear()
            print(f"\r{total} filas...", end="", flush=True)
    if lote:
        conexion.executemany(INSERT, lote)
        total += len(lote)

    conexion.commit()
    conexion.execute("VACUUM")
    conexion.close()

    segundos = time.monotonic() - inicio
    print(f"\r{total} filas insertadas en {ruta_db} ({segundos:.1f}s)")
    print(f"Tamano final: {ruta_db.stat().st_size / 1_048_576:.1f} MB")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ruta_xml = Path(sys.argv[1]).expanduser()
    ruta_db = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else (
        Path(__file__).resolve().parents[1] / "data" / "sepomex.sqlite"
    )
    if not ruta_xml.exists():
        print(f"No existe el archivo: {ruta_xml}")
        sys.exit(1)
    convertir(ruta_xml, ruta_db)


if __name__ == "__main__":
    main()

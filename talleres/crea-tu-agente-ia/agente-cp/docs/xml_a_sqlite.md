# `scripts/xml_a_sqlite.py` — del XML oficial a SQLite

Archivo: [`scripts/xml_a_sqlite.py`](../scripts/xml_a_sqlite.py)

Convierte el catálogo nacional que publica Correos de México (XML, ~67 MB,
formato `NewDataSet` de .NET) en `data/sepomex.sqlite`. Se corre **una sola
vez** — el resultado ya está commiteado en el repo, así que nadie en el
taller necesita ejecutarlo. Documentado aquí para quien quiera regenerarlo
o entender de dónde salió el archivo.

```bash
uv run python scripts/xml_a_sqlite.py /ruta/a/CPdescarga.xml
```

## El problema: 67 MB en una sola línea

El XML que entrega Correos de México no tiene saltos de línea — es un
único `<NewDataSet>` con ~158,539 elementos `<table>` hijos, cada uno con
15 campos. Cargarlo completo con `xml.etree.ElementTree.parse()`
construiría un árbol DOM de todo el documento en memoria antes de poder
leer una sola fila.

La solución es `iterparse`, que emite eventos (`start`, `end`) a medida
que el parser avanza por el archivo, sin necesidad de tenerlo completo en
RAM:

```python
def filas_xml(ruta_xml: Path):
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
```

Puntos clave:

- `elem.tag` viene con el namespace completo, algo como
  `{NewDataSet}d_asenta`. `tag.rsplit("}", 1)[-1]` se queda solo con
  `d_asenta` — es más simple que registrar el namespace formalmente para
  un script de un solo uso.
- `elem.clear()` libera la memoria del elemento ya procesado. Sin esto,
  aunque uses `iterparse`, ElementTree seguiría acumulando todo el árbol
  en memoria y el ahorro sería ilusorio.
- Cada `<table>` completo dispara un `yield fila` — el generador entrega
  una fila a la vez, así que el resto del script (la inserción a SQLite)
  tampoco necesita tener todas las filas en memoria simultáneamente.

Resultado medido: las 158,539 filas se parsean e insertan en **menos de 2
segundos**, con uso de memoria constante independientemente del tamaño del
XML de entrada.

## El esquema SQLite

```python
CAMPOS = [
    "d_codigo", "d_asenta", "d_tipo_asenta", "D_mnpio", "d_estado", "d_ciudad",
    "d_CP", "c_estado", "c_oficina", "c_CP", "c_tipo_asenta", "c_mnpio",
    "id_asenta_cpcons", "d_zona", "c_cve_ciudad",
]
```

Son los mismos 15 campos que define el propio XML (visibles en su
`xsd:schema` interno) — el script no inventa ni renombra columnas, para
que cualquiera pueda cotejar la base contra el archivo fuente.

```sql
CREATE TABLE codigos_postales (d_codigo TEXT, d_asenta TEXT, ...);
CREATE INDEX idx_cp_d_cp ON codigos_postales (d_CP);
CREATE INDEX idx_cp_estado ON codigos_postales (c_estado);
```

Todas las columnas son `TEXT` deliberadamente — `d_codigo` y `d_CP` tienen
ceros a la izquierda ("01001") que se perderían si se guardaran como
entero. Los dos índices son los que `sepomex.py` necesita para sus
consultas (`WHERE d_CP = ? AND c_estado = ?`); sin ellos, cada búsqueda
sería un recorrido completo de 158k filas en vez de un lookup indexado.

## Inserción por lotes, no fila por fila

```python
LOTE = 5000
...
lote.append(tuple(fila.get(c, "") for c in CAMPOS))
if len(lote) >= LOTE:
    conexion.executemany(INSERT, lote)
    lote.clear()
```

`executemany` con lotes de 5,000 filas evita el overhead de hacer ~158,539
viajes individuales a SQLite (cada `INSERT` suelto implicaría su propio
ciclo de parseo de SQL y, sin una transacción explícita, su propio commit
implícito). Es la diferencia entre ~2 segundos y varios minutos para este
volumen de datos.

Al final, `VACUUM` reconstruye el archivo `.sqlite` de forma compacta —
reduce el tamaño final y desfragmenta las páginas usadas durante la
inserción masiva.

## Por qué no se versiona el XML, solo el `.sqlite`

El XML de origen (~67 MB) no está en el repo — solo el resultado de la
conversión (~20 MB, porque SQLite indexado y sin la verbosidad de XML pesa
menos que el original). Si Correos de México actualiza su catálogo, el
flujo es: descargar el XML nuevo desde
[actCPcons.aspx](https://www.correosdemexico.gob.mx/SSLServicios/abcCP/actCPcons.aspx),
correr este script de nuevo, y commitear el `.sqlite` regenerado.

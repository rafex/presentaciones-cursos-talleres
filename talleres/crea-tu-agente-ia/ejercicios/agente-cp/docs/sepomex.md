# `sepomex.py` — la cascada de datos

Archivo: [`src/agente_cp/sepomex.py`](../src/agente_cp/sepomex.py)

Este módulo no sabe nada de agentes, MCP ni LLMs. Su único trabajo es
responder dos preguntas — "¿qué colonias tiene este CP?" y "¿esta colonia
corresponde a este CP?" — usando la mejor fuente de datos disponible en
ese momento, y diciendo siempre de dónde vino la respuesta.

## Los tres niveles, en orden de preferencia

### 1. SQLite local (`DB_PATH`, línea 49)

```python
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "sepomex.sqlite"
```

`parents[2]` sube de `sepomex.py` → `agente_cp/` → `src/` → raíz del
proyecto, donde vive `data/sepomex.sqlite`. Es el catálogo nacional
completo (158,539 filas), generado una sola vez por
[`xml_a_sqlite.py`](./xml_a_sqlite.md) y commiteado al repo.

`_consultar_sqlite(cp, codigo_estado)` abre la conexión, activa
`sqlite3.Row` (para acceder a columnas por nombre en vez de por índice) y
ejecuta una consulta indexada:

```sql
SELECT d_asenta, d_tipo_asenta, D_mnpio, d_estado, d_ciudad, d_CP
FROM codigos_postales
WHERE d_CP = ? AND c_estado = ?
```

Los `?` son parámetros enlazados (no f-strings) — esto evita inyección SQL
aunque aquí el riesgo sea bajo, es el hábito correcto. La tabla tiene
índices en `d_CP` y `c_estado` (ver [xml_a_sqlite.md](./xml_a_sqlite.md)),
así que la consulta es instantánea incluso sobre 158k filas.

Esta es la fuente que se usa **siempre que el archivo existe** — que es el
caso normal del taller. No hay red, no hay parsing de HTML, no hay
sorpresas.

### 2. Scraping en vivo (si no existe el `.sqlite`)

Si `DB_PATH.exists()` es falso, `buscar_por_cp` cae a
`obtener_catalogo_estado`, que reproduce el formulario ASP.NET de
[`CodigoPostal_Exportar.aspx`](https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx):

1. **GET** a la página — trae tres campos ocultos que ASP.NET WebForms usa
   para validar que el siguiente POST viene de un formulario real:
   `__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__EVENTVALIDATION`.
   `_extraer_campo_oculto` los saca con una regex simple:
   ```python
   patron = rf'id="{nombre}"\s+value="([^"]*)"'
   ```
2. **POST** a la misma URL, con esos tres campos más:
   - `cboEdo`: el código de 2 dígitos del estado (`"29"` para Tlaxcala).
   - `rblTipo`: `"txt"` — el formulario también ofrece Excel y XML.
   - `btnDescarga.x` / `btnDescarga.y`: el botón de envío es una
     `<input type="image">`, así que ASP.NET espera coordenadas de clic
     en vez de un nombre de botón normal. Cualquier par de números sirve.
3. La respuesta es texto plano separado por `|`, codificado en
   **latin-1** (no UTF-8 — el sitio es de la era .NET 2.0).

Este flujo se validó manualmente contra el sitio real antes de escribirlo
(ver el historial de la conversación del taller) — no es teoría, es lo que
el formulario efectivamente exige.

`obtener_catalogo_estado` también mantiene una **cache en disco**
(`~/.cache/agente-cp/sepomex/<codigo>.txt`) para no volver a pegarle al
sitio en cada pregunta dentro de la misma sesión de trabajo. `forzar_descarga=True`
(usada por la tool `descargar_estado`) la ignora a propósito.

### 3. Fixture local (si tampoco hay red)

Si el GET o el POST fallan (`httpx.HTTPError`) o el HTML no tiene los
campos esperados (`SepomexError`), cae a
`src/agente_cp/fixtures/29_tlaxcala.txt` — una captura real (60 filas) del
catálogo de Tlaxcala, para que la demo en vivo nunca se quede sin
respuesta aunque el sitio de Correos de México esté caído.

```python
except (httpx.HTTPError, SepomexError):
    fixture = _ruta_fixture(codigo)
    if fixture.exists():
        return fixture.read_text(encoding="utf-8"), "fixture"
    raise
```

Si tampoco hay fixture para ese estado, la excepción se vuelve a lanzar —
no hay un cuarto nivel que invente datos.

## `buscar_por_cp`: el punto de entrada único

```python
def buscar_por_cp(cp: str, estado: str) -> tuple[list[Asentamiento], str]:
    codigo = resolver_codigo_estado(estado)
    if DB_PATH.exists():
        return _consultar_sqlite(cp, codigo), "sqlite"
    contenido, origen = obtener_catalogo_estado(estado)
    filas = parsear_catalogo(contenido)
    coincidencias = [Asentamiento.from_row(f) for f in filas if f["d_CP"] == cp]
    return coincidencias, origen
```

Todo lo demás en el módulo (la tool MCP `buscar_cp`, `validar_direccion`)
llama a esta función — nunca a `_consultar_sqlite` o a
`obtener_catalogo_estado` directamente para buscar un CP. Es la única
puerta de entrada, y siempre devuelve `(resultados, origen)` para que quien
la llama pueda ser transparente sobre la procedencia del dato.

## `validar_direccion`: la tool de "reparar direcciones"

Recibe un CP, una colonia que el usuario escribió, y un estado. Tres casos:

1. **El CP no existe** en ninguna fuente → `valido: False`, sin sugerencias.
2. **La colonia coincide exactamente** (comparación case-insensitive) →
   `valido: True`.
3. **No coincide** → usa `difflib.get_close_matches` sobre el conjunto de
   colonias reales de ese CP para sugerir la más parecida por similitud de
   texto (no es IA, es comparación de cadenas — útil para typos como
   "Tlaxcala Cento" → "Tlaxcala Centro"). Si ninguna pasa el umbral de
   similitud (`cutoff=0.3`), devuelve las primeras 8 colonias del CP de
   todos modos, para que el agente tenga algo que ofrecer.

Cada rama incluye `origen_datos`, heredado de `buscar_por_cp`, para que la
respuesta del agente pueda decir "esto viene del catálogo local" en vez de
presentar todo como si fuera igualmente confiable.

## Por qué `ESTADOS` no lleva acentos

`ESTADOS` mapea código de 2 dígitos → nombre de estado sin acentos
(`"Mexico"`, no `"México"`). Es una elección deliberada para que
`resolver_codigo_estado` pueda aceptar lo que el usuario escriba sin
preocuparse por normalización Unicode de acentos — el costo es que el
nombre "bonito" que se le devuelve al usuario en las respuestas tampoco
lleva acentos. Para un taller esto es aceptable; en producción valdría la
pena usar `unicodedata.normalize` para aceptar ambas formas y mostrar el
nombre oficial correctamente acentuado.

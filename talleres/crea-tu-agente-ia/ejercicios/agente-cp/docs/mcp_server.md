# `mcp_server.py` — las tools como protocolo

Archivo: [`src/agente_cp/mcp_server.py`](../src/agente_cp/mcp_server.py)

Este archivo no implementa lógica de negocio — solo **envuelve**
`sepomex.py` (y una llamada HTTP de bonus) como tools que cualquier
cliente MCP puede descubrir e invocar.

## `FastMCP`: de función Python a tool MCP

```python
mcp = FastMCP("agente-cp")

@mcp.tool()
def buscar_cp(cp: str, estado: str) -> dict:
    """Busca un Codigo Postal mexicano en el catalogo oficial de SEPOMEX. ..."""
    ...
```

`FastMCP` (parte del SDK oficial `mcp`) genera automáticamente, a partir
de la firma de la función:

- El **nombre** de la tool (`buscar_cp`, el nombre de la función).
- El **`input_schema`** (JSON Schema) a partir de los type hints —
  `cp: str, estado: str` se vuelve un objeto con dos propiedades `string`
  requeridas. Esto es exactamente lo mismo que escribirías a mano en un
  `tools.json` (ver [ether-brain.md](./ether-brain.md)), pero derivado del
  código en vez de mantenido por separado.
- La **descripción** que el modelo lee para decidir cuándo usar la tool:
  el *docstring* de la función. Por eso cada docstring aquí está escrito
  pensando en el LLM como lector, no solo en quien lee el código.

`mcp.run(transport="stdio")` (al final del archivo) levanta un servidor
que lee/escribe el protocolo MCP por `stdin`/`stdout` — no abre ningún
puerto de red. Quien lo usa lo arranca como subproceso (ver
[agente_langgraph.md](./agente_langgraph.md)).

## Las 4 tools

### `buscar_cp(cp, estado)`

Llama a `sepomex.buscar_por_cp` (la única puerta de entrada del módulo de
datos) y da forma a la respuesta para el modelo:

```python
coincidencias, origen = sepomex.buscar_por_cp(cp, estado)
colonias = sorted({a.colonia for a in coincidencias})
return {
    "cp": cp, "estado": ..., "origen_datos": origen,
    "colonias": colonias[:20], "total_colonias": len(colonias),
    "municipio": coincidencias[0].municipio if coincidencias else None,
}
```

Dos detalles deliberados:

- `colonias[:20]` — algunos CP urbanos grandes (el centro de una ciudad)
  tienen 100+ colonias asociadas. Devolver la lista completa inflaría el
  contexto del LLM sin necesidad; se manda un total (`total_colonias`)
  para que el modelo sepa que hay más si las necesita.
- `origen_datos` siempre viaja en la respuesta — es la forma en que el
  agente puede decirle al usuario "esto viene del catálogo local" o
  avisar si tuvo que recurrir al fixture de respaldo.

### `validar_direccion(cp, colonia, estado)`

Delegación directa a `sepomex.validar_direccion` — toda la lógica de
"¿coincide? ¿qué tan parecido es lo más cercano?" vive en `sepomex.py`
(ver [sepomex.md](./sepomex.md)). Esta tool es deliberadamente una sola
línea: el servidor MCP es una capa de transporte, no de lógica.

### `descargar_estado(estado)`

```python
contenido, origen = sepomex.obtener_catalogo_estado(estado, forzar_descarga=True)
```

A diferencia de `buscar_cp`, esta tool llama a `obtener_catalogo_estado`
directamente (no a `buscar_por_cp`) — es intencional: existe para forzar
un refresco vía scraping en vivo, ignorando tanto el `.sqlite` como la
cache en disco. Es la tool que un agente usaría si el usuario dice
explícitamente "actualiza los datos de Tlaxcala".

### `geocodificar_direccion(direccion)` — el reto extra

La única tool que no toca `sepomex.py` en absoluto. Llama directamente a
[Nominatim](https://nominatim.openstreetmap.org/), el servicio de
geocodificación de OpenStreetMap — una API pública real, sin API key,
tomada de la lista [public-apis/public-apis](https://github.com/public-apis/public-apis).

```python
httpx.get(
    "https://nominatim.openstreetmap.org/search",
    params={"q": direccion, "format": "json", "limit": 1, "countrycodes": "mx"},
    headers={"User-Agent": "agente-cp-taller/1.0 (workshop UPTLAX 2026)"},
    timeout=10.0,
)
```

El header `User-Agent` no es decorativo: la [política de uso de
Nominatim](https://operations.osmfoundation.org/policies/nominatim/) exige
identificar la aplicación que hace la petición; sin un `User-Agent`
descriptivo el servicio puede rechazar la llamada. `countrycodes=mx` acota
la búsqueda a México para evitar falsos positivos con nombres de lugares
repetidos en otros países.

Esta tool es la plantilla para el ejercicio "agrega una tool con una API
pública" de las slides — copiar este patrón (función → `@mcp.tool()` →
docstring claro) es todo lo que hace falta para añadir una nueva.

## Por qué cada tool devuelve un `dict` y no un objeto Python

MCP serializa los resultados a JSON para mandarlos de vuelta al cliente.
Devolver `dict`s con tipos primitivos (`str`, `int`, `bool`, listas) evita
que `FastMCP` tenga que adivinar cómo serializar una `dataclass` como
`Asentamiento` — el límite del protocolo (texto/JSON) se respeta
explícitamente en el código, en vez de depender de magia de serialización.

# `tools.json` — una API pública convertida en tool, sin código

Archivo: [`tools.json`](../tools.json)

## El mecanismo: `ExternalToolLoader` + `HttpProxyTool`

Al arrancar, ether-brain busca un `tools.json` en el directorio de trabajo
(o en la ruta de `AGENT_TOOLS_FILE`). Por cada entrada con `"type": "http"`,
instancia un `HttpProxyTool` — una clase Java genérica que ya viene
incluida en el runtime — configurada con los datos de esa entrada. No hay
que escribir, compilar ni cargar ninguna clase nueva.

```
tools.json  ──→  ExternalToolLoader  ──→  HttpProxyTool (x2)  ──→  AgentLoop
```

## Las dos tools, explicadas

### `geocodificar_ciudad`

```json
{
  "type":        "http",
  "name":        "geocodificar_ciudad",
  "endpoint":    "https://geocoding-api.open-meteo.com/v1/search?count=1&language=es&format=json",
  "method":      "GET",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string", "description": "..."}
    },
    "required": ["name"]
  }
}
```

Cuando el modelo decide llamar `geocodificar_ciudad(name="Tlaxcala")`,
`HttpProxyTool.execute()` hace esto (ver el código real en
[`HttpProxyTool.java`](https://github.com/rafex/ether-brain/blob/main/ether-brain/ether-brain-tools-local/src/main/java/dev/rafex/etherbrain/tools/local/HttpProxyTool.java)):

```java
if ("GET".equals(method)) {
    JsonNode args = mapper.readTree(body);          // {"name": "Tlaxcala"}
    StringBuilder qs = new StringBuilder(endpoint.contains("?") ? "&" : "?");
    args.fields().forEachRemaining(e ->
            qs.append(e.getKey()).append("=").append(e.getValue().asText()).append("&"));
    req.uri(URI.create(endpoint + qs.toString().replaceAll("&$", "")));
    req.GET();
}
```

Es decir: **los argumentos que el modelo pasa se anexan tal cual como query
params** sobre el `endpoint` ya configurado. Por eso el `endpoint` de esta
tool ya incluye `?count=1&language=es&format=json` como parte fija de la
URL — el código solo añade `&name=Tlaxcala` al final. El resultado es:

```
https://geocoding-api.open-meteo.com/v1/search?count=1&language=es&format=json&name=Tlaxcala
```

Esto solo funciona porque el nombre del campo en `input_schema`
(`"name"`) coincide exactamente con el nombre del query param que espera
la API real de Open-Meteo. Si la API esperara un nombre distinto, este
tipo de tool no podría adaptarlo — para eso existe el tipo `"subprocess"`
con placeholders `${arg}`, que sí permite remapear nombres.

### `clima_actual`

Mismo patrón, con `latitude` y `longitude` como query params sobre
`https://api.open-meteo.com/v1/forecast?current_weather=true&timezone=auto`.

El modelo encadena las dos: usa el `latitude`/`longitude` que le devolvió
`geocodificar_ciudad` como entrada de `clima_actual`. Esta cadena de dos
llamadas — no una sola tool "todo en uno" — es deliberada: demuestra que
el agente puede **razonar sobre el orden** de las herramientas a partir de
sus descripciones (`"Usa esta tool ANTES de clima_actual..."`), no solo
ejecutar un script fijo.

## Por qué GET y no POST

`HttpProxyTool` por defecto manda `POST` con los argumentos como JSON
body — pensado para APIs propias o microservicios internos. Open-Meteo
(como casi cualquier API pública de solo lectura) espera `GET` con query
params, así que ambas tools declaran `"method": "GET"` explícitamente.

## Probarlas sin gastar una llamada al LLM

```bash
LLM_TYPE=demo java -jar ether-brain-cli.jar "hola"
```

`LLM_TYPE=demo` activa `DemoModelClient` — un cliente determinista incluido
en ether-brain que no llama a ningún proveedor real. No invoca nuestras
tools (solo conoce las tools internas `echo`/`current_time`), pero sí
confirma en el log de arranque que `tools.json` se parseó sin errores:

```
[EtherBrain] tool http: geocodificar_ciudad → https://geocoding-api.open-meteo.com/v1/search?...
[EtherBrain] tool http: clima_actual → https://api.open-meteo.com/v1/forecast?...
[EtherBrain] 2 tool(s) externas cargadas desde tools.json
```

Para probar las APIs en sí (sin ether-brain ni LLM de por medio), `curl`
directo es más rápido:

```bash
curl "https://geocoding-api.open-meteo.com/v1/search?count=1&language=es&format=json&name=Tlaxcala"
curl "https://api.open-meteo.com/v1/forecast?current_weather=true&timezone=auto&latitude=19.32&longitude=-98.24"
```

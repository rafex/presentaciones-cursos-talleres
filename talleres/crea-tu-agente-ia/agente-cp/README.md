# agente-cp

Proyecto del taller **"Cómo crear tu propio agente de IA usando solo software libre"**
(Foro de Tecnologías de la Información y Software Libre 2026, UPTLAX).

Un agente que valida y repara direcciones mexicanas contra el catálogo oficial
de Códigos Postales de Correos de México (SEPOMEX), construido con:

- **Python + [uv](https://docs.astral.sh/uv/)** para el entorno y dependencias.
- **SQLite autocontenido** — el catálogo nacional completo (~158k registros,
  20 MB) vive en `data/sepomex.sqlite`, generado una sola vez desde el XML
  oficial. El taller funciona sin internet.
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** para el ciclo del agente (modelo → tools → modelo).
- **[Groq](https://console.groq.com/)** como proveedor del LLM.
- **[MCP](https://modelcontextprotocol.io/)** para exponer las tools — el mismo
  servidor MCP lo puede usar este agente o
  [ether-brain](https://github.com/rafex/ether-brain) (runtime de agentes en Java).

## Setup

```bash
uv sync
cp .env.example .env
# edita .env y pon tu GROQ_API_KEY (gratis en https://console.groq.com/keys)
```

## Uso

```bash
uv run agente-cp "¿La colonia Tlaxcala Centro corresponde al CP 90001?"
uv run agente-cp "Dame las colonias del CP 90001 en Tlaxcala"
uv run agente-cp "Geocodifica Av. Independencia, Tlaxcala de Xicohténcatl"
```

Probar solo el servidor MCP (sin LangGraph ni Groq), por ejemplo con el
inspector oficial:

```bash
npx @modelcontextprotocol/inspector uv run python -m agente_cp.mcp_server
```

## Cómo está armado

```
data/
  sepomex.sqlite         # catalogo nacional completo (158k filas, 20 MB)
scripts/
  xml_a_sqlite.py         # convierte el XML oficial de SEPOMEX a sqlite
src/agente_cp/
  sepomex.py             # cascada: sqlite -> scraping en vivo -> fixture
  mcp_server.py          # servidor MCP: buscar_cp, validar_direccion,
                          #   descargar_estado, geocodificar_direccion (bonus)
  agente_langgraph.py    # grafo LangGraph (Groq) que consume las tools MCP
  cli.py                 # entrypoint: `uv run agente-cp "..."`
  fixtures/              # catálogo reducido de Tlaxcala, ultimo respaldo
```

### Las tres fuentes de datos, en cascada

1. **`data/sepomex.sqlite`** — fuente principal. Autocontenida, sin red,
   instantánea. Se genera una sola vez con:
   ```bash
   uv run python scripts/xml_a_sqlite.py /ruta/a/CPdescarga.xml
   ```
   El XML se descarga manualmente desde
   [actCPcons.aspx](https://www.correosdemexico.gob.mx/SSLServicios/abcCP/actCPcons.aspx)
   ("Descarga CP_CONS y Códigos Postales"). El `.sqlite` resultante ya está
   commiteado en el repo — no necesitas regenerarlo para el taller.
2. **Scraping en vivo** — si borras o no existe `data/sepomex.sqlite`,
   `sepomex.py` cae a simular el postback del formulario ASP.NET de
   [CodigoPostal_Exportar.aspx](https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx):
   toma `__VIEWSTATE`/`__VIEWSTATEGENERATOR`/`__EVENTVALIDATION` de un GET y
   los reenvía en un POST junto con el estado elegido.
3. **Fixture local** (`fixtures/29_tlaxcala.txt`) — si tampoco hay red, usa
   un catálogo reducido de Tlaxcala embebido en el repo. La demo nunca se
   queda sin respuesta.

Cada respuesta del agente incluye `origen_datos` (`sqlite`, `red`, `cache` o
`fixture`) para que sea explícito de dónde vino la información.

## Reusar las tools en ether-brain

El mismo servidor MCP funciona como tool externa de
[ether-brain](https://github.com/rafex/ether-brain) sin escribir Java:
copia `tools.json.example` a `tools.json`, ajusta la ruta absoluta y arranca
ether-brain con `LLM_TYPE=openai`, `LLM_URL=https://api.groq.com`,
`LLM_TOKEN=<tu GROQ_API_KEY>`. Mismas tools, dos runtimes distintos.

## Reto extra

Cambia o agrega una tool en `mcp_server.py` que consuma alguna API de
[public-apis/public-apis](https://github.com/public-apis/public-apis) y
combínala con `buscar_cp` para enriquecer la respuesta del agente.

## Documentación a fondo

Para una explicación detallada de cómo y por qué está construido cada
módulo, ver [`docs/`](./docs/README.md).

# Generación de presentaciones

Para generar las presentaciones actuales en formato PDF y ODP a partir de los archivos Markdown, utiliza el script `generate.sh`.

## Slidev, de forma incremental

Slidev está disponible como una ruta experimental y opt-in. Marp sigue siendo
el backend predeterminado para las presentaciones existentes, la exportación
ODP y los ZIP de release; no es necesario migrar ningún deck para instalarlo.

El piloto está en `red-soberana-de-ia/slidev/slides.md` y reutiliza los assets
de la presentación Marp mediante `vite.config.ts`.

La decisión y los límites de la evaluación están documentados en
[`SLIDEV.md`](SLIDEV.md).

Desde la raíz del repositorio:

```bash
npm install --prefix presentaciones
just slidev-dev presentaciones/red-soberana-de-ia/slidev/slides.md
just slidev-export presentaciones/red-soberana-de-ia/slidev/slides.md pdf
just slidev-zip presentaciones/red-soberana-de-ia/slidev/slides.md
```

Los formatos disponibles para la exportación opt-in son `pdf`, `pptx`, `png`
y `md`. El PPTX de Slidev contiene una imagen por diapositiva; para ODP se
conserva Marp. Para InsightBloom usa `just zip <nombre> --engine slidev` o
`just slidev-zip`: genera un ZIP Slidev transportable con la fuente, un
manifiesto, sus assets y `dist/index.html` producido por `slidev build`.

Sin `--engine`, `just zip` mantiene el comportamiento Marp.

## Portal local

Para mostrar las presentaciones Marp y Slidev en un catálogo navegable:

```bash
just portal-dev
```

Abre <http://localhost:4173>. `just portal-dev` genera automáticamente el HTML
Marp y los builds estáticos Slidev dentro de `portal/generated/`, que no se
versiona. `just portal-build` queda disponible para generar el catálogo sin
levantar el servidor.

Las directivas Marp como `<!-- _class: ... -->` y `![bg ...]` requieren una
adaptación manual a layouts/CSS de Slidev. Por eso las fuentes actuales no se
convierten automáticamente.

## Uso básico

Abre una terminal en esta carpeta y ejecuta:

```bash
./generate.sh
```

Esto generará archivos PDF y ODP para todas las presentaciones encontradas.

## Opciones de formato

Puedes especificar el formato que deseas generar pasando uno de los siguientes argumentos:

- `pdf` : Genera solo archivos PDF.
- `odp` : Genera solo archivos ODP.
- `all` : Genera ambos formatos (equivalente a no pasar argumentos).

Ejemplo:

```bash
./generate.sh pdf
```

## Requisitos

- Tener instalado [Marp CLI](https://marp.app/).
- Los archivos Markdown deben estar en subcarpetas y cada carpeta debe tener su tema en `assets/css/theme.css`.

## Notas

- Si no hay archivos `.md` en una carpeta, esa carpeta será ignorada.
- Si se pasa un formato desconocido, se generarán ambos formatos por defecto.

# Paquete ZIP de Slidev para InsightBloom

## Propósito

Esta guía define el formato de entrada que acepta actualmente el motor Slidev
de InsightBloom. Está escrita para dos públicos:

- la persona que prepara una presentación;
- un agente de IA que genera el ZIP antes de subirlo al panel de moderación.

Hay dos formatos deliberados y deben generarse con comandos distintos:

| Comando | Contenido | Trabajo del servidor | Uso |
|---|---|---|---|
| `just slidev-insightbloom-zip` | `slides.md` y assets declarativos, sin JavaScript | Compila Slidev | formato recomendado y actual |
| `just slidev-insightbloom-fat-zip` | `dist/` compilado, manifiesto y hashes | Sirve el artefacto; no recompila | formato experimental, sujeto a auditoría y aislamiento |

El primer ZIP se mantiene como contrato actual: InsightBloom recibe la fuente
declarativa y ejecuta su propia versión fijada de Slidev dentro de
`insightbloom-presentations`.

El segundo ZIP reduce CPU, memoria y tiempo de build en InsightBloom, pero
traslada el riesgo al JavaScript que se sube. Por eso no debe tratarse como una
variante equivalente: sólo puede habilitarse después de pasar el auditor de
artefactos, validación de hashes, procedencia y el runtime aislado descrito en
[`SLIDEV-ARTIFACT-AUDIT.md`](./SLIDEV-ARTIFACT-AUDIT.md).

## Contrato vigente del MVP: `slidev-insightbloom-zip`

Al cargar el archivo se debe seleccionar `Slidev` como engine. El multipart
envía `presentationProvider=SLIDEV` junto con el ZIP.

El paquete debe contener:

- un archivo `slides.md`;
- Markdown adicional, sólo si es necesario y sin crear ambigüedad sobre la entrada principal;
- CSS local;
- imágenes locales;
- fuentes locales;
- audio o video local, cuando la presentación realmente los necesite.

La estructura recomendada es:

```text
mi-presentacion-slidev.zip
└── slides.md
└── assets/
    ├── css/
    │   └── theme.css
    ├── images/
    │   ├── portada.png
    │   └── diagrama.svg
    └── fonts/
        └── Inter-Regular.woff2
```

Los paths usados desde `slides.md` deben apuntar a esos archivos. Por ejemplo:

```md
![Portada](assets/images/portada.png)
```

También se acepta una carpeta raíz común, pero conviene que `slides.md` quede en la raíz del ZIP. El backend busca Markdown recursivamente y, para Slidev, prefiere un archivo cuyo nombre sea exactamente `slides.md`.

## Archivos que no deben estar en el ZIP fuente

No incluir ninguno de estos elementos:

```text
dist/
node_modules/
package.json
package-lock.json
npm-shrinkwrap.json
vite.config.js
vite.config.ts
vite.config.mjs
vite.config.cjs
webpack.config.js
*.js
*.mjs
*.cjs
*.ts
*.tsx
*.jsx
*.vue
*.sh
```

Esto incluye tanto archivos de fuente como archivos generados. En particular,
no se debe comprimir la carpeta `dist/` producida por `slidev build`: contiene
los bundles JavaScript de la aplicación y el validador del MVP los rechaza.

Tampoco se permiten:

- enlaces simbólicos;
- paths absolutos;
- entradas con `../`;
- plugins o imports remotos;
- instalaciones de dependencias del usuario;
- componentes Vue personalizados;
- configuraciones Vite/Slidev aportadas por el usuario.

La restricción es intencional. El servicio compila la presentación dentro de su propia imagen, con versiones controladas, y no ejecuta código arbitrario del ZIP ni instala paquetes durante una carga.

## Límites técnicos

- máximo comprimido: 100 MiB;
- máximo descomprimido: 250 MiB;
- máximo de entradas: 1000.

Los límites protegen el proceso de extracción y el build. Mantener el paquete
pequeño también reduce el tiempo de procesamiento y el consumo temporal del
pod.

## Cómo generar `slidev-insightbloom-zip`

Preparar un directorio temporal que sólo contenga los archivos permitidos:

```bash
set -euo pipefail

SOURCE_DIR="/ruta/a/mi-presentacion-slidev"
PACKAGE_DIR="$(mktemp -d /tmp/mi-presentacion-slidev-package.XXXXXX)"
OUTPUT_ZIP="/tmp/mi-presentacion-slidev.zip"

mkdir -p "$PACKAGE_DIR/assets/css" "$PACKAGE_DIR/assets/images" "$PACKAGE_DIR/assets/fonts"

cp "$SOURCE_DIR/slides.md" "$PACKAGE_DIR/slides.md"
cp -R "$SOURCE_DIR/assets/." "$PACKAGE_DIR/assets/"

find "$PACKAGE_DIR" -type f -print

(cd "$PACKAGE_DIR" && zip -r "$OUTPUT_ZIP" slides.md assets -x '*.DS_Store')
unzip -t "$OUTPUT_ZIP"
unzip -Z1 "$OUTPUT_ZIP"
```

Si no existen fuentes, audio o video, no se deben crear carpetas vacías sólo
por cumplir una plantilla. La estructura mínima puede ser:

```text
slides.md
assets/images/...
```

Para una comprobación rápida, la lista final no debe mostrar `dist/`,
`node_modules/`, `.js`, `.ts`, `.vue`, `package.json` ni configuraciones de
build.

## Checklist del agente de IA que prepara el ZIP fuente

El agente debe aplicar esta secuencia antes de entregar el ZIP:

1. Generar `slides.md` con frontmatter Slidev válido.
2. Reemplazar componentes Vue personalizados por Markdown, HTML/CSS
   declarativo o funcionalidades integradas de Slidev.
3. Copiar únicamente imágenes, fuentes, estilos y multimedia necesarios a
   `assets/`.
4. Reescribir las referencias de `slides.md` para que sean relativas al ZIP.
5. Eliminar `dist`, `node_modules`, manifests npm, configuraciones Vite,
   componentes y scripts.
6. Crear el ZIP desde el directorio de staging, no desde el repositorio
   completo ni desde la carpeta de salida de un build.
7. Ejecutar la validación local siguiente antes de entregar el archivo:

```bash
unzip -Z1 mi-presentacion-slidev.zip \
  | grep -E '(^|/)(dist|node_modules)(/|$)|(^|/)(package(-lock)?|npm-shrinkwrap|vite\.config|webpack\.config).*|\.(js|mjs|cjs|ts|tsx|jsx|vue|sh)$' \
  && { echo 'ZIP INVALIDO'; exit 1; } \
  || echo 'ZIP compatible con el allowlist del MVP'

unzip -Z1 mi-presentacion-slidev.zip | grep '(^|/)slides\.md$'
unzip -t mi-presentacion-slidev.zip
```

8. Entregar el ZIP y reportar su estructura, tamaño comprimido y resultado de
   las tres comprobaciones.

## Instrucción lista para copiar al agente de IA (ZIP fuente)

```text
Genera un paquete ZIP compatible con el MVP de Slidev de InsightBloom.

El ZIP debe contener una entrada principal llamada slides.md y, como máximo,
Markdown adicional, CSS, imágenes, fuentes, audio y video locales. Coloca los
assets bajo assets/ y usa rutas relativas desde slides.md.

No incluyas dist/, node_modules/, package.json, package-lock.json,
npm-shrinkwrap.json, vite.config.*, webpack.config.*, archivos .js, .mjs,
.cjs, .ts, .tsx, .jsx, .vue o .sh. No uses componentes Vue personalizados,
plugins, dependencias npm, imports remotos, symlinks ni rutas ../.

No comprimas el resultado de slidev build. InsightBloom compila slides.md con
su propio @slidev/cli fijado y genera la vista pública, el modo presentador,
los previews y las exportaciones.

Antes de entregar el archivo:
1. verifica que exista slides.md;
2. verifica que no existan dist, node_modules ni extensiones prohibidas;
3. ejecuta unzip -t sobre el ZIP;
4. reporta la estructura final y el tamaño comprimido.
```

## Contrato experimental: `slidev-insightbloom-fat-zip`

El paquete FAT no contiene `slides.md`, `source/`, componentes Vue ni archivos
de proyecto. Es una distribución estática producida por el builder del agente:

```text
slidev-artifact.json
dist/
  index.html
  assets/
    *.js
    *.css
    fuentes e imágenes locales
exports/
  presentation.pdf       # opcional
previews/
  slide-1.png             # opcional
```

El manifiesto mínimo debe declarar el engine, su versión, el formato estático,
la base relativa, el identificador de build y el SHA-256 de cada archivo
publicable:

```json
{
  "engine": "slidev",
  "engineVersion": "52.18.0",
  "artifactFormat": "static",
  "base": "relative",
  "buildId": "ci-12345",
  "files": {
    "dist/index.html": "sha256:...",
    "dist/assets/index-abc.js": "sha256:..."
  }
}
```

El comando `just slidev-insightbloom-fat-zip` debe construir en un directorio
temporal, copiar sólo `dist/`, `exports/`, `previews/` y el manifiesto, ejecutar
el auditor de InsightBloom y fallar si el resultado es `REJECT`. No debe
empaquetar `node_modules`, `package.json`, `source`, `*.map`, configuraciones de
Vite ni el repositorio completo.

El FAT es más pesado para transportar y almacenar, pero evita que el servidor
compile el proyecto. También conserva el JavaScript generado, por lo que el
servidor debe servirlo desde un origen separado, con CSP e iframe sandbox; el
auditor por sí solo no es una garantía de seguridad.

### Checklist del agente de IA que prepara el ZIP compilado (FAT)

El agente debe ejecutar esta secuencia:

1. Construir el proyecto con `slidev build`.
2. Recolectar archivos compilados desde `dist/`, `exports/` y `previews/`.
3. Generar un manifiesto `slidev-artifact.json` con:
   - `engine: "slidev"`
   - `engineVersion`: versión de @slidev/cli usado
   - `artifactFormat: "static"`
   - `base: "relative"` (rutas sin `/` inicial)
   - `buildId`: identificador único de la construcción (ej: `ci-12345`, timestamp, etc.)
   - `files`: objeto con rutas relativas como claves y `sha256:HASH` como valores
4. Eliminar completamente `node_modules`, `package.json`, `source`, `*.map` y
   configuraciones de Vite/Webpack.
5. Crear el ZIP desde un directorio de staging limpio que contenga solo:
   - `slidev-artifact.json`
   - `dist/` (con `index.html` y `assets/`)
   - `exports/` (opcional, si existen PDFs/PPTXs)
   - `previews/` (opcional, si existen imágenes de preview)
6. Ejecutar la validación local:

```bash
unzip -Z1 slidev-compilado.zip \
  | grep -E 'node_modules|package\.json|\.map$|source/' \
  && { echo 'ZIP INVALIDO: contiene archivos prohibidos'; exit 1; } \
  || echo 'ZIP compatible: solo contiene artefacto compilado'

unzip -Z1 slidev-compilado.zip | grep 'slidev-artifact\.json$'
unzip -t slidev-compilado.zip
```

7. Reportar:
   - Estructura final
   - Tamaño comprimido
   - Versión de Slidev
   - BuildId
   - Resultado de las tres comprobaciones

## Instrucción lista para copiar al agente de IA (ZIP compilado)

```text
Genera un paquete ZIP compilado (FAT) de Slidev para InsightBloom.

Construye el proyecto completo con slidev build. Luego, crea un directorio de
staging que contenga SOLO:
- slidev-artifact.json (manifiesto con metadatos y SHA-256 de archivos)
- dist/ (compilado por Slidev, sin node_modules)
- exports/ (opcional: PDFs, PPTXs)
- previews/ (opcional: imágenes de slide)

El manifiesto debe incluir:
- engine: "slidev"
- engineVersion: (versión de @slidev/cli usado)
- artifactFormat: "static"
- base: "relative"
- buildId: (identificador único: CI_PIPELINE_ID, timestamp, etc.)
- files: objeto con rutas relativas y sus SHA-256

NO incluyas:
- node_modules, package.json, package-lock.json
- source/, slides.md, componentes Vue
- *.map, vite.config.*, webpack.config.*
- el repositorio completo

Validación antes de entregar:
1. unzip -Z1 | grep -E 'node_modules|package\.json|\.map|source/' → debe estar vacío
2. unzip -Z1 | grep slidev-artifact.json → debe encontrarse
3. unzip -t → debe ser íntegro

Reporta la estructura, tamaño, versión de Slidev y buildId.
```

## Caso concreto: `slidev-en-10-minutos-slidev.zip`

El archivo analizado contiene correctamente `source/slides.md`, pero también
incluye el build completo en `dist/` y archivos de proyecto como:

```text
source/components/Counter.vue
source/package.json
source/slidev.config.ts
source/vite.config.ts
dist/assets/*.js
```

Por eso el endpoint responde `400 archive_file_type_not_allowed` antes de
ejecutar Slidev. Además, `slides.md` usa `<Counter />`; aun si se elimina
`dist/`, ese componente no es compatible con el MVP porque los componentes
Vue están fuera del allowlist.

Para hacer compatible esa presentación con el MVP se debe:

1. quitar o reemplazar `<Counter />` por contenido declarativo;
2. eliminar `source/components/Counter.vue`;
3. eliminar `package.json`, `slidev.config.ts` y `vite.config.ts`;
4. eliminar completamente `dist/`;
5. conservar sólo `slides.md` y los assets locales realmente usados;
6. regenerar el ZIP con la estructura recomendada.

Si se necesita conservar componentes Vue, plugins o configuraciones propias,
eso requiere otra iniciativa: un sandbox de build aislado para proyectos
Slidev completos. No se debe relajar este allowlist directamente en el
servicio HTTP.

## Flujo de carga y procesamiento

```text
Agente IA
   │
   ├── just slidev-insightbloom-zip
   │      └── slides.md + assets permitidos
   │
   └── just slidev-insightbloom-fat-zip
          └── dist/ + slidev-artifact.json + hashes
          │
          ▼
Panel de moderación: engine = Slidev
          │ presentationProvider=SLIDEV
          ▼
InsightBloom selecciona el flujo por formato
          │
          ├── ZIP fuente: valida, extrae y ejecuta @slidev/cli fijado
          └── FAT ZIP: audita, verifica y publica sólo si está habilitado
```

El servicio no consume el `index.html` ni los bundles de un `dist/` generado
localmente. Esto garantiza que la presentación pública, el modo presentador,
los previews y las exportaciones usen el engine y las rutas controladas por
InsightBloom.

## Diferencia: ZIP Fuente vs ZIP FAT

| Aspecto | ZIP Fuente (`slidev-insightbloom-zip`) | ZIP FAT (`slidev-insightbloom-fat-zip`) |
|---|---|---|
| **Contenido** | `slides.md` + assets permitidos (CSS, imágenes, fuentes, audio, video) | `dist/` compilado + `slidev-artifact.json` + manifiesto con SHA-256 |
| **Tamaño comprimido** | ~1-10 KB | ~100 KB - 10 MB |
| **Tamaño descomprimido** | ~5-50 KB | ~500 KB - 50 MB |
| **Componentes Vue** | ❌ No permitidos | ❌ No permitidos (ya compilados) |
| **Node_modules** | ❌ No permitido | ❌ No permitido |
| **Package.json** | ❌ No permitido | ❌ No permitido |
| **Compilación en servidor** | ✅ Sí (CPU, memoria, tiempo) | ❌ No (JavaScript precompilado) |
| **Para InsightBloom** | ✅ **Recomendado** (actual) | ⚠️ Experimental (requiere auditoría) |
| **Para archivo local** | ❌ No ejecutable | ⚠️ Solo si se sirve desde HTTP |
| **Riesgo de seguridad** | ✅ Mínimo (solo fuente) | ⚠️ Mayor (JavaScript generado sube sin compilación) |

## Comandos de generación

### ZIP Fuente (MVP actual)

```bash
# Opción 1: Nombre simple (resuelve automáticamente)
just slidev-insightbloom-zip slidev-en-10-minutos

# Opción 2: Con tipo (si existe en ambos directorios)
just slidev-insightbloom-zip slidev-en-10-minutos -t presentation

# Opción 3: Con salida personalizada
just slidev-insightbloom-zip slidev-en-10-minutos dist/custom.zip

# Opción 4: Ruta completa
just slidev-insightbloom-zip presentaciones/slidev-en-10-minutos/slidev
```

### ZIP FAT (Experimental)

```bash
# Opción 1: Nombre simple (compila automáticamente)
just slidev-insightbloom-fat-zip slidev-en-10-minutos

# Opción 2: Con tipo
just slidev-insightbloom-fat-zip slidev-en-10-minutos -t presentation

# Opción 3: Con salida personalizada
just slidev-insightbloom-fat-zip slidev-en-10-minutos dist/fat-custom.zip

# Opción 4: Ruta completa
just slidev-insightbloom-fat-zip presentaciones/slidev-en-10-minutos/slidev
```

## Validación automática

### Para ZIP fuente

```bash
#!/bin/bash
ZIP_FILE="dist/slidev-en-10-minutos-insightbloom.zip"

echo "Verificando ZIP fuente..."
unzip -Z1 "$ZIP_FILE" \
  | grep -E '(^|/)(dist|node_modules)(/|$)|(^|/)(package(-lock)?|npm-shrinkwrap|vite\.config|webpack\.config).*|\.(js|mjs|cjs|ts|tsx|jsx|vue|sh)$' \
  && { echo '❌ ZIP INVALIDO'; exit 1; } \
  || echo '✓ Sin archivos prohibidos'

unzip -Z1 "$ZIP_FILE" | grep -q '^slides\.md$' && echo '✓ Contiene slides.md' || { echo '❌ Falta slides.md'; exit 1; }
unzip -t "$ZIP_FILE" > /dev/null 2>&1 && echo '✓ ZIP íntegro' || { echo '❌ ZIP corrupto'; exit 1; }

echo "✅ ZIP fuente VÁLIDO"
```

### Para ZIP FAT

```bash
#!/bin/bash
ZIP_FILE="dist/slidev-en-10-minutos-insightbloom-fat.zip"

echo "Verificando ZIP FAT..."
unzip -Z1 "$ZIP_FILE" \
  | grep -E 'node_modules|package\.json|\.map$|source/' \
  && { echo '❌ ZIP INVALIDO: contiene archivos prohibidos'; exit 1; } \
  || echo '✓ Sin archivos prohibidos'

unzip -Z1 "$ZIP_FILE" | grep -q '^slidev-artifact\.json$' && echo '✓ Contiene slidev-artifact.json' || { echo '❌ Falta manifiesto'; exit 1; }
unzip -Z1 "$ZIP_FILE" | grep -q '^dist/' && echo '✓ Contiene dist/' || { echo '❌ Falta dist/'; exit 1; }
unzip -t "$ZIP_FILE" > /dev/null 2>&1 && echo '✓ ZIP íntegro' || { echo '❌ ZIP corrupto'; exit 1; }

# Validar JSON del manifiesto
unzip -p "$ZIP_FILE" slidev-artifact.json | jq . > /dev/null 2>&1 && echo '✓ Manifiesto JSON válido' || { echo '❌ JSON inválido'; exit 1; }

echo "✅ ZIP FAT VÁLIDO"
```

## Diferencia: ZIP Completo vs MVP

| Aspecto | ZIP Completo (`slidev-zip`) | ZIP MVP (`slidev-insightbloom-zip`) |
|---|---|---|
| **Contiene** | `source/` + `dist/` + build completo | Solo `slides.md` + assets permitidos |
| **Tamaño** | ~1-50 MB | ~1-10 KB |
| **Componentes Vue** | ✅ Permitidos | ❌ No permitidos |
| **Node_modules** | ✅ Incluido | ❌ No permitido |
| **Para InsightBloom** | No recomendado (innecesario) | ✅ **Recomendado** |
| **Para archivo local** | ✅ Ejecutable con `npm install` | ❌ No ejecutable (solo fuente) |
| **Compila en** | Máquina local | Servidor InsightBloom |

**Usa ZIP MVP cuando:**
- Subes a InsightBloom
- Quieres minimizar tamaño
- No necesitas componentes Vue

**Usa ZIP Completo cuando:**
- Distribuyes localmente
- Necesitas que sea portable y ejecutable
- Planeas reutilizar fuente con modificaciones

## Flujo de carga y procesamiento

```text
Agente IA / Presentador
   │
   ├── genera slides.md + assets permitidos
   ├── valida con just slidev-insightbloom-zip
   └── crea ZIP compatible con MVP
          │
          ▼
Panel de moderación
          │ presentationProvider=SLIDEV
          ▼
InsightBloom MVP valida y extrae
          │
          ├── encuentra slides.md
          ├── ejecuta @slidev/cli fijado
          ├── genera SPA para audiencia
          ├── genera presenter mode
          └── publica artefactos por conferencia
```

El servicio **no consume** el `index.html` ni los bundles de un `dist/` generado localmente. Esto garantiza que la presentación pública, el modo presentador, los previews y las exportaciones usen el engine y las rutas controladas por InsightBloom.

## Problemas comunes

### "400 archive_file_type_not_allowed"

**Causa:** El ZIP contiene `dist/`, `node_modules/`, `.js`, `.ts`, `.vue` o `package.json`.

**Solución:**
```bash
unzip -l tu-presentacion.zip | grep -E '(dist/|node_modules/|package\.json|\.js$|\.ts$|\.vue$)'
```

Si aparece algo, elimínalo del ZIP. Usa `just slidev-insightbloom-zip` para generar correctamente.

### "Component not found: <Counter />"

**Causa:** El `slides.md` usa componentes Vue personalizados, que no son compatibles con MVP.

**Solución:**
```bash
# En slides.md, reemplaza:
<Counter />

# Por HTML/CSS declarativo:
<div style="padding: 20px; background: blue; color: white; border-radius: 8px;">
  ✨ Contador estático
</div>
```

O elimina la línea si no es crítica.

### "Tamaño del ZIP excede 100 MiB"

**Causa:** Incluiste archivos grandes innecesarios.

**Solución:**
- Optimiza imágenes con `ImageOptim`, `TinyPNG`, etc.
- Comprime videos con `ffmpeg`
- Remueve assets no usados
- Valida con: `unzip -l tu-presentacion.zip`

## Recursos

- Guía [Flujo general](./01-flujo-general.md)
- Guía [Slidev](./03-slidev.md)
- Guía [Exportación](./04-exportacion.md)
- Script de construcción: [build-slidev-insightbloom-zip.sh](../scripts/build-slidev-insightbloom-zip.sh)

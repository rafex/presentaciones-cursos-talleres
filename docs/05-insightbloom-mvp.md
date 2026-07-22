# Paquete ZIP de Slidev para InsightBloom MVP

## Propósito

Esta guía define el formato de entrada que acepta actualmente el motor Slidev de InsightBloom. Está escrita para dos públicos:

- la persona que prepara una presentación;
- un agente de IA que genera el ZIP antes de subirlo al panel de moderación.

El ZIP que se sube a InsightBloom **no es el resultado compilado** de `slidev build`. InsightBloom recibe la fuente declarativa y ejecuta su propia versión fijada de Slidev dentro de `insightbloom-presentations`.

## Contrato vigente del MVP

Al cargar el archivo se debe seleccionar `Slidev` como engine. El multipart envía `presentationProvider=SLIDEV` junto con el ZIP.

El paquete debe contener:

- un archivo `slides.md`;
- Markdown adicional, sólo si es necesario y sin crear ambigüedad sobre la entrada principal;
- CSS local;
- imágenes locales;
- fuentes locales;
- audio o video local, cuando la presentación realmente los necesite.

### Estructura recomendada

```text
mi-presentacion-insightbloom.zip
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

## Archivos que NO deben estar en el ZIP

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

Esto incluye tanto archivos de fuente como archivos generados. En particular, **no se debe comprimir la carpeta `dist/`** producida por `slidev build`: contiene los bundles JavaScript de la aplicación y el validador del MVP los rechaza.

### Restricciones adicionales

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

| Límite | Valor |
|---|---|
| Tamaño comprimido | 100 MiB |
| Tamaño descomprimido | 250 MiB |
| Máximo de entradas | 1000 |

Los límites protegen el proceso de extracción y el build. Mantener el paquete pequeño también reduce el tiempo de procesamiento y el consumo temporal del pod.

## Generar el ZIP correctamente

### Opción 1: Usar el script (recomendado)

```bash
# Resolución automática de presentación o taller
just slidev-insightbloom-zip slidev-en-10-minutos

# Con tipo explícito (si existe en ambos directorios)
just slidev-insightbloom-zip slidev-en-10-minutos -t presentation

# Con salida personalizada
just slidev-insightbloom-zip slidev-en-10-minutos dist/custom.zip
```

Genera: `dist/slidev-en-10-minutos-insightbloom.zip`

El script:
1. Resuelve el nombre usando `resolve-target.sh`
2. Copia solo `slides.md`
3. Copia assets permitidos (CSS, imágenes, fuentes, audio, video)
4. Valida que no hay archivos prohibidos
5. Comprueba integridad del ZIP

### Opción 2: Script manual (ruta completa)

```bash
./scripts/build-slidev-insightbloom-zip.sh presentaciones/mi-presentacion/slidev
./scripts/build-slidev-insightbloom-zip.sh presentaciones/mi-presentacion/slidev dist/mi-presentacion.zip
```

### Opción 3: Manualmente

Preparar un directorio temporal que sólo contenga los archivos permitidos:

```bash
set -euo pipefail

SOURCE_DIR="/ruta/a/mi-presentacion-slidev"
PACKAGE_DIR="$(mktemp -d /tmp/mi-presentacion-slidev-package.XXXXXX)"
OUTPUT_ZIP="/tmp/mi-presentacion-slidev.zip"

mkdir -p "$PACKAGE_DIR/assets/css" "$PACKAGE_DIR/assets/images" "$PACKAGE_DIR/assets/fonts"

cp "$SOURCE_DIR/slides.md" "$PACKAGE_DIR/slides.md"
cp -R "$SOURCE_DIR/assets/." "$PACKAGE_DIR/assets/" 2>/dev/null || true

find "$PACKAGE_DIR" -type f -print

(cd "$PACKAGE_DIR" && zip -r "$OUTPUT_ZIP" slides.md assets -x '*.DS_Store')
unzip -t "$OUTPUT_ZIP"
unzip -Z1 "$OUTPUT_ZIP"
```

Si no existen fuentes, audio o video, no se deben crear carpetas vacías sólo por cumplir una plantilla. La estructura mínima puede ser:

```text
slides.md
assets/images/...
```

## Validación antes de subir

Ejecuta estas comprobaciones antes de enviar a InsightBloom:

### 1. Verificar que existe `slides.md`

```bash
unzip -l mi-presentacion-slidev.zip | grep slides.md
```

Debe aparecer `slides.md` en el listado.

### 2. Verificar integridad

```bash
unzip -t mi-presentacion-slidev.zip
```

Debe terminar con "No errors detected" u "OK".

### 3. Verificar ausencia de archivos prohibidos

```bash
unzip -Z1 mi-presentacion-slidev.zip \
  | grep -E '(^|/)(dist|node_modules)(/|$)|(^|/)(package(-lock)?|npm-shrinkwrap|vite\.config|webpack\.config).*|\.(js|mjs|cjs|ts|tsx|jsx|vue|sh)$' \
  && { echo 'ZIP INVÁLIDO'; exit 1; } \
  || echo 'ZIP compatible con el allowlist del MVP'
```

## Checklist del agente de IA

El agente debe aplicar esta secuencia antes de entregar el ZIP:

1. ✅ Generar `slides.md` con frontmatter Slidev válido.
2. ✅ Reemplazar componentes Vue personalizados por Markdown, HTML/CSS declarativo o funcionalidades integradas de Slidev.
3. ✅ Copiar únicamente imágenes, fuentes, estilos y multimedia necesarios a `assets/`.
4. ✅ Reescribir las referencias de `slides.md` para que sean relativas al ZIP.
5. ✅ Eliminar `dist`, `node_modules`, manifests npm, configuraciones Vite, componentes y scripts.
6. ✅ Crear el ZIP desde el directorio de staging, no desde el repositorio completo ni desde la carpeta de salida de un build.
7. ✅ Ejecutar la validación local:
   ```bash
   unzip -Z1 mi-presentacion-slidev.zip \
     | grep -E '(^|/)(dist|node_modules)(/|$)|(^|/)(package(-lock)?|npm-shrinkwrap|vite\.config|webpack\.config).*|\.(js|mjs|cjs|ts|tsx|jsx|vue|sh)$' \
     && { echo 'ZIP INVALIDO'; exit 1; } \
     || echo 'ZIP compatible con el allowlist del MVP'

   unzip -Z1 mi-presentacion-slidev.zip | grep '(^|/)slides\.md$'
   unzip -t mi-presentacion-slidev.zip
   ```
8. ✅ Entregar el ZIP y reportar su estructura, tamaño comprimido y resultado de las comprobaciones.

## Instrucción lista para copiar al agente de IA

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

## Validación automatizada de ejemplo

Script para validar un ZIP de ejemplo (`slidev-en-10-minutos`):

```bash
#!/bin/bash

ZIP_FILE="dist/slidev-en-10-minutos-insightbloom.zip"

echo "=========================================="
echo "VALIDACIÓN: ZIP MVP (slidev-insightbloom-zip)"
echo "=========================================="
echo

# ✓ Integridad
if unzip -t "$ZIP_FILE" 2>&1 | grep -q "OK\|No errors"; then
  echo "✓ ZIP íntegro"
else
  echo "❌ ZIP corrupto"
  exit 1
fi

# ✓ Contiene slides.md
if unzip -l "$ZIP_FILE" | grep -q "slides.md"; then
  echo "✓ slides.md presente"
else
  echo "❌ FALTA slides.md"
  exit 1
fi

# ✓ Sin archivos prohibidos
if unzip -l "$ZIP_FILE" | awk 'NR > 3 { print $4 }' | grep -E '\.(js|ts|vue|sh)$|dist/|node_modules/|package\.json' > /dev/null; then
  echo "❌ Contiene archivos prohibidos"
  exit 1
fi
echo "✓ Sin archivos prohibidos"

# ✓ Sin componentes Vue
if unzip -p "$ZIP_FILE" slides.md | grep -q "<Counter\|import.*from\|<script"; then
  echo "❌ Contiene componentes o imports"
  exit 1
fi
echo "✓ Sin componentes Vue personalizados"

echo
echo "Tamaño: $(du -h "$ZIP_FILE" | cut -f1)"
echo "Archivos: $(unzip -l "$ZIP_FILE" | tail -1 | awk '{print $(NF-1)}')"
echo
echo "✅ ZIP VÁLIDO para InsightBloom MVP"
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

# ZIP para InsightBloom: MVP Slidev

Esta guía describe el formato de ZIP que acepta el motor Slidev del MVP de InsightBloom.

## Resumen

InsightBloom **recibe la fuente declarativa** de Slidev, no el resultado compilado de `slidev build`. El servicio ejecuta su propia versión controlada de Slidev dentro de `insightbloom-presentations`.

El ZIP debe contener:
- Un archivo principal: **`slides.md`**
- Assets locales: CSS, imágenes, fuentes, audio, video
- **Nada más**

## Estructura recomendada

```
mi-presentacion-insightbloom.zip
├── slides.md
└── assets/
    ├── css/
    │   └── theme.css
    ├── images/
    │   ├── portada.png
    │   └── diagrama.svg
    └── fonts/
        └── Inter-Regular.woff2
```

Si no existen fuentes, audio o video, no crees carpetas vacías. La estructura mínima puede ser:

```
mi-presentacion-insightbloom.zip
├── slides.md
└── assets/images/
    ├── imagen1.png
    └── imagen2.svg
```

## Paths desde `slides.md`

Usa rutas relativas que apunten a los archivos en `assets/`:

```markdown
![Portada](assets/images/portada.png)

<style scoped>
@import url('assets/css/theme.css');
</style>
```

## Archivos prohibidos

**NO incluir bajo ninguna circunstancia:**

```
dist/                    # Resultado de slidev build
node_modules/            # Dependencias npm
package.json             # Manifiesto npm
package-lock.json
npm-shrinkwrap.json
vite.config.*            # .js, .ts, .mjs, .cjs
slidev.config.*
webpack.config.*
*.vue                    # Componentes Vue personalizados
*.ts                     # TypeScript (excepto en slides.md)
*.tsx
*.jsx
*.js                     # JavaScript (excepto en slides.md)
*.mjs
*.cjs
*.sh                     # Scripts
symlinks                 # Enlaces simbólicos
```

También está prohibido:
- Componentes Vue personalizados (`<Counter />`, `<MyComponent />`, etc.)
- Plugins Slidev
- Imports remotos o CDN
- Configuraciones de Vite o Slidev
- Rutas absolutas
- Rutas con `../`

## Límites técnicos

| Límite | Valor |
|---|---|
| Tamaño comprimido | 100 MiB |
| Tamaño descomprimido | 250 MiB |
| Máximo de entradas | 1000 |

## Generar el ZIP correctamente

### Opción 1: Usar el script con nombre de proyecto (recomendado)

El script resuelve automáticamente si el proyecto está en `presentaciones/` o `talleres/`:

```bash
# Resolución automática
just slidev-insightbloom-zip slidev-en-10-minutos

# Con tipo explícito (si existe ambigüedad)
just slidev-insightbloom-zip slidev-en-10-minutos -t presentation

# Con salida personalizada
just slidev-insightbloom-zip slidev-en-10-minutos dist/custom.zip

# Tipo + salida
just slidev-insightbloom-zip slidev-en-10-minutos -t taller dist/custom.zip
```

Genera: `dist/slidev-en-10-minutos-insightbloom.zip` (o la ruta especificada)

### Opción 2: Usar el script con ruta completa

Para rutas absolutas o complejas:

```bash
./scripts/build-slidev-insightbloom-zip.sh presentaciones/mi-presentacion/slidev
./scripts/build-slidev-insightbloom-zip.sh presentaciones/mi-presentacion/slidev dist/mi-presentacion.zip
```

### Opción 3: Manualmente (sin script)

Si prefieres no usar el script:

```bash
#!/bin/bash
SOURCE_DIR="presentaciones/mi-presentacion/slidev"
PACKAGE_DIR="/tmp/mi-presentacion-package"
OUTPUT_ZIP="dist/mi-presentacion-insightbloom.zip"

# Crear staging
mkdir -p "$PACKAGE_DIR/assets/css" "$PACKAGE_DIR/assets/images"

# Copiar solo lo permitido
cp "$SOURCE_DIR/slides.md" "$PACKAGE_DIR/slides.md"
cp -R "$SOURCE_DIR/assets/css" "$PACKAGE_DIR/assets/" 2>/dev/null || true
cp -R "$SOURCE_DIR/assets/images" "$PACKAGE_DIR/assets/" 2>/dev/null || true

# Crear ZIP desde staging
cd "$PACKAGE_DIR"
zip -r "$OUTPUT_ZIP" slides.md assets/

# Validar
unzip -t "$OUTPUT_ZIP"
unzip -l "$OUTPUT_ZIP"
```

## Validación antes de subir

Ejecuta estas comprobaciones antes de enviar a InsightBloom:

### 1. Verificar que existe `slides.md`

```bash
unzip -l mi-presentacion-insightbloom.zip | grep "slides.md"
```

Debe aparecer `slides.md` en la raíz.

### 2. Verificar integridad del ZIP

```bash
unzip -t mi-presentacion-insightbloom.zip
```

Debe terminar con "OK" o "No errors detected".

### 3. Verificar que NO hay archivos prohibidos

```bash
unzip -l mi-presentacion-insightbloom.zip | grep -E "(dist/|node_modules/|package\.json|\.vue$|\.ts$|\.js$|vite\.config|slidev\.config)"
```

Si aparece algo, está mal. Si no aparece nada, está bien.

### 4. Listar contenido final

```bash
unzip -l mi-presentacion-insightbloom.zip
```

Reporta la estructura y verifica que solo contiene `slides.md` y `assets/`.

## Script de validación automatizado

```bash
#!/bin/bash

ZIP_FILE="$1"

echo "✓ Validando $ZIP_FILE para InsightBloom..."

# 1. slides.md
if ! unzip -l "$ZIP_FILE" | grep -q "^.*slides\.md$"; then
  echo "❌ ERROR: slides.md no encontrado"
  exit 1
fi
echo "✓ slides.md presente"

# 2. Integridad
if ! unzip -t "$ZIP_FILE" >/dev/null 2>&1; then
  echo "❌ ERROR: ZIP corrupto"
  exit 1
fi
echo "✓ ZIP íntegro"

# 3. Sin prohibidos
if unzip -l "$ZIP_FILE" | grep -E "(dist/|node_modules/|package\.json|\.vue$|\.ts$|\.js$|vite\.config|slidev\.config)"; then
  echo "❌ ERROR: contiene archivos prohibidos"
  exit 1
fi
echo "✓ Sin archivos prohibidos"

echo "✅ ZIP válido para InsightBloom"
```

## Caso: Migrar de ZIP completo a MVP

Si generaste un ZIP con `slidev build` que incluye `dist/`, `node_modules/`, `package.json`, etc., debes:

1. **Eliminar componentes Vue personalizados** (ej: `<Counter />`)
   - Reemplaza por contenido declarativo
   - O elimina la línea si no es crítica

2. **Copiar solo `slides.md`**
   ```bash
   cp presentaciones/mi-presentacion/slidev/slides.md ./staging/
   ```

3. **Copiar solo assets permitidos**
   ```bash
   cp -R presentaciones/mi-presentacion/assets/css ./staging/assets/
   cp -R presentaciones/mi-presentacion/assets/images ./staging/assets/
   ```

4. **Eliminar todo lo demás**
   - No incluyas `dist/`
   - No incluyas `node_modules/`
   - No incluyas `package.json`

5. **Crear ZIP desde staging**
   ```bash
   cd ./staging
   zip -r ../mi-presentacion-insightbloom.zip slides.md assets/
   ```

6. **Validar**
   ```bash
   unzip -t ../mi-presentacion-insightbloom.zip
   ```

## Ejemplo: `slidev-en-10-minutos` compatible

Para hacer compatible la presentación de ejemplo:

1. **El componente `<Counter />` es problema**
   - Reemplazar por HTML/CSS declarativo
   - O eliminar si no es crítico

2. **Generar ZIP correcto**
   ```bash
   just slidev-insightbloom-zip presentaciones/slidev-en-10-minutos/slidev
   ```

3. **Verificar**
   ```bash
   unzip -l slidev-en-10-minutos-insightbloom.zip
   ```

Contenido esperado:
```
slides.md
assets/css/theme.css
assets/images/.gitkeep
```

## Flujo en InsightBloom

```
Agente IA / Usuario
         │
         ├── crea mi-presentacion-insightbloom.zip
         ├── valida con just slidev-insightbloom-zip o unzip -t
         └── sube a InsightBloom (engine: Slidev)
                │
                ▼
         InsightBloom MVP
                │
                ├── extrae ZIP
                ├── encuentra slides.md
                ├── ejecuta @slidev/cli (versión controlada)
                ├── genera HTML + presenter mode
                └── publica para conferencia
```

InsightBloom **no usa** el `index.html` ni los bundles de un `dist/` generado localmente. Esto garantiza que la presentación pública, presenter mode, previews y exportaciones usen el engine controlado.

## Recursos

- [Guía Slidev local](./03-slidev.md)
- [Exportación de presentaciones](./04-exportacion.md)
- [Especificación completa del MVP](https://insightbloom.example.com/docs/slidev-mvp) (referencia)

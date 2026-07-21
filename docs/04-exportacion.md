# Exportación y ZIP para InsightBloom

Esta guía explica cómo empaquetar tu presentación Marp o Slidev en un ZIP transportable para importar en InsightBloom.

## ZIP de Marp

### Generar el ZIP

```bash
just zip mi-presentacion
```

O desde la línea de comandos:

```bash
./scripts/build-presentation-zip.sh presentaciones/mi-presentacion
```

### Estructura del ZIP

```
mi-presentacion.zip
├── README.md                       # Información de la presentación
├── manifest.json                   # Metadatos
├── mi-presentacion.pdf             # PDF exportado
├── mi-presentacion.odp             # ODP exportado
└── source/
    ├── mi-presentacion.md          # Archivo markdown fuente
    ├── assets/
    │   ├── css/
    │   │   └── theme.css           # Tema personalizado
    │   └── images/
    │       └── ...                 # Todas las imágenes
    └── .gitignore
```

### Qué se incluye

- **PDF**: Versión final en PDF
- **ODP**: Versión nativa de LibreOffice (editable)
- **Markdown fuente**: Para futuras ediciones o reconstrucción
- **Assets**: Imágenes y CSS utilizados
- **Metadatos**: Título, descripción, fecha, autor

### Importar en InsightBloom

1. Descomprime el ZIP
2. Copia el contenido a InsightBloom
3. Usa el `manifest.json` para metadatos
4. Sirve el PDF o abre con LibreOffice el ODP

## ZIP de Slidev

### Generar el ZIP

**Opción 1: ZIP completo (transportable, incluye fuente)**

```bash
just slidev-zip presentaciones/mi-presentacion/slidev
```

**Opción 2: ZIP para MVP de InsightBloom (recomendado)**

```bash
just slidev-insightbloom-zip presentaciones/mi-presentacion/slidev
```

⚠️ **Importante:** Si planeas subir a InsightBloom, usa **`slidev-insightbloom-zip`** que genera un ZIP compatible con el MVP (sin `dist/`, `node_modules/`, componentes Vue, etc.).

### Estructura del ZIP

```
mi-presentacion-slidev.zip
├── README.md                       # Instrucciones de uso
├── slidev.project.json             # Marca como proyecto Slidev
├── source/
│   ├── slides.md                   # Presentación fuente
│   ├── package.json                # Dependencias del proyecto
│   ├── slidev.config.ts            # Configuración Slidev
│   ├── vite.config.ts              # Configuración Vite
│   ├── components/                 # Componentes Vue (si existen)
│   │   └── ...
│   └── public/                     # Assets (imágenes, etc.)
│       └── ...
└── dist/
    ├── index.html                  # HTML estática (listo para usar)
    ├── assets/
    │   ├── *.js
    │   ├── *.css
    │   └── *.png
    └── ...
```

### Qué se incluye

- **HTML estática** (`dist/index.html`): Presentación compilada, lista para servir directamente
- **Fuente Slidev** (`source/`): Archivo markdown, configuración y componentes
- **Metadatos** (`slidev.project.json`): Identificación del proyecto
- **Assets**: Imágenes y recursos

### Importar en InsightBloom

**Opción 1: Usar HTML precompilado (más rápido)**

```bash
unzip mi-presentacion-slidev.zip
cp -r dist/ /var/www/presentaciones/mi-presentacion/
```

Sirve directamente desde tu servidor web.

**Opción 2: Reconstruir desde fuente (para personalizaciones)**

```bash
unzip mi-presentacion-slidev.zip
cd source/
npm install
npm run build
# Genera dist/ nuevo
cp -r dist/ /var/www/presentaciones/mi-presentacion/
```

### Ventajas del ZIP de Slidev

- ✅ Presentación web interactiva (presenter mode, animaciones)
- ✅ Totalmente reconstruible desde fuente
- ✅ Componentes Vue y scripts ejecutables
- ✅ Portable y sin dependencias externas

## manifest.json (Marp)

El ZIP de Marp incluye un `manifest.json` con metadatos:

```json
{
  "format": "marp",
  "version": "1.0",
  "title": "Mi presentación increíble",
  "description": "Una presentación técnica sobre ...",
  "author": "Tu nombre",
  "date": "2026-07-21",
  "tags": ["ia", "desarrollo", "opensource"],
  "files": {
    "pdf": "mi-presentacion.pdf",
    "odp": "mi-presentacion.odp",
    "source": "source/mi-presentacion.md"
  }
}
```

## slidev.project.json (Slidev)

El ZIP de Slidev incluye un `slidev.project.json`:

```json
{
  "format": "slidev",
  "version": "1.0",
  "title": "Mi presentación increíble",
  "description": "Una presentación técnica con Slidev",
  "author": "Tu nombre",
  "date": "2026-07-21",
  "entry": "dist/index.html",
  "source": "source/slides.md"
}
```

## Comparación: ¿Cuál ZIP elegir?

| Aspecto | Marp | Slidev (Completo) | Slidev (MVP) |
|---|---|---|---|
| **Comando** | `just zip` | `just slidev-zip` | `just slidev-insightbloom-zip` |
| **Tamaño** | Pequeño (~2-5 MB) | Grande (~20-50 MB) | Pequeño (~1-2 MB) |
| **Incluye** | PDF, ODP, fuente | Fuente + dist/ + node_modules/ | Solo slides.md + assets |
| **Reconstruible** | Con Marp CLI | Con `npm install && npm run build` | Solo lectura (compila en InsightBloom) |
| **Componentes Vue** | No | Sí | No permitidos |
| **Para InsightBloom** | No soportado | Soportado pero innecesario | ✅ **Recomendado** |
| **Para archivo local** | ✅ Sí | ✅ Sí | No (necesita servidor) |

**Decisión:**
- **Marp:** `just zip mi-presentacion`
- **Slidev local/portabilidad:** `just slidev-zip presentaciones/mi-presentacion/slidev`
- **Slidev para InsightBloom MVP:** `just slidev-insightbloom-zip presentaciones/mi-presentacion/slidev` ✅

## Subir a InsightBloom

### Requisitos

1. Acceso a la plataforma InsightBloom
2. Permiso para crear/importar presentaciones
3. Cuota de almacenamiento disponible

### Pasos

1. **Generar el ZIP**
   ```bash
   just zip mi-presentacion                    # Marp
   # o
   just zip mi-presentacion --engine slidev    # Slidev
   ```

2. **Iniciar sesión en InsightBloom**
   - Accede a tu panel de control

3. **Importar presentación**
   - Botón "Importar" o "Upload ZIP"
   - Selecciona el archivo `.zip` generado
   - Verifica metadatos (título, descripción, etc.)

4. **Publicar**
   - Confirma los detalles
   - Establece permisos (público/privado)
   - Obtén URL de compartir

## Personalizar metadatos del ZIP

### Para Marp

Edita `manifest.json` antes de hacer el ZIP:

```json
{
  "format": "marp",
  "version": "1.0",
  "title": "Mi presentación increíble",
  "description": "Una presentación técnica sobre IA y desarrollo.",
  "author": "Tu nombre",
  "tags": ["ia", "desarrollo", "opensource"],
  "license": "CC-BY-4.0",
  "keywords": ["machine learning", "open source"]
}
```

### Para Slidev

Edita `slidev.config.ts`:

```typescript
import { defineConfig } from '@slidev/cli'

export default defineConfig({
  title: 'Mi presentación increíble',
  author: 'Tu nombre',
  keywords: 'ia,desarrollo,opensource',
  presenter: true,
  download: true,
})
```

## Troubleshooting

### ZIP de Marp no genera PDF/ODP

```bash
# Verifica que Marp CLI está instalado
npm list --prefix presentaciones | grep marp

# Reinstala si es necesario
npm install --prefix presentaciones
```

### ZIP de Slidev muy grande

- Elimina `node_modules/` antes de comprimir
- Solo incluye `dist/` compilado
- Comprime con `--engine slidev` automáticamente

### No puedo servir el HTML de Slidev

- Asegúrate de que `dist/` está completo
- Verifica rutas de assets en `dist/assets/`
- Usa un servidor web (no `file://`)

## Recursos

- [Guía Marp](./02-marp.md)
- [Guía Slidev](./03-slidev.md)
- [Documentación de Slidev export](https://sli.dev/guide/exporting.html)
- [Documentación de Marp CLI](https://github.com/marp-team/marp-cli)

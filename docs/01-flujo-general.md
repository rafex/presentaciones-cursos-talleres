# Flujo general: Crear una presentación

## Decisión: ¿Marp o Slidev?

Antes de crear, decide qué motor usar. Ambos son independientes; puedes tener ambos en el mismo repositorio.

### Marp: Presentación tradicional

Usa Marp si necesitas:
- Exportar a **PDF y ODP** (formato nativo de LibreOffice)
- Presentación clásica de diapositivas
- Publicar en múltiples formatos rápidamente
- Workflow simple y robusto

**No uses Marp si necesitas:**
- Demos en vivo o componentes interactivos
- Animaciones CSS complejas
- Presenter mode web integrado

### Slidev: Presentación web interactiva

Usa Slidev si necesitas:
- Presentación web con **presenter mode** (notas, navegación privada)
- **Demos en vivo** (código ejecutable, componentes Vue)
- Animaciones y transiciones avanzadas
- **Diagramas Mermaid interactivos**
- CSS y layouts personalizados

**No uses Slidev si:**
- Solo necesitas PDF y ODP
- La presentación es muy simple
- Necesitas máxima portabilidad

## Estructura de directorios

Ambos motores usan la misma estructura base; la diferencia está en los archivos internos.

### Marp
```
presentaciones/mi-presentacion/
├── mi-presentacion.md          # Archivo principal (Marp Markdown)
└── assets/
    ├── css/
    │   └── theme.css           # Tema personalizado
    └── images/
        └── ...                 # Imágenes de la presentación
```

### Slidev
```
presentaciones/mi-presentacion/
├── slidev/
│   ├── slides.md               # Archivo principal (Slidev Markdown)
│   ├── vite.config.ts          # Configuración Vite
│   ├── package.json            # Dependencias Slidev
│   ├── slidev.config.ts        # Configuración Slidev
│   ├── public/                 # Assets compartidos (enlace a ../assets)
│   └── components/             # Componentes Vue personalizados (opcional)
└── assets/
    ├── css/
    │   └── theme.css           # Tema (opcional; Slidev usa CSS directo)
    └── images/
        └── ...                 # Imágenes de la presentación
```

## Proceso de creación: Paso a paso

### 1. Crear la carpeta y archivos base

**Marp:**
```bash
./scripts/new-presentacion.sh
# Ingresa el nombre: mi-presentacion
# Ingresa el título: Mi presentación increíble
```

**Slidev:**
```bash
./scripts/new-presentacion.sh --engine slidev
# Ingresa el nombre: mi-presentacion
# Ingresa el título: Mi presentación increíble
```

### 2. Editar el contenido

- **Marp:** Edita `presentaciones/mi-presentacion/mi-presentacion.md`
- **Slidev:** Edita `presentaciones/mi-presentacion/slidev/slides.md`

Ver [Guía Marp](./02-marp.md) o [Guía Slidev](./03-slidev.md) para sintaxis específica.

### 3. Personalizar el tema

- **Marp:** Edita `presentaciones/mi-presentacion/assets/css/theme.css`
- **Slidev:** Crea `presentaciones/mi-presentacion/slidev/theme.css` o personaliza en el frontmatter

### 4. Generar salida

**Marp:**
```bash
just generate mi-presentacion       # PDF + ODP
just generate mi-presentacion pdf   # Solo PDF
```

**Slidev:**
```bash
just slidev-dev presentaciones/mi-presentacion/slidev/slides.md  # Modo dev
just slidev-export presentaciones/mi-presentacion/slidev/slides.md pdf
```

### 5. Empaquetar para InsightBloom

Ambos motores generan un ZIP listo para importar:

```bash
just zip mi-presentacion                    # Marp (por defecto)
just zip mi-presentacion --engine slidev    # Slidev
```

## Convenciones de nombres

| Elemento | Formato | Ejemplo |
|---|---|---|
| Directorio | kebab-case, minúsculas | `mi-presentacion`, `crea-tu-agente-ia` |
| Archivo MD | snake_case (Marp) o slides.md (Slidev) | `mi_presentacion.md`, `slidev/slides.md` |
| Título | Título normal con capitales | `Mi presentación increíble`, `Cómo crear un agente de IA` |

## Portal local

Para ver todas tus presentaciones (Marp y Slidev) en un catálogo navegable:

```bash
just portal-dev
```

Se abre en <http://localhost:4173>. Ambos motores se mostrarán con sus respectivos badges.

## Próximos pasos

1. Lee [Guía Marp](./02-marp.md) si vas a usar Marp
2. Lee [Guía Slidev](./03-slidev.md) si vas a usar Slidev
3. Lee [Exportación y ZIP](./04-exportacion.md) cuando esté lista la presentación para publicar

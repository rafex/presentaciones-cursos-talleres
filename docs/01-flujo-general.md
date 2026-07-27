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

### Marp (presentaciones y talleres)
```
presentaciones/mi-presentacion/ # o talleres/mi-taller/
├── mi-presentacion.md          # Archivo principal (Marp Markdown)
├── cronograma.md               # Agenda, prácticas y ronda de preguntas
└── assets/
    ├── css/
    │   └── theme.css           # Tema personalizado
    └── images/
        └── ...                 # Imágenes de la presentación
```

### Slidev como engine adicional
```
presentaciones/mi-presentacion/ # o talleres/mi-taller/
├── mi-presentacion.md          # Marp se conserva como fuente principal
├── cronograma.md               # Agenda común para conferencia o taller
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

**Slidev (opcional para talleres y presentaciones):**
```bash
./scripts/new-taller.py "mi-taller" "Mi taller" "python" "vscode" --engine slidev
# Ingresa el nombre: mi-presentacion
# Ingresa el título: Mi presentación increíble
```

### 2. Editar el contenido

- **Marp:** Edita `presentaciones/mi-presentacion/mi-presentacion.md`
- **Slidev:** Edita `presentaciones/mi-presentacion/slidev/slides.md` o
  `talleres/mi-taller/slidev/slides.md`
- **Cronograma:** Completa siempre `cronograma.md` con tiempos, explicación,
  actividad de participantes y la ronda final de preguntas.

Ver [Guía Marp](./02-marp.md) o [Guía Slidev](./03-slidev.md) para sintaxis específica.

### 3. Personalizar el tema

- **Marp:** Edita `presentaciones/mi-presentacion/assets/css/theme.css`
- **Slidev:** Crea `presentaciones/mi-presentacion/slidev/theme.css` o personaliza en el frontmatter

### 4. Generar salida

**Marp:**
```bash
just generate mi-presentacion                 # Genera PDF y ODP
just generate mi-presentacion pdf             # Genera sólo PDF
just generate mi-taller pdf -t taller         # PDF de un taller
```

**Slidev:**
```bash
just slidev-dev presentaciones/mi-presentacion/slidev/slides.md
just slidev-export presentaciones/mi-presentacion/slidev/slides.md pdf
```

`just` ejecuta recetas definidas en el archivo `Justfile` desde la raíz del
repositorio. La forma general es `just <receta> <argumentos>`:

| Comando | Qué hace | Cuándo usarlo |
|---|---|---|
| `just generate <nombre>` | Busca el material Marp y genera PDF/ODP. | Para la salida tradicional. |
| `just slidev-dev <nombre>` | Levanta Slidev en modo desarrollo; también acepta la ruta a `slides.md`. | Mientras editas y quieres recarga automática. |
| `just slidev-export <nombre> pdf` | Resuelve `slidev/slides.md` y exporta a PDF, PPTX o PNG; también acepta una ruta. | Para entregar una copia estática. |
| `just zip <nombre>` | Crea un ZIP para InsightBloom. Usa Marp si no indicas otro motor. | Para publicar la presentación. |
| `just zip <nombre> --engine slidev` | Crea el ZIP usando `slidev/slides.md`, sin borrar la fuente Marp. | Para publicar la versión Slidev. |

Opciones útiles:

- `-t taller` indica que el nombre se debe buscar en `talleres/`.
- `-t presentation` indica que se debe buscar en `presentaciones/`.
- `--engine marp` o `--engine slidev` elige qué fuente se empaqueta.
- `slidev-dev` y `slidev-export` aceptan el nombre del proyecto o la ruta al
  archivo `slides.md`; `just zip` recibe el nombre del proyecto.

### 5. Empaquetar para InsightBloom

Ambos motores generan un ZIP listo para importar:

```bash
just zip mi-presentacion                     # Empaqueta Marp por defecto
just zip mi-taller mi-taller.md -t taller    # Empaqueta el Markdown Marp del taller
just zip mi-taller --engine slidev -t taller # Empaqueta talleres/mi-taller/slidev/slides.md
```

En ambos casos Marp y Slidev son fuentes paralelas: los ejercicios siguen
viviendo en `ejercicios/` y no se reemplazan al crear `slidev/`.

## Convenciones de nombres

| Elemento | Formato | Ejemplo |
|---|---|---|
| Directorio | kebab-case, minúsculas | `mi-presentacion`, `crea-tu-agente-ia` |
| Archivo MD | snake_case (Marp) o slides.md (Slidev) | `mi_presentacion.md`, `slidev/slides.md` |
| Título | Título normal con capitales | `Mi presentación increíble`, `Cómo crear un agente de IA` |
| Cronograma | `cronograma.md` obligatorio | Agenda de 90 minutos con práctica y 15 min de preguntas |

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

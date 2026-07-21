# Documentación: Crear y publicar presentaciones

Este directorio contiene los manuales para crear presentaciones usando **Marp** o **Slidev**.

## Guía rápida

Elige el motor que mejor se adapte a tu presentación:

| Necesidad | Motor | Complejidad |
|---|---|---|
| Presentación estándar, PDF + ODP de archivo | **Marp** | Baja |
| Demos en vivo, animaciones, Mermaid interactivo, Web con presenter mode | **Slidev** | Media-Alta |

## Documentos

- **[Flujo general](./01-flujo-general.md)** — Cómo funciona la creación de presentaciones
- **[Guía Marp](./02-marp.md)** — Paso a paso para crear una presentación con Marp
- **[Guía Slidev](./03-slidev.md)** — Paso a paso para crear una presentación con Slidev
- **[Exportación y ZIP](./04-exportacion.md)** — Cómo empaquetar tu presentación para InsightBloom
- **[ZIP InsightBloom MVP Slidev](./05-insightbloom-mvp.md)** — Formato específico del MVP (sin dist/, node_modules/, componentes Vue)

## Inicio rápido

### Crear una presentación (elige una opción)

**Marp (recomendado para mayoría de casos):**
```bash
./scripts/new-presentacion.sh
# Sigue el asistente interactivo
# Elige: motor = marp
```

**Slidev (para presentaciones técnicas avanzadas):**
```bash
./scripts/new-presentacion.sh
# Sigue el asistente interactivo
# Elige: motor = slidev
```

### Generar y exportar

**Marp:**
```bash
just generate <nombre>              # Genera PDF y ODP
just zip <nombre>                   # Empaqueta para InsightBloom
```

**Slidev:**
```bash
just slidev-dev presentaciones/<nombre>/slidev/slides.md    # Modo desarrollo
just slidev-export presentaciones/<nombre>/slidev/slides.md pdf  # Exportar PDF
just zip <nombre> --engine slidev   # Empaqueta para InsightBloom
```

## Convenciones del repositorio

- **Nombres:** minúsculas, con guiones (ej: `mi-presentacion`)
- **Estructura:** `presentaciones/<nombre>/` o `talleres/<nombre>/`
- **Motor:** Se define al crear; Marp o Slidev son independientes
- **Salida:** PDF + ODP (Marp), PDF/PPTX/PNG (Slidev), ZIP para InsightBloom (ambos)

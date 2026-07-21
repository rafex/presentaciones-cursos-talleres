# Guía Marp: Crear una presentación

Marp (Markdown Presentation Ecosystem) convierte Markdown en presentaciones de diapositivas con soporte para PDF, ODP, HTML y más.

## Crear tu primera presentación Marp

### Paso 1: Generar la estructura

```bash
./scripts/new-presentacion.sh
```

Ingresa:
- **Nombre:** `mi-presentacion` (se convierte automáticamente a kebab-case)
- **Título:** `Mi presentación increíble`

Esto crea:
```
presentaciones/mi-presentacion/
├── mi-presentacion.md
└── assets/
    ├── css/
    │   └── theme.css
    └── images/
```

### Paso 2: Editar la presentación

Abre `presentaciones/mi-presentacion/mi-presentacion.md` y reemplaza el contenido con tu presentación.

**Estructura básica:**

```markdown
---
marp: true
title: Mi presentación increíble
description: Una presentación técnica sobre ...
theme: default
paginate: true
footer: © 2026 Mi nombre
---

# Slide 1: Portada

Mi presentación increíble

---

# Slide 2: Contenido

Contenido aquí

- Punto 1
- Punto 2
- Punto 3

---

## Slide 3: Código

```python
def hola():
    print("Hola mundo")
```
```

### Paso 3: Personalizar el tema

Edita `presentaciones/mi-presentacion/assets/css/theme.css` para personalizar colores, tipografía y estilos.

**Ejemplo mínimo:**

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

section {
  font-family: 'Inter', sans-serif;
  font-size: 32px;
  color: #1a1a1a;
  background: #ffffff;
  padding: 60px;
}

h1, h2, h3 {
  color: #0066cc;
  margin-bottom: 20px;
}

code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
}
```

## Sintaxis Marp: Diapositivas

### Diapositivas básicas

```markdown
# Título principal

---

## Subtítulo

Contenido aquí

---

### Sección más pequeña

- Punto 1
- Punto 2
```

Cada `---` es un separador de diapositiva.

### Directivas de diapositiva

Las directivas controlan el comportamiento individual de cada slide:

```markdown
<!-- _class: lead -->
# Diapositiva con estilo "lead" (centrada, grande)

---

<!-- _footer: "Pie personalizado para esta slide" -->
## Slide con pie personalizado

---

<!-- _paginate: false -->
# Slide sin número de página

---

<!-- _backgroundColor: #123456 -->
# Slide con fondo personalizado

---

![bg](./assets/images/fondo.png)
# Slide con fondo de imagen (llena la slide)

---

![bg left](./assets/images/lateral.png)
# Contenido a la derecha, imagen a la izquierda
```

### Dos columnas

```markdown
<!-- _class: two-columns -->

## Izquierda

- Punto A
- Punto B

---

## Derecha

- Punto X
- Punto Y
```

### Listas y énfasis

```markdown
## Contenido

- Punto principal
  - Sub-punto
  - Otro sub-punto
- Punto 2

**Texto en negrita**
*Texto en itálica*
`código inline`

> Cita destacada
```

### Código

```markdown
## Ejemplo de código

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

---

## Código con highlight de línea

```javascript
// highlight: 2,5-7
function hola() {
  console.log("Hola");
  
  for (let i = 0; i < 5; i++) {
    console.log(i);
  }
}
```
```

### Imágenes y figuras

```markdown
## Imagen centrada

![w:300px](./assets/images/logo.png)

---

## Imagen a tamaño específico

![h:400px](./assets/images/diagram.png)

---

## Imagen con caption

![](./assets/images/foto.jpg)
*Esto es un caption*
```

### Tablas

```markdown
## Tabla de datos

| Encabezado 1 | Encabezado 2 |
|---|---|
| Celda A1 | Celda B1 |
| Celda A2 | Celda B2 |

---

## Tabla con alineación

| Izquierda | Centro | Derecha |
|:---|:---:|---:|
| A | B | C |
| 1 | 2 | 3 |
```

## Generar salida

### PDF

```bash
just generate mi-presentacion pdf
```

Genera: `presentaciones/mi-presentacion/mi-presentacion.pdf`

### ODP (LibreOffice)

```bash
just generate mi-presentacion odp
```

Genera: `presentaciones/mi-presentacion/mi-presentacion.odp`

### Ambos

```bash
just generate mi-presentacion all
# o simplemente:
just generate mi-presentacion
```

### HTML (para web)

```bash
./scripts/generate-slides.sh presentaciones/mi-presentacion html
```

## Exportar para InsightBloom

Cuando tu presentación esté lista para publicar:

```bash
just zip mi-presentacion
```

Genera: `mi-presentacion.zip` con estructura:

```
mi-presentacion.zip
├── mi-presentacion.pdf
├── mi-presentacion.odp
├── source/
│   ├── mi-presentacion.md
│   └── assets/
│       ├── css/theme.css
│       └── images/
└── manifest.json
```

## Frontmatter completo (opciones de Marp)

```markdown
---
marp: true                           # Habilita Marp
title: Título de la presentación     # Título en navegador
description: Descripción             # Meta descripción
theme: default                       # Tema: default, gaia, uncover
class: invert                        # Clase global: invert, lead, etc.
paginate: true                       # Mostrar número de página
style: |                             # CSS embebido (opcional)
  section {
    font-size: 32px;
  }
footer: © 2026 Mi nombre             # Pie de página global
---
```

## Temas predefinidos

Marp incluye temas listos para usar. Cámbialos en el frontmatter:

- **default** — Tema neutro y limpio
- **gaia** — Tema moderno con gradientes
- **uncover** — Tema minimalista

```markdown
---
marp: true
theme: gaia
---
```

O crea tu propio tema en `assets/css/theme.css` (se aplica automáticamente).

## Ejemplos en el repositorio

Mira estas presentaciones Marp como referencia:

- [Desarrollando con IA](../presentaciones/desarrollando-con-ia/desarrollando_con_ia.md)
- [De estudiante a desarrollador](../presentaciones/de-estudiante-a-desarrollador-y-a-trabajador/de_estudiante_a_desarrollador_y_a_trabajador.md)
- [Boost desarrollo con IA](../presentaciones/boost-desarrollo-con-ia-con-opensource/boost-desarrollo-con-ia-con-opensource.md)

Revisa su estructura, frontmatter y directivas como referencia.

## Recursos

- [Marp Dokumentation](https://marpit.marp.app/)
- [Marp CLI](https://github.com/marp-team/marp-cli)
- [Temas Marp](https://marp.app/#themes)

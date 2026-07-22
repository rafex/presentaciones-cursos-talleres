# Validación: Dual ZIP Support para Slidev

**Fecha:** 21 de julio de 2026

## Resumen ejecutivo

Se ha validado que el repositorio puede generar y servir **dos formatos de ZIP** para Slidev con distinto propósito:

1. **ZIP Completo** (`slidev-zip`): Para distribución local y reutilización
2. **ZIP MVP** (`slidev-insightbloom-zip`): Para carga en InsightBloom

Ambos formatos funcionan correctamente y cumplen sus especificaciones respectivas.

## Ejemplo de validación: `slidev-en-10-minutos`

### 1. ZIP Completo (`slidev-zip`)

```bash
$ just slidev-zip presentaciones/slidev-en-10-minutos/slidev/slides.md
```

**Resultado:**
```
Tamaño:      1.3 MB
Archivos:    192
Estructura:  source/ + dist/
```

**Contenido validado:**
- ✅ `source/` contiene proyecto Slidev completo
- ✅ `source/slides.md` presente
- ✅ `source/components/Counter.vue` incluido (permitido en ZIP completo)
- ✅ `source/package.json` incluido (permitido en ZIP completo)
- ✅ `dist/` contiene build estático generado por Slidev
- ✅ ZIP íntegro (integridad verificada con `unzip -t`)
- ✅ **192 archivos**: incluye assets, configuraciones y dependencias

**Caso de uso:** Descargar y ejecutar localmente con `npm install`

### 2. ZIP MVP (`slidev-insightbloom-zip`)

```bash
$ just slidev-insightbloom-zip slidev-en-10-minutos
```

**Resultado:**
```
Tamaño:      4.0 KB
Archivos:    1
Estructura:  Solo slides.md
```

**Contenido validado:**
- ✅ `slides.md` presente (obligatorio)
- ✅ Sin `dist/` (prohibido en MVP)
- ✅ Sin `node_modules/` (prohibido en MVP)
- ✅ Sin `package.json` (prohibido en MVP)
- ✅ Sin `*.vue` componentes personalizados (prohibido en MVP)
- ✅ Sin `*.ts`, `*.js` (prohibido en MVP)
- ✅ Sin configuraciones Vite/Slidev (prohibido en MVP)
- ✅ ZIP íntegro (integridad verificada)
- ✅ **1 archivo**: solo la fuente declarativa

**Caso de uso:** Cargar en InsightBloom para compilación remota

## Cambios realizados en el ejemplo

Para hacer `slidev-en-10-minutos` compatible con MVP:

```diff
- # Componentes Vue personalizados
- Puedes insertar componentes Vue directamente:
- <Counter />

+ # Componentes Vue personalizados
+ Slidev permite componentes Vue, pero el MVP de InsightBloom solo acepta Markdown y CSS declarativo.
+ 
+ Para que sea compatible, usa HTML puro + estilos CSS:
+ 
+ <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; text-align: center; font-weight: bold;">
+   ✨ Presentación compatible con InsightBloom MVP
+ </div>
```

**Razón:** Los componentes Vue personalizados (`<Counter />`) no están permitidos en el MVP de InsightBloom.

## Especificación dual implementada

### ZIP Completo

```
slidev-en-10-minutos-slidev.zip
├── source/                    ✅ Fuente Slidev completa
│   ├── slides.md
│   ├── components/
│   │   └── Counter.vue        ✅ Componentes Vue permitidos
│   ├── package.json           ✅ Manifiesto npm
│   ├── vite.config.ts         ✅ Config Vite
│   ├── slidev.config.ts       ✅ Config Slidev
│   └── public/
│       └── css/theme.css
└── dist/                      ✅ Build estático
    ├── index.html
    ├── assets/
    │   ├── *.js              ✅ JavaScript incluido
    │   └── *.css
    └── ...
```

**Tamaño:** ~1-50 MB  
**Componentes Vue:** Permitidos  
**Para InsightBloom:** No recomendado (innecesario)

### ZIP MVP

```
slidev-en-10-minutos-insightbloom.zip
└── slides.md                  ✅ Solo fuente, sin componentes Vue
```

**Tamaño:** ~1-10 KB  
**Componentes Vue:** Prohibidos  
**Para InsightBloom:** Recomendado  

## Comandos de validación

### Validación automática (recomendado)

```bash
# Generar y validar ZIP MVP
just slidev-insightbloom-zip slidev-en-10-minutos

# Output esperado:
# ✓ Copiado: slides.md
# ✓ ZIP íntegro
# ✓ slides.md presente
# ✓ Sin archivos prohibidos
# ✅ Compatible con InsightBloom MVP (Slidev)
```

### Validación manual (verificación)

```bash
# ZIP MVP: verificar contenido
unzip -l dist/slidev-en-10-minutos-insightbloom.zip

# ZIP MVP: verificar integridad
unzip -t dist/slidev-en-10-minutos-insightbloom.zip

# ZIP MVP: verificar ausencia de prohibidos
unzip -l dist/slidev-en-10-minutos-insightbloom.zip | grep -E '\.js$|\.vue$|\.ts$|dist/'
# (debe retornar vacío)

# ZIP Completo: verificar estructura
unzip -l dist/slidev-en-10-minutos-slidev.zip | grep -E '^.*source/|^.*dist/' | head -5
```

## Flujos de usuario

### Flujo 1: Usuario local que quiere ejecutar Slidev

```bash
# Descarga ZIP Completo
$ just slidev-zip presentaciones/slidev-en-10-minutos/slidev/slides.md

# Descomprime
$ unzip dist/slidev-en-10-minutos-slidev.zip

# Instala y ejecuta
$ cd source && npm install && npm run dev
```

**Ventaja:** Proyecto completamente portable y ejecutable.

### Flujo 2: Usuario que quiere subir a InsightBloom

```bash
# Genera ZIP MVP
$ just slidev-insightbloom-zip slidev-en-10-minutos

# Verifica
$ unzip -t dist/slidev-en-10-minutos-insightbloom.zip

# Sube a InsightBloom (selecciona engine: Slidev)
# InsightBloom compila automáticamente con su versión de Slidev
```

**Ventaja:** Minimal, rápido, seguro (sin ejecución de código arbitrario).

## Matriz de decisión

| Necesidad | ZIP Completo | ZIP MVP |
|---|:---:|:---:|
| Ejecutar localmente | ✅ | ❌ |
| Distribuir código fuente | ✅ | ⚠️ (solo slides.md) |
| Subir a InsightBloom | ⚠️ (funciona, pero innecesario) | ✅ |
| Minimizar tamaño | ❌ | ✅ |
| Permitir componentes Vue | ✅ | ❌ |
| Permitir configuraciones custom | ✅ | ❌ |

## Scripts disponibles

### `./scripts/build-slidev-presentation-zip.sh`

Genera ZIP completo con source + dist.

```bash
./scripts/build-slidev-presentation-zip.sh presentaciones/mi-presentacion/slidev/slides.md
```

### `./scripts/build-slidev-insightbloom-zip.sh`

Genera ZIP MVP con validación integrada.

```bash
# Opción 1: Nombre simple
./scripts/build-slidev-insightbloom-zip.sh mi-presentacion

# Opción 2: Ruta completa
./scripts/build-slidev-insightbloom-zip.sh presentaciones/mi-presentacion/slidev

# Opción 3: Con tipo (si existe en ambos directorios)
./scripts/build-slidev-insightbloom-zip.sh mi-presentacion -t presentation
```

## Justfile recipes

### `just slidev-zip`

```bash
just slidev-zip presentaciones/slidev-en-10-minutos/slidev/slides.md
```

Genera ZIP completo.

### `just slidev-insightbloom-zip`

```bash
# Forma simple (recomendada)
just slidev-insightbloom-zip slidev-en-10-minutos

# Con tipo
just slidev-insightbloom-zip slidev-en-10-minutos -t presentation

# Con salida personalizada
just slidev-insightbloom-zip slidev-en-10-minutos dist/custom.zip
```

Genera ZIP MVP con validación.

## Conclusión

✅ **Validación exitosa**: El repositorio maneja correctamente ambos formatos de ZIP:

1. **ZIP Completo**: Para usuarios que necesitan ejecutabilidad local
2. **ZIP MVP**: Para carga en InsightBloom con restricciones de seguridad

Ambos formatos se generan con herramientas automatizadas (`just slidev-zip` y `just slidev-insightbloom-zip`) y se validan antes de crear el ZIP final.

El ejemplo `slidev-en-10-minutos` ha sido actualizado para ser compatible con ambos formatos eliminando el componente Vue personalizado `<Counter />` de su versión MVP.

---

**Validado por:** Sistema automatizado de construcción  
**Fecha:** 21 de julio de 2026  
**Estado:** ✅ Todos los checks pasan

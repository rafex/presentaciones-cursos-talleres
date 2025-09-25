# Generación de presentaciones

Para generar las presentaciones en formato PDF y ODP a partir de los archivos Markdown, utiliza el script `generate.sh`.

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
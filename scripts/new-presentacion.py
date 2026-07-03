#!/usr/bin/env python3
"""
Crea una nueva presentación/ponencia bajo presentaciones/<nombre>/
respetando la convención del repo.

Uso:
  ./scripts/new-presentacion.py                    # Modo interactivo
  ./scripts/new-presentacion.py "nombre" "título"  # No interactivo
"""

import sys
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

def normalize_name(name: str) -> str:
    """
    Normaliza el nombre: minúsculas, espacios→guiones, sin caracteres especiales.
    """
    # Convertir a minúsculas
    name = name.lower()
    # Reemplazar espacios por guiones
    name = re.sub(r'\s+', '-', name)
    # Eliminar caracteres que no sean a-z, 0-9, -
    name = re.sub(r'[^a-z0-9-]', '', name)
    # Limpiar múltiples guiones
    name = re.sub(r'-+', '-', name)
    # Eliminar guiones al inicio y final
    name = name.strip('-')
    return name

def prompt(msg: str, default: str = None) -> str:
    """Pide entrada del usuario con opción de default."""
    if default:
        user_input = input(f"{msg} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{msg}: ").strip()
            if user_input:
                return user_input
            print("  ⚠️  No puede estar vacío, intenta de nuevo.")

def get_fecha_actual() -> str:
    """Retorna la fecha actual en formato: "3 julio 2026" """
    ahora = datetime.now()
    dia = ahora.day
    mes = MESES_ES[ahora.month - 1]
    anio = ahora.year
    return f"{dia} {mes} {anio}"

def main():
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    templates_dir = script_dir / "templates"
    
    # Procesar argumentos
    nombre = None
    titulo = None
    
    if len(sys.argv) > 1:
        # Modo no interactivo: todos los args después del primero son parte del nombre
        # Si hay 2 args: nombre y título
        # Si hay más: tomar primero como nombre, concatenar el resto con espacios como título
        if len(sys.argv) == 2:
            nombre = sys.argv[1]
        elif len(sys.argv) >= 3:
            nombre = sys.argv[1]
            titulo = " ".join(sys.argv[2:])
    
    # Modo interactivo si no hay argumentos
    if not nombre:
        nombre = prompt("Nombre de la presentación (espacios se convierten a guiones)")
    
    if not nombre:
        print("❌ Error: el nombre no puede estar vacío.", file=sys.stderr)
        sys.exit(1)
    
    # Normalizar nombre
    nombre_normalizado = normalize_name(nombre)
    
    if not nombre_normalizado:
        print(f"❌ Error: el nombre '{nombre}' resultó vacío después de normalizar.", file=sys.stderr)
        sys.exit(1)
    
    # Verificar si ya existe
    pres_dir = repo_root / "presentaciones" / nombre_normalizado
    if pres_dir.exists():
        print(f"❌ Error: 'presentaciones/{nombre_normalizado}' ya existe.", file=sys.stderr)
        sys.exit(1)
    
    # Pedir título si no lo tenemos
    if not titulo:
        titulo = prompt("Título de la charla", nombre_normalizado)
    
    # Obtener fecha
    fecha = get_fecha_actual()
    
    # Crear estructura de directorios
    print(f"\n📁 Creando presentaciones/{nombre_normalizado} ...")
    (pres_dir / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (pres_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    
    # Crear archivo principal .md
    template_md = templates_dir / "presentacion.md"
    with open(template_md, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Reemplazar placeholders
    contenido = contenido.replace("__TITULO__", titulo)
    contenido = contenido.replace("__FECHA__", fecha)
    
    output_md = pres_dir / f"{nombre_normalizado}.md"
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    # Copiar theme.css
    template_css = templates_dir / "theme.css"
    output_css = pres_dir / "assets" / "css" / "theme.css"
    shutil.copy(template_css, output_css)
    
    # Crear .gitkeep
    (pres_dir / "assets" / "images" / ".gitkeep").touch()
    
    print(f"✅ Presentación creada en presentaciones/{nombre_normalizado}\n")
    print("Estructura:")
    for p in sorted(pres_dir.rglob('*')):
        rel_path = p.relative_to(repo_root)
        print(f"  {rel_path}")
    
    print("\n📋 Próximos pasos:")
    print(f"  - Edita presentaciones/{nombre_normalizado}/{nombre_normalizado}.md")
    print(f"  - Personaliza presentaciones/{nombre_normalizado}/assets/css/theme.css")
    print(f"  - just generate {nombre_normalizado} -t presentation")
    print(f"  - Cuando esté lista: crea presentaciones/{nombre_normalizado}/.release.yaml")
    print(f"    (ver presentaciones/boost-desarrollo-con-ia-con-opensource/.release.yaml)")

if __name__ == "__main__":
    main()

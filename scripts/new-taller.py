#!/usr/bin/env python3
"""
Crea un nuevo taller bajo talleres/<nombre>/
Uso:
  ./scripts/new-taller.py                              # Modo interactivo
  ./scripts/new-taller.py "nombre" "título"            # Con título
  ./scripts/new-taller.py "nombre" "título" "python"   # Con lenguajes
  ./scripts/new-taller.py "nombre" "título" "python" "vscode" --engine slidev

El motor predeterminado es Marp. `--engine slidev` agrega una fuente Slidev
paralela; no elimina ni reemplaza la presentación Marp.
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

LENGUAJES_DISPONIBLES = ["go", "java", "jetbrains", "macos", "node", "python", "security", "vscode"]
IDES_DISPONIBLES = ["vscode", "jetbrains"]

def normalize_name(name: str) -> str:
    """Normaliza el nombre: minúsculas, espacios→guiones, sin caracteres especiales."""
    name = name.lower()
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'[^a-z0-9-]', '', name)
    name = re.sub(r'-+', '-', name)
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

def prompt_multiselect(msg: str, options: list) -> list:
    """Pide selección múltiple (separada por espacios o comas)."""
    print(f"\n{msg}")
    print(f"  Disponibles: {', '.join(options)}")
    user_input = input("  Selecciona (espacio o coma separados): ").strip()
    
    if not user_input:
        return []
    
    # Separar por espacio o coma
    selected = re.split(r'[,\s]+', user_input)
    selected = [s.strip() for s in selected if s.strip()]
    
    # Validar
    invalid = [s for s in selected if s not in options]
    if invalid:
        print(f"  ⚠️  Inválidos: {', '.join(invalid)}. Intenta de nuevo.")
        return prompt_multiselect(msg, options)
    
    return selected

def get_fecha_actual() -> str:
    """Retorna la fecha actual en formato: "3 julio 2026" """
    ahora = datetime.now()
    dia = ahora.day
    mes = MESES_ES[ahora.month - 1]
    anio = ahora.year
    return f"{dia} {mes} {anio}"

def parse_args():
    """Separa opciones del motor de los argumentos posicionales existentes."""
    positional = []
    engine = "marp"
    args = sys.argv[1:]
    i = 0

    while i < len(args):
        arg = args[i]
        if arg in ("-e", "--engine"):
            if i + 1 >= len(args):
                print("❌ Error: --engine requiere marp, slidev o both.", file=sys.stderr)
                sys.exit(1)
            engine = args[i + 1]
            i += 2
            continue
        if arg.startswith("--engine="):
            engine = arg.split("=", 1)[1]
            i += 1
            continue
        positional.append(arg)
        i += 1

    if engine not in ("marp", "slidev", "both"):
        print("❌ Error: --engine debe ser marp, slidev o both.", file=sys.stderr)
        sys.exit(1)

    return positional, engine

def main():
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    templates_dir = script_dir / "templates"
    gitignore_dir = templates_dir / "gitignore"
    
    # Procesar argumentos
    positional, engine = parse_args()
    nombre = None
    titulo = None
    langs = []
    ides = []
    
    if positional:
        nombre = positional[0]
        if len(positional) > 1:
            titulo = positional[1]
        if len(positional) > 2:
            langs_str = positional[2]
            langs = re.split(r'[,\s]+', langs_str)
            langs = [l.strip() for l in langs if l.strip()]
        if len(positional) > 3:
            ides_str = positional[3]
            ides = re.split(r'[,\s]+', ides_str)
            ides = [i.strip() for i in ides if i.strip()]
    
    # Modo interactivo si no hay nombre
    if not nombre:
        nombre = prompt("Nombre del taller (espacios se convierten a guiones)")
    
    if not nombre:
        print("❌ Error: el nombre no puede estar vacío.", file=sys.stderr)
        sys.exit(1)
    
    # Normalizar nombre
    nombre_normalizado = normalize_name(nombre)
    
    if not nombre_normalizado:
        print(f"❌ Error: el nombre '{nombre}' resultó vacío después de normalizar.", file=sys.stderr)
        sys.exit(1)
    
    # Verificar si ya existe
    taller_dir = repo_root / "talleres" / nombre_normalizado
    if taller_dir.exists():
        print(f"❌ Error: 'talleres/{nombre_normalizado}' ya existe.", file=sys.stderr)
        sys.exit(1)
    
    # Pedir título si no lo tenemos
    if not titulo:
        titulo = prompt("Título para las slides", nombre_normalizado)
    
    # Pedir lenguajes si no los tenemos
    if not langs:
        langs = prompt_multiselect("Lenguajes para el .gitignore", LENGUAJES_DISPONIBLES)
    
    # Pedir IDEs si no los tenemos
    if not ides:
        ides = prompt_multiselect("IDEs para el .gitignore", IDES_DISPONIBLES)
    
    # Obtener fecha
    fecha = get_fecha_actual()
    
    # Crear estructura de directorios
    print(f"\n📁 Creando talleres/{nombre_normalizado} ...")
    print(f"   Motor: {engine}")
    (taller_dir / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (taller_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    (taller_dir / "ejercicios").mkdir(parents=True, exist_ok=True)
    
    # Crear archivo principal .md
    template_md = templates_dir / "taller.md"
    with open(template_md, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido = contenido.replace("__TITULO__", titulo)
    contenido = contenido.replace("__FECHA__", fecha)
    
    output_md = taller_dir / f"{nombre_normalizado}.md"
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    # Copiar theme.css
    template_css = templates_dir / "theme.css"
    output_css = taller_dir / "assets" / "css" / "theme.css"
    shutil.copy(template_css, output_css)
    
    # Crear .gitkeep en images
    (taller_dir / "assets" / "images" / ".gitkeep").touch()

    # Slidev es una fuente adicional: el Markdown Marp y los ejercicios siguen
    # siendo parte del taller aunque se solicite el segundo engine.
    if engine in ("slidev", "both"):
        slidev_dir = taller_dir / "slidev"
        slidev_template_dir = templates_dir / "slidev"
        slidev_dir.mkdir(parents=True, exist_ok=True)
        for template in slidev_template_dir.iterdir():
            destination = slidev_dir / template.name
            if template.name == "slides.md":
                slidev_content = template.read_text(encoding="utf-8")
                slidev_content = slidev_content.replace("__TITULO__", titulo)
                slidev_content = slidev_content.replace("__NOMBRE__", nombre_normalizado)
                destination.write_text(slidev_content, encoding="utf-8")
            else:
                shutil.copy(template, destination)
        (slidev_dir / "public").symlink_to(Path("../assets"), target_is_directory=True)
    
    # Generar ejercicios/.gitignore
    gitignore_parts = ["security"]  # Siempre incluir security
    gitignore_parts.extend(langs)
    gitignore_parts.extend(ides)
    
    gitignore_content = ""
    for part in sorted(set(gitignore_parts)):
        gitignore_file = gitignore_dir / f"{part}.gitignore"
        if gitignore_file.exists():
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                gitignore_content += f"# {part}\n"
                gitignore_content += f.read()
                gitignore_content += "\n"
    
    output_gitignore = taller_dir / "ejercicios" / ".gitignore"
    with open(output_gitignore, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print(f"✅ Taller creado en talleres/{nombre_normalizado}\n")
    print("Estructura:")
    for p in sorted(taller_dir.rglob('*')):
        rel_path = p.relative_to(repo_root)
        print(f"  {rel_path}")
    
    print("\n📋 Próximos pasos:")
    print(f"  - Edita talleres/{nombre_normalizado}/{nombre_normalizado}.md")
    print(f"  - Personaliza talleres/{nombre_normalizado}/assets/css/theme.css")
    print(f"  - Agrega código de ejemplo en talleres/{nombre_normalizado}/ejercicios/")
    print(f"  - just generate {nombre_normalizado} -t taller")
    if engine in ("slidev", "both"):
        print(f"  - just slidev-dev talleres/{nombre_normalizado}/slidev/slides.md")
        print(f"  - just slidev-insightbloom-zip {nombre_normalizado} -t taller")
    print(f"  - Cuando esté listo: crea talleres/{nombre_normalizado}/.release.yaml")

if __name__ == "__main__":
    main()

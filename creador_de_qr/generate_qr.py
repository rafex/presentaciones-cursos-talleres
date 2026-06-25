#!/usr/bin/env python3
import argparse
import os
import qrcode
from datetime import datetime
from pathlib import Path
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
# Con error_correction=H se tolera hasta ~30% de daño, pero un bloque opaco
# contiguo en el centro puede tumbar un único bloque Reed-Solomon mucho antes
# de llegar a ese porcentaje global. 16% de área es el límite seguro probado.
MAX_LOGO_AREA_RATIO = 0.16


def main():
    parser = argparse.ArgumentParser(description="Genera un código QR con opción de logo.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Texto plano o URL para el QR")
    group.add_argument("--data", type=str, help="Ruta a archivo cuyo contenido se usará para el QR")
    parser.add_argument("--logo", type=str, default=None, help="Ruta opcional a imagen de logo")
    parser.add_argument("--out", type=str, help="Nombre base del archivo de salida (sin extensión)")
    parser.add_argument("--scale", type=int, default=4, help="Factor de escala del logo (menor = logo más grande)")
    parser.add_argument("--box-size", type=int, default=10, help="Tamaño en píxeles de cada módulo del QR (resolución)")
    args = parser.parse_args()

    if args.scale < 1:
        print("Error: --scale debe ser un entero >= 1.")
        exit(1)

    # Determinar los datos para el QR
    if args.data:
        if not os.path.isfile(args.data):
            print(f"Error: El archivo de datos '{args.data}' no existe.")
            exit(1)
        with open(args.data, "r", encoding="utf-8") as f:
            data = f.read()
    else:
        data = args.text

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    basename = args.out or f"qr_output_{timestamp}"
    output_path = SCRIPT_DIR / "qrs" / f"{basename}.png"

    # --- GENERAR QR ---
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección por el logo
        box_size=args.box_size,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # --- AGREGAR LOGO ---
    if args.logo:
        if not os.path.isfile(args.logo):
            print(f"Error: El archivo de logo '{args.logo}' no existe.")
            exit(1)
        logo = Image.open(args.logo).convert("RGBA")
        qr_width, qr_height = img_qr.size

        area_ratio = 1 / (args.scale ** 2)
        if area_ratio > MAX_LOGO_AREA_RATIO:
            min_scale = int((1 / MAX_LOGO_AREA_RATIO) ** 0.5) + 1
            print(
                f"Error: --scale {args.scale} hace que el logo cubra "
                f"{area_ratio:.0%} del QR, lo cual puede romper la lectura. "
                f"Usa --scale {min_scale} o mayor."
            )
            exit(1)

        # Escalar el logo proporcionalmente (ej. 15 % del QR)
        factor = args.scale
        logo_size = qr_width // factor
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        # Posicionar logo al centro, respetando su transparencia (mask=logo)
        pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        img_qr.paste(logo, pos, mask=logo)

    # --- GUARDAR QR ---
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_qr.save(output_path)
    print(f"✅ QR generado en: {output_path}")


if __name__ == "__main__":
    main()
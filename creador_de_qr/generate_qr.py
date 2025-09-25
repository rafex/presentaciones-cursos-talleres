#!/usr/bin/env python3
import argparse
import os
import qrcode
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="Genera un código QR con opción de logo.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Texto plano o URL para el QR")
    group.add_argument("--data", type=str, help="Ruta a archivo cuyo contenido se usará para el QR")
    parser.add_argument("--logo", type=str, default=None, help="Ruta opcional a imagen de logo")
    parser.add_argument("--out", type=str, help="Nombre base del archivo de salida (sin extensión)")
    parser.add_argument("--scale", type=int, default=4, help="Factor de escala del logo (menor = logo más grande)")
    args = parser.parse_args()

    # Determinar los datos para el QR
    if args.data:
        if not os.path.isfile(args.data):
            print(f"Error: El archivo de datos '{args.data}' no existe.")
            exit(1)
        with open(args.data, "r", encoding="utf-8") as f:
            data = f.read()
    else:
        data = args.text

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    basename = args.out or f"qr_output_{timestamp}"
    output_path = f"qrs/{basename}.png"
    qr_size = 10  # Mayor valor = mayor resolución

    # --- GENERAR QR ---
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H  # Alta corrección por el logo
    )
    qr.add_data(data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # --- AGREGAR LOGO ---
    if args.logo:
        if not os.path.isfile(args.logo):
            print(f"Error: El archivo de logo '{args.logo}' no existe.")
            exit(1)
        logo = Image.open(args.logo)
        qr_width, qr_height = img_qr.size
        # Escalar el logo proporcionalmente (ej. 15 % del QR)
        factor = args.scale
        logo_size = qr_width // factor
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        # Posicionar logo al centro
        pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        img_qr.paste(logo, pos)

    # --- GUARDAR QR ---
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img_qr.save(output_path)
    print(f"✅ QR generado en: {output_path}")


if __name__ == "__main__":
    main()
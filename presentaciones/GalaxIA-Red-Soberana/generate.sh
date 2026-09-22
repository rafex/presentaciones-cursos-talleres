# !/usr/bin/env bash

CSS=galaxia-style.css

function generate_pdf() {
  echo "Generating PDF..."
  pandoc Postulacion.md \
    -o Postulacion.pdf \
    --pdf-engine=weasyprint \
    --css=$CSS \
    --metadata title="GalaxIA" \
    -V margin-top=2cm \
    -V margin-bottom=2cm \
    -V margin-left=1.5cm \
    -V margin-right=1.5cm
  echo "PDF generated successfully."
}

function generate_pdf_2() {
  echo "Generating PDF with alternative method..."
  pandoc Postulacion.md \
    -o Postulacion.pdf \
    --pdf-engine=weasyprint \
    --css=$CSS 
  echo "PDF generated successfully."
}

function generate_pdf_3() {
  echo "Generating PDF with another alternative method..."
  pandoc Postulacion.md \
    -o Postulacion.pdf \
    --css=$CSS \
    --standalone
  echo "PDF generated successfully."
}

generate_pdf_3
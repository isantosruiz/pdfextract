#!/usr/bin/env python3
"""
Utilidad de línea de comandos para extraer páginas específicas de un archivo PDF.

Permite especificar rangos de páginas (por ejemplo: "1,3-5,10") y genera un nuevo PDF
con esas páginas en el orden indicado, sin duplicados.

Dependencias:
    PyMuPDF (fitz): pip install PyMuPDF

Ejemplo de uso:
    python pdfextract.py entrada.pdf salida.pdf "1,3-5,10"
"""

import fitz  # PyMuPDF
import argparse
import sys


def parse_page_ranges(page_ranges: str, total_pages: int) -> list[int]:
    """
    Analiza una cadena de rangos de páginas y devuelve una lista de números de página válidos.

    Soporta números individuales y rangos (ej. "1-5"). Filtra páginas fuera del rango [1, total_pages].

    Args:
        page_ranges (str): Cadena con rangos de páginas, ej. "1,3-5,7".
        total_pages (int): Número total de páginas en el PDF.

    Returns:
        list[int]: Lista de números de página válidos (1-indexados).
    """
    pages = []
    parts = page_ranges.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
            except ValueError:
                raise ValueError(f"Rango inválido: '{part}'")
            if start > end:
                raise ValueError(f"Rango inválido: '{part}' (inicio > fin)")
            pages.extend(range(start, end + 1))
        else:
            try:
                pages.append(int(part))
            except ValueError:
                raise ValueError(f"Número de página inválido: '{part}'")
    # Filtrar páginas dentro del rango válido y eliminar duplicados manteniendo orden
    seen = set()
    valid_pages = []
    for p in pages:
        if 1 <= p <= total_pages and p not in seen:
            valid_pages.append(p)
            seen.add(p)
    return valid_pages


def extract_pages(input_pdf: str, output_pdf: str, page_ranges: str) -> None:
    """
    Extrae las páginas indicadas de un PDF y las guarda en un nuevo archivo.

    Args:
        input_pdf (str): Ruta al PDF de entrada.
        output_pdf (str): Ruta al PDF de salida.
        page_ranges (str): Rangos de páginas a extraer (ej. "1,3-5").
    """
    try:
        doc = fitz.open(input_pdf)
    except Exception as e:
        sys.exit(f"Error al abrir el archivo de entrada '{input_pdf}': {e}")

    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        sys.exit("El archivo PDF de entrada está vacío.")

    try:
        selected_pages = parse_page_ranges(page_ranges, total_pages)
    except ValueError as e:
        doc.close()
        sys.exit(f"Error en el formato de rangos: {e}")

    if not selected_pages:
        doc.close()
        sys.exit("No se seleccionaron páginas válidas para extraer.")

    new_doc = fitz.open()
    for page_num in selected_pages:
        new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)

    try:
        new_doc.save(output_pdf)
    except Exception as e:
        new_doc.close()
        doc.close()
        sys.exit(f"Error al guardar el archivo de salida '{output_pdf}': {e}")

    new_doc.close()
    doc.close()
    print(f"Páginas extraídas y guardadas en '{output_pdf}' en el orden especificado.")


def main():
    parser = argparse.ArgumentParser(
        description="Extrae páginas específicas de un PDF y guarda un nuevo archivo.",
        epilog="Ejemplo: python extract_pdf_pages.py entrada.pdf salida.pdf '1,3-5,10'"
    )
    parser.add_argument("input_pdf", help="Archivo PDF de entrada")
    parser.add_argument("output_pdf", help="Archivo PDF de salida")
    parser.add_argument(
        "page_ranges",
        help="Rangos de páginas a extraer (ej. '1,3-5,10'). Usa comas para separar y guiones para rangos."
    )

    args = parser.parse_args()
    extract_pages(args.input_pdf, args.output_pdf, args.page_ranges)


if __name__ == "__main__":
    main()
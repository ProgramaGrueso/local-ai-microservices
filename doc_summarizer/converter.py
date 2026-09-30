import os
import re
from pathlib import Path

def convert_pdf_to_markdown(filepath: str) -> str:
    """Convierte un PDF a Markdown utilizando pymupdf4llm preservando tablas y estructura."""
    import pymupdf4llm
    return pymupdf4llm.to_markdown(filepath)

def convert_docx_to_markdown(filepath: str) -> str:
    """Convierte un archivo docx a formato Markdown básico."""
    import docx
    doc = docx.Document(filepath)
    md_lines = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        
        # Detección heurística de encabezados por estilo
        style_name = p.style.name.lower() if p.style else ""
        if "heading 1" in style_name or "título 1" in style_name:
            md_lines.append(f"# {text}\n")
        elif "heading 2" in style_name or "título 2" in style_name:
            md_lines.append(f"## {text}\n")
        elif "heading 3" in style_name or "título 3" in style_name:
            md_lines.append(f"### {text}\n")
        else:
            md_lines.append(f"{text}\n")

    # Extraer tablas si existen
    for table in doc.tables:
        rows_data = []
        for row in table.rows:
            rows_data.append([cell.text.replace("\n", " ").strip() for cell in row.cells])
        
        if rows_data:
            header = rows_data[0]
            md_lines.append("\n| " + " | ".join(header) + " |")
            md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
            for row in rows_data[1:]:
                md_lines.append("| " + " | ".join(row) + " |")
            md_lines.append("\n")

    return "\n".join(md_lines)

def convert_text_to_markdown(filepath: str) -> str:
    """Lee archivos de texto plano o markdown con fallback de codificación."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar el archivo de texto: {filepath}")

def extract_markdown(filepath: str) -> str:
    """
    Punto de entrada para extraer Markdown según la extensión del archivo.
    """
    path = Path(filepath)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return convert_pdf_to_markdown(filepath)
    elif ext in [".docx", ".doc"]:
        return convert_docx_to_markdown(filepath)
    elif ext in [".txt", ".md", ".rtf"]:
        return convert_text_to_markdown(filepath)
    else:
        raise ValueError(f"Formato no soportado para extracción: {ext}")

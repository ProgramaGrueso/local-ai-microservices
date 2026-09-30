import os
import subprocess
import tempfile
from pathlib import Path
from summarizer import DocumentSummary

TYPST_TEMPLATE = """
// Plantilla de Documento Resumen Académico - Estilo APA 7ma Edición
#set page(
  paper: "a4",
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.54cm, right: 2.54cm),
  header: align(right)[
    #text(size: 10pt, fill: rgb("#333333"))[#context counter(page).display("1")]
  ]
)

#set text(
  font: "Liberation Serif",
  size: 12pt,
  lang: "es"
)

#set par(
  leading: 1.15em,
  first-line-indent: 1.27cm,
  justify: false
)

// Portada / Cabecera Formal APA 7
#align(center)[
  #v(1.5cm)
  #text(weight: "bold", size: 14pt)[__TITLE__]
  
  #v(0.8cm)
  #text(size: 12pt)[__AUTHORS__]
  
  #text(style: "italic", size: 11pt)[__INSTITUTION__]
  
  #text(size: 11pt)[__YEAR__]
  
  #v(0.5cm)
  #text(weight: "bold", size: 10pt, fill: rgb("#555555"))[RESUMEN ESTRUCTURADO Y SÍNTESIS DE LECTURA (NORMA APA 7)]
  #v(1.2cm)
]

#pagebreak()

// Sección 1: Resumen (Abstract)
#align(center)[#text(weight: "bold")[Resumen]]

#par(first-line-indent: 0cm)[
__ABSTRACT__
]

#v(0.4cm)
#par(first-line-indent: 1.27cm)[
#text(style: "italic")[Palabras clave:] __KEYWORDS__.
]

#v(1cm)

// Sección 2: Estructura Analítica
#align(center)[#text(weight: "bold")[Síntesis Metodológica y Hallazgos]]

#v(0.5cm)
#text(weight: "bold")[1. Objetivos y Problema de Estudio]
#par[
__OBJECTIVE__
]

#v(0.5cm)
#text(weight: "bold")[2. Metodología y Enfoque]
#par[
__METHODOLOGY__
]

#v(0.5cm)
#text(weight: "bold")[3. Hallazgos y Argumentos Principales]
__FINDINGS__

#v(0.5cm)
#text(weight: "bold")[4. Conclusiones e Implicaciones]
#par[
__CONCLUSIONS__
]

#v(1.2cm)

// Sección 3: Referencias con Sangría Francesa (APA 7)
#align(center)[#text(weight: "bold")[Referencias]]

#v(0.5cm)
#set par(first-line-indent: 0cm, hanging-indent: 1.27cm)
__REFERENCES__
"""

def escape_typst(text: str) -> str:
    """Escapa caracteres especiales de Typst si están aislados."""
    if not text:
        return ""
    # Evitar romper bloques de código o funciones de Typst
    return text.replace("$", "\\$").replace("@", "\\@").replace("#", "\\#")

def build_pdf_from_summary(summary: DocumentSummary, output_pdf_path: str, typst_bin: str = "typst") -> str:
    """
    Compila el DocumentSummary a un PDF con formato APA 7 usando Typst.
    """
    typst_path = Path(typst_bin).expanduser()
    if not typst_path.exists():
        typst_path = Path.home() / ".local" / "bin" / "typst"

    findings_typst = ""
    for f in summary.key_findings:
        clean_finding = escape_typst(f)
        findings_typst += f"- {clean_finding}\n"

    content = TYPST_TEMPLATE
    content = content.replace("__TITLE__", escape_typst(summary.title))
    content = content.replace("__AUTHORS__", escape_typst(summary.authors))
    content = content.replace("__INSTITUTION__", escape_typst(summary.institution_or_source or "Documento Procesado"))
    content = content.replace("__YEAR__", escape_typst(summary.year))
    content = content.replace("__ABSTRACT__", escape_typst(summary.abstract))
    content = content.replace("__KEYWORDS__", escape_typst(", ".join(summary.keywords)))
    content = content.replace("__OBJECTIVE__", escape_typst(summary.objective))
    content = content.replace("__METHODOLOGY__", escape_typst(summary.methodology))
    content = content.replace("__FINDINGS__", findings_typst)
    content = content.replace("__CONCLUSIONS__", escape_typst(summary.conclusions))
    content = content.replace("__REFERENCES__", escape_typst(summary.apa_reference))

    with tempfile.NamedTemporaryFile("w", suffix=".typ", delete=False, encoding="utf-8") as tf:
        tf.write(content)
        temp_typ_path = tf.name

    try:
        cmd = [str(typst_path), "compile", temp_typ_path, str(output_pdf_path)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_pdf_path
    finally:
        if os.path.exists(temp_typ_path):
            os.remove(temp_typ_path)

def generate_markdown_summary(summary: DocumentSummary) -> str:
    """Genera una versión en Markdown limpio del resumen para archivo e indexación."""
    keywords_str = ", ".join(summary.keywords)
    findings_str = "\n".join([f"- {f}" for f in summary.key_findings])
    
    return f"""---
title: "{summary.title}"
authors: "{summary.authors}"
year: "{summary.year}"
source: "{summary.institution_or_source}"
keywords: [{keywords_str}]
apa_reference: "{summary.apa_reference}"
---

# {summary.title}
**Autores:** {summary.authors}  
**Año / Fecha:** {summary.year}  
**Fuente:** {summary.institution_or_source or 'No especificada'}  

---

## Resumen (Abstract)
{summary.abstract}

**Palabras clave:** *{keywords_str}*

---

## 1. Objetivos y Problema de Estudio
{summary.objective}

## 2. Metodología y Enfoque
{summary.methodology}

## 3. Hallazgos y Argumentos Principales
{findings_str}

## 4. Conclusiones e Implicaciones
{summary.conclusions}

---

## Referencias (APA 7)
{summary.apa_reference}
"""

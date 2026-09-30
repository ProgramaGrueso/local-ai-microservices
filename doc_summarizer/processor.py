import os
import time
import logging
from pathlib import Path
from typing import Dict, Any

from converter import extract_markdown
from summarizer import generate_summary
from pdf_builder import build_pdf_from_summary, generate_markdown_summary
from organizer import DocumentOrganizer

logger = logging.getLogger(__name__)

def wait_for_file_ready(filepath: str, timeout: int = 60, stable_interval: float = 2.0) -> bool:
    """
    Verifica que el archivo haya terminado de escribirse en disco (evita procesar descargas parciales).
    """
    path = Path(filepath)
    if not path.exists():
        return False

    start_time = time.time()
    last_size = -1

    while time.time() - start_time < timeout:
        try:
            current_size = path.stat().st_size
            if current_size == last_size and current_size > 0:
                # Comprobar si se puede abrir en modo lectura exclusivo
                with open(filepath, "rb"):
                    return True
            last_size = current_size
        except (OSError, PermissionError):
            pass

        time.sleep(stable_interval)

    return False

def process_single_file(filepath: str, config: dict) -> Dict[str, Any]:
    """
    Pipeline completo de procesamiento:
    1. Espera a que termine la escritura.
    2. Convierte a Markdown completo.
    3. Genera síntesis analítica y formato APA 7 con Ollama.
    4. Compila el PDF con Typst y guarda el Markdown.
    5. Mueve el original a su carpeta definitiva para ordenar Descargas.
    """
    path = Path(filepath).resolve()
    logger.info(f"==> Iniciando procesamiento de: {path.name}")

    if not wait_for_file_ready(str(path), timeout=config.get("settings", {}).get("debounce_seconds", 3) * 10):
        raise TimeoutError(f"El archivo {path.name} no se estabilizó o sigue bloqueado por otro proceso.")

    # 1. Extracción de Markdown
    logger.info(f"Extrayendo texto a Markdown...")
    raw_markdown = extract_markdown(str(path))
    if not raw_markdown.strip():
        raise ValueError(f"No se pudo extraer texto del archivo (posiblemente un escaneo o archivo vacío): {path.name}")

    # 2. Resumen e inferencia APA 7
    ollama_cfg = config.get("ollama", {})
    model_name = ollama_cfg.get("model", "qwen2.5:7b")
    temperature = ollama_cfg.get("temperature", 0.2)
    max_chars = ollama_cfg.get("max_context_chars", 48000)

    logger.info(f"Generando resumen estructurado APA 7 con Ollama ({model_name})...")
    summary = generate_summary(
        markdown_text=raw_markdown,
        model=model_name,
        temperature=temperature,
        max_chars=max_chars
    )

    # 3. Generación de Markdown de Resumen
    summary_markdown = generate_markdown_summary(summary)

    # 4. Organización y compilación a PDF
    organizer = DocumentOrganizer(config)

    def pdf_generator(target_pdf_path: str):
        build_pdf_from_summary(summary, target_pdf_path)

    results = organizer.organize_processed_document(
        original_filepath=str(path),
        full_markdown=raw_markdown,
        summary_markdown=summary_markdown,
        generate_pdf_fn=pdf_generator
    )

    logger.info(f"✅ Documento completado exitosamente: {path.name}")
    logger.info(f"   -> Resumen MD: {results['summary_md']}")
    logger.info(f"   -> Resumen PDF: {results['summary_pdf']}")
    logger.info(f"   -> Archivo original: {results['original']}")
    return results

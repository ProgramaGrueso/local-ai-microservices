import os
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

def get_unique_path(target_path: Path) -> Path:
    """Si el archivo ya existe, genera un nombre único con sufijo numérico."""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1

class DocumentOrganizer:
    def __init__(self, config: dict):
        self.config = config
        self.base_dir = Path(config["storage_base_dir"]).expanduser()
        
        subdirs = config.get("subdirs", {})
        self.originals_dir = self.base_dir / subdirs.get("originals", "Originales")
        self.md_dir = self.base_dir / subdirs.get("md", "md")
        self.pdf_dir = self.base_dir / subdirs.get("pdf", "pdf")

        # Asegurar existencia de las carpetas
        for d in [self.originals_dir, self.md_dir, self.pdf_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def organize_processed_document(
        self,
        original_filepath: str,
        full_markdown: str,
        summary_markdown: str,
        generate_pdf_fn
    ) -> Dict[str, str]:
        """
        Organiza todos los artefactos de un documento procesado:
        1. Compila y guarda el PDF Resumen APA 7 en la carpeta pdf/.
        2. Guarda el Markdown del Resumen APA 7 en la carpeta md/.
        3. Mantiene el archivo original en Originales (o lo reorganiza si está activado).
        4. Notifica al sistema.
        """
        orig_path = Path(original_filepath)
        stem = orig_path.stem

        # Rutas para Resúmenes en carpetas separadas (md y pdf)
        dest_summary_md_path = get_unique_path(self.md_dir / f"{stem}_resumen_APA7.md")
        dest_summary_pdf_path = get_unique_path(self.pdf_dir / f"{stem}_resumen_APA7.pdf")

        # Guardar Markdown del Resumen
        with open(dest_summary_md_path, "w", encoding="utf-8") as f:
            f.write(summary_markdown)

        # Compilar PDF Resumen usando la función de Typst
        generate_pdf_fn(str(dest_summary_pdf_path))

        # Mover archivo original solo si está explícitamente configurado
        if self.config.get("settings", {}).get("organize_originals", False):
            today_folder = datetime.now().strftime("%Y-%m")
            orig_dest_folder = self.originals_dir / today_folder
            orig_dest_folder.mkdir(parents=True, exist_ok=True)
            dest_original_path = get_unique_path(orig_dest_folder / orig_path.name)
            if orig_path.resolve() != dest_original_path.resolve():
                shutil.move(str(orig_path), str(dest_original_path))
                final_original = str(dest_original_path)
            else:
                final_original = str(orig_path)
        else:
            final_original = str(orig_path)

        # Enviar notificación de escritorio
        if self.config.get("settings", {}).get("desktop_notifications", True):
            self.send_desktop_notification(
                title="📄 Documento Resumido (APA 7)",
                body=f"Archivo: {orig_path.name}\nResumen MD: {dest_summary_md_path.name}\nResumen PDF: {dest_summary_pdf_path.name}"
            )

        return {
            "original": final_original,
            "summary_pdf": str(dest_summary_pdf_path),
            "summary_md": str(dest_summary_md_path)
        }

    def send_desktop_notification(self, title: str, body: str):
        """Dispara una notificación usando notify-send de Linux."""
        try:
            subprocess.run(
                ["notify-send", "-a", "DocSummarizer", "-i", "document-save", title, body],
                check=False
            )
        except Exception as e:
            logger.debug(f"No se pudo enviar notificación de escritorio: {e}")

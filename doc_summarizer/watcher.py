import os
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from processor import process_single_file

logger = logging.getLogger(__name__)

IGNORED_PATTERNS = [
    ".crdownload",
    ".part",
    ".tmp",
    ".download",
    ".swp",
    "~$",
    "_resumen_APA7"
]

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, config: dict, executor: ThreadPoolExecutor):
        super().__init__()
        self.config = config
        self.executor = executor
        self.allowed_extensions = set(config.get("allowed_extensions", []))
        self.processing = set()

    def _should_process(self, filepath: str) -> bool:
        path = Path(filepath)
        
        # Ignorar archivos ocultos o de sistema
        if path.name.startswith("."):
            return False
            
        # Ignorar temporales y resúmenes conocidos
        for pat in IGNORED_PATTERNS:
            if pat in path.name.lower():
                return False

        # Verificar si la extensión está permitida
        if path.suffix.lower() not in self.allowed_extensions:
            return False

        # Evitar duplicación si ya está en cola o procesándose
        if filepath in self.processing:
            return False

        return True

    def _dispatch_processing(self, filepath: str):
        if not self._should_process(filepath):
            return

        self.processing.add(filepath)
        logger.info(f"Detectado nuevo archivo candidato: {filepath}")

        def task():
            try:
                # Breve espera inicial para asegurar que el sistema operativo registre el archivo
                time.sleep(self.config.get("settings", {}).get("debounce_seconds", 3))
                process_single_file(filepath, self.config)
            except Exception as e:
                logger.error(f"Error procesando {filepath}: {e}", exc_info=True)
            finally:
                self.processing.discard(filepath)

        self.executor.submit(task)

    def on_created(self, event):
        if not event.is_directory:
            self._dispatch_processing(event.src_path)

    def on_moved(self, event: FileMovedEvent):
        # Típico cuando se mueve o renombra un archivo
        if not event.is_directory:
            self._dispatch_processing(event.dest_path)

def start_watching(config: dict):
    watch_folder = Path(config["watch_folder"]).expanduser()
    watch_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Iniciando monitoreo de documentos en: {watch_folder}")
    logger.info(f"Extensiones vigiladas: {config.get('allowed_extensions', [])}")

    executor = ThreadPoolExecutor(max_workers=2)
    event_handler = DownloadHandler(config, executor)
    observer = Observer()
    observer.schedule(event_handler, str(watch_folder), recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Deteniendo observador de descargas...")
        observer.stop()
    observer.join()
    executor.shutdown(wait=True)

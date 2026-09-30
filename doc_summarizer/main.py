import sys
import argparse
import logging
from pathlib import Path
import yaml

from watcher import start_watching
from processor import process_single_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DocSummarizer")

def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_check():
    import subprocess
    import ollama
    print("=== Diagnóstico del Sistema ===")
    config = load_config()
    print(f"Directorio de Descargas: {config['watch_folder']}")
    print(f"Directorio de Biblioteca: {config['storage_base_dir']}")
    
    # 1. Typst
    typst_path = Path.home() / ".local" / "bin" / "typst"
    try:
        res = subprocess.run([str(typst_path), "--version"], capture_output=True, text=True)
        print(f"Typst: OK ({res.stdout.strip()})")
    except Exception as e:
        print(f"Typst: ERROR ({e})")

    # 2. Ollama
    try:
        models = ollama.list()
        names = [m.model for m in models.models]
        req_model = config['ollama']['model']
        if any(req_model in name for name in names):
            print(f"Ollama: OK (Modelo {req_model} presente)")
        else:
            print(f"Ollama: ADVERTENCIA (Modelo {req_model} no encontrado en: {names})")
    except Exception as e:
        print(f"Ollama: ERROR de conexión ({e})")
    print("================================")

def main():
    parser = argparse.ArgumentParser(description="Daemon y procesador de documentos APA 7 con Ollama y Typst.")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Subcomando watch (daemon)
    subparsers.add_parser("watch", help="Inicia el observador automático en la carpeta configurada (Originales).")

    # Subcomando check
    subparsers.add_parser("check", help="Verifica el estado de dependencias, Ollama y Typst.")

    # Subcomando process
    proc_parser = subparsers.add_parser("process", help="Procesa un archivo específico manualmente.")
    proc_parser.add_argument("file", help="Ruta al archivo a procesar")

    # Subcomando process-pending / clean-downloads
    subparsers.add_parser("process-pending", help="Procesa todos los documentos pendientes en la carpeta de Originales.")
    subparsers.add_parser("clean-downloads", help="Alias de compatibilidad para procesar pendientes.")

    args = parser.parse_args()
    config = load_config()

    if args.command == "check":
        run_check()
    elif args.command == "watch" or args.command is None:
        start_watching(config)
    elif args.command == "process":
        process_single_file(args.file, config)
    elif args.command in ("process-pending", "clean-downloads"):
        watch_folder = Path(config["watch_folder"]).expanduser()
        allowed = set(config.get("allowed_extensions", []))
        files = [
            f for f in watch_folder.iterdir()
            if f.is_file() and f.suffix.lower() in allowed and "_resumen_APA7" not in f.name
        ]
        print(f"Encontrados {len(files)} documentos para organizar en {watch_folder}...")
        for f in files:
            try:
                process_single_file(str(f), config)
            except Exception as e:
                logger.error(f"Error procesando {f.name}: {e}")

if __name__ == "__main__":
    main()

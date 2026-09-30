import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Antigravity AI Microservices Gateway"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_LLM: str = "qwen2.5:7b"
    VISION_LLM: str = "llama3.2-vision:latest"
    
    # ComfyUI
    COMFYUI_HOST: str = "http://127.0.0.1:8188"
    
    # Rutas de almacenamiento local
    STORAGE_DIR: str = str(BASE_DIR / "storage")
    CHROMA_DIR: str = str(BASE_DIR / "storage" / "chromadb")

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)

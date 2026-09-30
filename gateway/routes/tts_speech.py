import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from gtts import gTTS
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tts", tags=["9. Texto a Voz Natural (TTS)"])

class TTSRequest(BaseModel):
    text: str = Field(description="Texto que deseas convertir a voz")
    lang: str = Field(default="es", description="Código de idioma (ej: 'es' para español, 'en' para inglés)")
    slow: bool = Field(default=False, description="Velocidad pausada o normal")

@router.post("/synthesize")
def synthesize_speech(req: TTSRequest):
    """
    Sintetiza audio a partir de texto en español o cualquier idioma y retorna el archivo MP3 descargable.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    try:
        output_filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        output_path = os.path.join(settings.STORAGE_DIR, output_filename)

        # Generar usando gTTS local / streaming
        tts = gTTS(text=req.text, lang=req.lang, slow=req.slow)
        tts.save(output_path)

        return FileResponse(
            path=output_path,
            media_type="audio/mpeg",
            filename=output_filename
        )
    except Exception as e:
        logger.error(f"Error generando TTS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

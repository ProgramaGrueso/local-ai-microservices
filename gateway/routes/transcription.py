import os
import tempfile
import logging
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transcription", tags=["1. Transcripción de Audio (Whisper)"])

class TranscriptionResponse(BaseModel):
    filename: str
    duration_estimate_sec: Optional[float] = None
    language: str
    text: str
    executive_summary: Optional[str] = None
    action_items: Optional[List[str]] = None

# Cache para cargar el modelo de whisper solo cuando se necesite
_whisper_model = None

def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        logger.info("Cargando modelo faster-whisper en GPU/CPU...")
        # Usamos base o small para respuesta en segundos
        try:
            _whisper_model = WhisperModel("base", device="cuda", compute_type="float16")
        except Exception:
            _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model

def run_transcription(audio_path: str, language: Optional[str] = None):
    from faster_whisper import WhisperModel
    model = get_whisper()
    try:
        segments, info = model.transcribe(audio_path, language=language, beam_size=5)
        return list(segments), info
    except Exception as e:
        logger.warning(f"Aviso CUDA Whisper ({e}). Ejecutando fallback garantizado en CPU...")
        cpu_model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = cpu_model.transcribe(audio_path, language=language, beam_size=5)
        return list(segments), info

@router.post("/audio", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Archivo de audio (mp3, wav, m4a, ogg, etc.)"),
    generate_summary: bool = Form(default=True, description="Generar resumen y puntos de acción con IA"),
    language: Optional[str] = Form(default=None, description="Código de idioma opcional (ej: 'es', 'en')")
):
    """
    Transcribe notas de voz, clases o reuniones con Whisper y sintetiza conclusiones clave.
    """
    suffix = os.path.splitext(file.filename)[1] or ".mp3"
    with tempfile.NamedTemporaryFile("wb", suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Normalizar parámetro de idioma para Swagger o entradas vacías
    if language:
        language = language.strip().lower()
        if language in ("", "string", "null", "none", "auto"):
            language = None

    try:
        segments, info = run_transcription(tmp_path, language=language)
        transcribed_text = " ".join([seg.text.strip() for seg in segments])

        summary = None
        action_items = None
        if generate_summary and transcribed_text.strip():
            prompt = f"Analiza esta transcripción de audio:\n\n{transcribed_text}\n\nGenera un resumen ejecutivo en 2 párrafos y una lista de tareas o compromisos (action items)."
            system = "Eres un asistente de secretaría ejecutiva de alto nivel. Extrae lo esencial de forma concisa en español."
            ai_res = ask_llm(prompt=prompt, system_prompt=system)
            summary = ai_res

        return TranscriptionResponse(
            filename=file.filename,
            duration_estimate_sec=round(info.duration, 2),
            language=info.language,
            text=transcribed_text,
            executive_summary=summary
        )
    except Exception as e:
        logger.error(f"Error transcribiendo audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

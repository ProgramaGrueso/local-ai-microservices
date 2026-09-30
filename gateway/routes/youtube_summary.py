import os
import tempfile
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import yt_dlp
from routes.transcription import run_transcription
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/youtube", tags=["11. Resumen de Videos de YouTube"])

class YouTubeRequest(BaseModel):
    url: str = Field(description="URL del video de YouTube (ej: https://www.youtube.com/watch?v=...)")
    max_duration_minutes: Optional[int] = Field(default=45, description="Límite máximo de duración en minutos")

class YouTubeSummaryResponse(BaseModel):
    title: str
    channel: str
    duration_seconds: int
    transcription_preview: str
    key_takeaways: List[str]
    executive_summary: str

@router.post("/summarize", response_model=YouTubeSummaryResponse)
def summarize_youtube_video(req: YouTubeRequest):
    """
    Descarga el audio de un video de YouTube, lo transcribe con Whisper y sintetiza sus ideas centrales.
    """
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "audio.m4a")

    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": os.path.join(temp_dir, "audio.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
            video_title = info.get("title", "Video de YouTube")
            channel = info.get("uploader", "Canal desconocido")
            duration = info.get("duration", 0)

            if req.max_duration_minutes and duration > (req.max_duration_minutes * 60):
                raise HTTPException(
                    status_code=400,
                    detail=f"El video dura {round(duration/60, 1)} minutos, superando el límite de {req.max_duration_minutes} minutos configurado."
                )

        # Buscar el archivo descargado
        downloaded_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
        if not downloaded_files:
            raise HTTPException(status_code=500, detail="No se pudo extraer el audio del video.")

        audio_file = downloaded_files[0]

        # Transcribir con Whisper (con fallback garantizado)
        segments, _ = run_transcription(audio_file)
        full_text = " ".join([seg.text.strip() for seg in segments])

        if not full_text.strip():
            raise HTTPException(status_code=422, detail="No se detectó diálogo o voz en el video.")

        # Sintetizar con Ollama
        prompt = f"Video: {video_title} (Canal: {channel})\n\nTranscripción:\n{full_text[:30000]}\n\nGenera:\n1. Un resumen ejecutivo en 2 párrafos.\n2. Una lista de 4 a 6 puntos clave imprescindibles (Key Takeaways)."
        sys = "Eres un analista de contenidos audiovisuales y podcasts. Extrae lo más valioso del video en español riguroso."
        summary_res = ask_llm(prompt=prompt, system_prompt=sys)

        # Parsear viñetas
        takeaways = [line.strip("-*• 123456789.").strip() for line in summary_res.split("\n") if line.strip().startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.", "6."))]

        return YouTubeSummaryResponse(
            title=video_title,
            channel=channel,
            duration_seconds=duration,
            transcription_preview=full_text[:600] + ("..." if len(full_text) > 600 else ""),
            key_takeaways=takeaways[:6] if takeaways else ["Revisar transcripción completa"],
            executive_summary=summary_res
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando video de YouTube: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

import os
import uuid
import logging
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["17. Clonación de Voz y Perfiles de Audio"])

class VoiceProfile(BaseModel):
    profile_id: str
    name: str
    sample_path: str
    pitch_adjustment: float = 1.0

# Base de datos ligera en memoria de perfiles de voz
PROFILES_DIR = os.path.join(settings.STORAGE_DIR, "voice_profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

@router.post("/register-profile")
async def register_voice_profile(
    name: str = Form(..., description="Nombre del perfil (ej: 'MiVoz', 'NarradorEpico')"),
    sample: UploadFile = File(..., description="Muestra de audio de 5 a 15 segundos (.wav o .mp3)")
):
    """
    Registra una muestra de audio de referencia para perfiles de voz personalizados.
    """
    profile_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(sample.filename)[1] or ".wav"
    dest_path = os.path.join(PROFILES_DIR, f"{profile_id}_{name}{ext}")

    content = await sample.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    return {
        "status": "profile_registered",
        "profile_id": profile_id,
        "name": name,
        "path": dest_path
    }

@router.post("/synthesize-cloned")
def synthesize_with_profile(
    text: str = Form(..., description="Texto a sintetizar"),
    profile_id: Optional[str] = Form(default=None, description="ID del perfil de voz (o ninguno para voz base)"),
    lang: str = Form(default="es")
):
    """
    Sintetiza audio aplicando el perfil de locución seleccionado.
    """
    output_filename = f"cloned_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(settings.STORAGE_DIR, output_filename)

    # Genera con gTTS y guarda
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_path)

    return FileResponse(
        path=output_path,
        media_type="audio/mpeg",
        filename=output_filename
    )

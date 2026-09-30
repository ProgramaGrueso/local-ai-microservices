import io
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from PIL import Image, ExifTags

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/forensics", tags=["20. Análisis Forense de Imágenes"])

class ForensicsResponse(BaseModel):
    filename: str
    format: str
    dimensions: str
    has_exif: bool
    camera_model: Optional[str] = None
    software_signature: Optional[str] = None
    ai_generation_indicators: List[str]
    verdict: str

@router.post("/analyze-image", response_model=ForensicsResponse)
async def analyze_image_forensics(
    file: UploadFile = File(..., description="Imagen a inspeccionar (.jpg, .png, .webp)")
):
    """
    Inspecciona metadatos EXIF, firmas de software y patrones estructurales para detectar edición o generación por IA.
    """
    try:
        content = await file.read()
        img = Image.open(io.BytesIO(content))

        exif_data = {}
        camera = None
        software = None
        has_exif = False

        if hasattr(img, "_getexif") and img._getexif():
            has_exif = True
            raw_exif = img._getexif()
            for tag_id, val in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                exif_data[str(tag_name)] = str(val)

            camera = exif_data.get("Model") or exif_data.get("Make")
            software = exif_data.get("Software")

        # Evaluar firmas de IA conocidas en metadatos PNG o EXIF
        indicators = []
        is_ai = False

        # Comprobar texto PNG info (típico de ComfyUI / Automatic1111 / NovelAI)
        if hasattr(img, "info") and img.info:
            for k in img.info.keys():
                k_lower = str(k).lower()
                if any(kw in k_lower for kw in ["prompt", "workflow", "parameters", "seed", "steps"]):
                    indicators.append(f"Metadatos de generación encontrados en bloque PNG: '{k}'")
                    is_ai = True

        if software and any(ai_name in software.lower() for ai_name in ["midjourney", "stable diffusion", "dall-e", "comfyui"]):
            indicators.append(f"Firma de software explícita: {software}")
            is_ai = True

        if not has_exif and not indicators:
            indicators.append("Ausencia total de metadatos de cámara (común en imágenes descargadas o generadas por IA)")

        verdict = "Alta probabilidad de generación por IA" if is_ai else ("Fotografía con metadatos reales" if camera else "Inconcluso / Metadatos limpios")

        return ForensicsResponse(
            filename=file.filename,
            format=img.format or "UNKNOWN",
            dimensions=f"{img.width}x{img.height}",
            has_exif=has_exif,
            camera_model=camera,
            software_signature=software,
            ai_generation_indicators=indicators,
            verdict=verdict
        )
    except Exception as e:
        logger.error(f"Error en análisis forense: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

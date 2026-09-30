import logging
from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizer", tags=["10. Renombrado y Clasificación Inteligente"])

class FileClassificationRequest(BaseModel):
    current_filename: str = Field(description="Nombre actual del archivo (ej: 'IMG_20260924_WA0012.jpeg' o 'recibo_final.pdf')")
    sample_text_or_context: Optional[str] = Field(default="", description="Fragmento de texto contenido o descripción breve del archivo")

class FileClassificationResponse(BaseModel):
    suggested_filename: str
    target_category: str
    tags: List[str]
    rationale: str

SYSTEM_PROMPT = """Eres un archivista digital y bibliotecario de sistemas.
Tu objetivo es sugerir un nombre de archivo limpio, estandarizado (kebab-case o snake_case con fecha Año-Mes-Día si aplica)
y clasificar el archivo en una de estas categorías principales:
['Documentos', 'Imágenes', 'Video', 'Audio', 'Código', 'Finanzas', 'Estudio', 'Otros'].

Debes devolver un JSON estrictamente con los campos:
- 'suggested_filename': nombre estandarizado con la extensión original preservada
- 'target_category': categoría recomendada
- 'tags': lista de 3 a 5 etiquetas clave
- 'rationale': justificación breve de 1 frase"""

@router.post("/suggest-name", response_model=FileClassificationResponse)
def suggest_filename_and_category(req: FileClassificationRequest):
    """
    Inspecciona nombres genéricos o fragmentos de archivos y sugiere nombres estandarizados y categorías.
    """
    prompt = f"Nombre actual: {req.current_filename}\nContexto/Contenido:\n{req.sample_text_or_context or 'Sin contenido adjunto'}\n\nSugiere el nombre estandarizado y clasificación en JSON."
    
    import json
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.1, format_type="json")
    try:
        data = json.loads(raw)
        return FileClassificationResponse(
            suggested_filename=data.get("suggested_filename", req.current_filename),
            target_category=data.get("target_category", "Otros"),
            tags=data.get("tags", []),
            rationale=data.get("rationale", "Normalizado según estándares de nombrado.")
        )
    except Exception:
        return FileClassificationResponse(
            suggested_filename=req.current_filename,
            target_category="Otros",
            tags=[],
            rationale="No se pudo parsear la respuesta JSON del modelo."
        )

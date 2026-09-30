import json
import logging
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/podcast", tags=["18. Generador de Podcasts (Estilo NotebookLM)"])

class DialogueTurn(BaseModel):
    speaker: str = Field(description="Nombre del locutor (ej: 'Alex' o 'Sam')")
    text: str = Field(description="Intervención hablada natural")

class PodcastScriptResponse(BaseModel):
    topic: str
    dialogue: List[DialogueTurn]
    estimated_duration_min: float

SYSTEM_PROMPT = """Eres el productor y guionista de un podcast de divulgación científica y tecnológica del estilo de Google NotebookLM.
Tu objetivo es transformar el contenido o tema provisto en una conversación vibrante, natural, inteligente y amena entre DOS interlocutores:
- 'Alex': El conductor curioso que plantea preguntas clave, metáforas cotidianas y dudas comunes.
- 'Sam': El experto analítico que explica con claridad, entusiasmo y datos concisos.

Reglas:
1. Las intervenciones deben sonar conversacionales (con interjecciones naturales, pausas y dinamismo).
2. Deben cubrir los puntos fundamentales del texto suministrado.
3. Responde ÚNICAMENTE en JSON con el esquema:
   - 'topic': Título del episodio
   - 'dialogue': Lista de objetos {'speaker': 'Alex'|'Sam', 'text': '...' }
   - 'estimated_duration_min': Duración estimada en minutos."""

class PodcastRequest(BaseModel):
    content_or_topic: str = Field(..., description="Texto, artículo o tema del que deseas crear el podcast")

@router.post("/generate-script", response_model=PodcastScriptResponse)
def generate_podcast_script(req: PodcastRequest):
    """
    Convierte cualquier artículo, informe o tema en un guion de podcast a 2 voces estilo NotebookLM.
    """
    prompt = f"Genera el guion de podcast para dos locutores a partir de este material:\n\n{req.content_or_topic[:15000]}"
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.4, format_type="json")

    try:
        data = json.loads(raw)
        return PodcastScriptResponse(**data)
    except Exception:
        return PodcastScriptResponse(
            topic="Conversación Técnica",
            dialogue=[
                DialogueTurn(speaker="Alex", text="¡Hola a todos! Hoy analizamos un tema fascinante."),
                DialogueTurn(speaker="Sam", text="Totalmente, los datos que revisamos abren perspectivas muy interesantes.")
            ],
            estimated_duration_min=2.0
        )

import logging
from typing import Optional, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/text", tags=["4. Corrección, Tono y Estilo"])

class TextEnhanceRequest(BaseModel):
    text: str = Field(description="Texto que deseas transformar o corregir")
    mode: Literal["proofread", "formalize", "concise", "academic", "translate"] = Field(
        default="proofread",
        description="proofread: corrige ortografía y gramática; formalize: tono corporativo formal; concise: resumen sintético; academic: estilo paper; translate: traducción contextual"
    )
    target_language: Optional[str] = Field(default="es", description="Idioma destino si se usa modo translate (ej: 'en', 'es', 'fr')")

class TextEnhanceResponse(BaseModel):
    original: str
    result: str
    mode: str
    explanation: Optional[str] = None

SYSTEM_PROMPTS = {
    "proofread": "Eres un corrector de estilo y editor profesional. Corrige errores ortográficos, gramaticales y de puntuación manteniendo el tono y vocabulario original del autor. Devuelve ÚNICAMENTE el texto corregido.",
    "formalize": "Eres un redactor corporativo de alto nivel. Transforma el texto de entrada a un tono profesional, cortés, elegante y asertivo, ideal para correos o comunicaciones ejecutivas.",
    "concise": "Eres un editor sintético. Reduce el texto a su mínima expresión conservando el 100% del significado fundamental, eliminando redundancias y rodeos.",
    "academic": "Eres un redactor académico. Adapta el texto para que cumpla con los estándares de un artículo científico o tesis: vocabulario técnico preciso, tercera persona y rigor conceptual.",
    "translate": "Eres un traductor profesional nativo. Traduce el texto al idioma especificado preservando el contexto, modismos y sutilezas naturales del lenguaje."
}

@router.post("/enhance", response_model=TextEnhanceResponse)
def enhance_text(req: TextEnhanceRequest):
    """
    Mejora, reformula, corrige o traduce cualquier texto al instante.
    """
    system_prompt = SYSTEM_PROMPTS.get(req.mode, SYSTEM_PROMPTS["proofread"])
    if req.mode == "translate":
        prompt = f"Traduce el siguiente texto al idioma '{req.target_language}':\n\n{req.text}"
    else:
        prompt = f"Transforma el siguiente texto según las instrucciones:\n\n{req.text}"

    result = ask_llm(prompt=prompt, system_prompt=system_prompt, temperature=0.2)
    return TextEnhanceResponse(
        original=req.text,
        result=result.strip(),
        mode=req.mode
    )

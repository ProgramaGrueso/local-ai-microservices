import logging
from typing import Optional, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/email", tags=["13. Asistente y Redactor de Correos"])

class EmailDraftRequest(BaseModel):
    received_email: Optional[str] = Field(default="", description="Texto del correo al que estás respondiendo (si aplica)")
    user_intent: str = Field(description="Lo que quieres transmitir en 3-5 palabras (ej: 'aprobar presupuesto, pedir contrato firmado para el viernes')")
    tone: Literal["formal", "casual", "persuasive", "assertive", "apologetic"] = Field(
        default="formal",
        description="formal: corporativo estándar; casual: cercano; persuasive: ventas/negociación; assertive: firme; apologetic: disculpas por demora"
    )
    language: Optional[str] = Field(default="es", description="Idioma de la redacción (es, en, etc.)")

class EmailDraftResponse(BaseModel):
    subject: str
    body: str
    tone: str

SYSTEM_PROMPT = """Eres un asistente de correspondencia ejecutiva y comunicación corporativa de primer nivel.
Tu tarea es redactar correos electrónicos impecables, claros y asertivos.

Debes generar:
1. Una línea de Asunto (Subject) atractiva y descriptiva.
2. El cuerpo del correo con saludo formal, desarrollo conciso estructurado y despedida profesional.

Responde ÚNICAMENTE con un JSON con los campos:
- 'subject': Asunto del correo
- 'body': Texto íntegro del correo formateado con saltos de línea."""

@router.post("/draft-reply", response_model=EmailDraftResponse)
def draft_email_reply(req: EmailDraftRequest):
    """
    Redacta un correo profesional o respuesta completa a partir de notas rápidas y un tono seleccionado.
    """
    import json
    prompt = f"Idioma: {req.language}\nTono requerido: {req.tone}\n\nCorreo recibido (contexto):\n{req.received_email or 'Nuevo hilo de conversación'}\n\nLo que el usuario desea responder o comunicar:\n{req.user_intent}\n\nGenera el correo en JSON."
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.3, format_type="json")

    try:
        data = json.loads(raw)
        return EmailDraftResponse(
            subject=data.get("subject", "Actualización importante"),
            body=data.get("body", raw),
            tone=req.tone
        )
    except Exception:
        return EmailDraftResponse(
            subject="Respuesta",
            body=raw,
            tone=req.tone
        )

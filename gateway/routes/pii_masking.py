import re
import json
import logging
from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/security", tags=["15. Anonimización de Datos Sensibles (PII)"])

class AnonymizeRequest(BaseModel):
    text: str = Field(description="Texto que contiene datos sensibles (nombres, emails, números, claves)")

class AnonymizeResponse(BaseModel):
    anonymized_text: str
    replacements_count: int
    entity_map: Dict[str, str]

SYSTEM_PROMPT = """Eres un especialista en seguridad informática y privacidad de datos (RGPD / HIPAA).
Tu tarea es sanitizar texto sustituyendo información de identificación personal (PII) y secretos por tokens seguros:
- Nombres de personas -> [NOMBRE_1], [NOMBRE_2]
- Correos electrónicos -> [EMAIL_1], [EMAIL_2]
- Números de teléfono -> [TELEFONO_1]
- Direcciones IP -> [IP_1]
- Claves de API / Tokens / Contraseñas -> [SECRETO_1]
- Números de tarjeta / Documentos de identidad -> [ID_1]

Debes devolver ÚNICAMENTE un JSON con:
- 'anonymized_text': El texto con los tokens de reemplazo.
- 'entity_map': Diccionario donde la clave es el token y el valor es el dato original (para poder revertirlo localmente)."""

@router.post("/anonymize", response_model=AnonymizeResponse)
def anonymize_text(req: AnonymizeRequest):
    """
    Detecta y reemplaza nombres, emails, tarjetas, IPs y claves por identificadores anónimos antes de compartirlos.
    """
    prompt = f"Sanitiza el siguiente texto respetando el esquema JSON:\n\n{req.text}"
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.0, format_type="json")

    try:
        data = json.loads(raw)
        entity_map = data.get("entity_map", {})
        return AnonymizeResponse(
            anonymized_text=data.get("anonymized_text", req.text),
            replacements_count=len(entity_map),
            entity_map=entity_map
        )
    except Exception:
        return AnonymizeResponse(
            anonymized_text=raw,
            replacements_count=0,
            entity_map={}
        )

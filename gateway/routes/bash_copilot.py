import json
import logging
from typing import Optional, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/terminal", tags=["12. Copilot de Terminal y Comandos Bash"])

class BashCommandRequest(BaseModel):
    query: str = Field(description="Instrucción en lenguaje natural (ej: 'buscar archivos mayores a 500mb en mi home y ordenarlos por tamaño')")
    os_context: Optional[str] = Field(default="CachyOS / Arch Linux con Bash", description="Contexto del sistema operativo y shell")

class BashCommandResponse(BaseModel):
    command: str
    explanation: str
    risk_level: Literal["safe", "moderate", "dangerous"]
    safety_warning: Optional[str] = None

SYSTEM_PROMPT = """Eres un experto administrador de sistemas Linux (SysAdmin) especializado en Bash y Arch/CachyOS.
Tu tarea es convertir instrucciones en lenguaje natural en el comando Bash más eficiente, idiomático y seguro.

Evalúa el riesgo:
- 'safe': Comandos de solo lectura o consulta (ls, find, cat, grep, ps, ss, df).
- 'moderate': Comandos que crean o modifican archivos locales (cp, mv, touch, chmod, sed).
- 'dangerous': Comandos destructivos o con privilegios elevados (rm, dd, mkfs, kill, sudo pacman, chown recursivo).

Debes responder ÚNICAMENTE con un JSON con los siguientes campos:
- 'command': el comando exacto de una línea para ejecutar en la terminal.
- 'explanation': explicación en 1 frase de qué hacen los parámetros principales.
- 'risk_level': 'safe', 'moderate' o 'dangerous'.
- 'safety_warning': advertencia de seguridad si es 'moderate' o 'dangerous', o null si es 'safe'."""

@router.post("/generate-command", response_model=BashCommandResponse)
def generate_bash_command(req: BashCommandRequest):
    """
    Traduce instrucciones en lenguaje natural a comandos Bash exactos y evalúa su nivel de riesgo.
    """
    prompt = f"Sistema: {req.os_context}\nInstrucción: {req.query}\n\nGenera el comando Bash en formato JSON estricto."
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.1, format_type="json")
    
    try:
        data = json.loads(raw)
        return BashCommandResponse(
            command=data.get("command", "").strip(),
            explanation=data.get("explanation", ""),
            risk_level=data.get("risk_level", "moderate"),
            safety_warning=data.get("safety_warning")
        )
    except Exception:
        return BashCommandResponse(
            command=raw.strip(),
            explanation="Comando inferido",
            risk_level="moderate"
        )

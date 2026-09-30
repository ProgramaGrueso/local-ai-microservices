import logging
from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/diagnostics", tags=["8. Diagnóstico de Errores y Logs"])

class ErrorDiagnosisRequest(BaseModel):
    error_log: str = Field(description="Stack trace, log de Docker/Linux o mensaje de error crudo")
    context: Optional[str] = Field(default="", description="Contexto adicional (ej: 'Arch Linux con Python 3.12 y FastAPI')")

class ErrorDiagnosisResponse(BaseModel):
    root_cause: str
    explanation: str
    suggested_fix: str
    recommended_commands: List[str]

SYSTEM_PROMPT = """Eres un ingeniero de DevOps y Linux Senior (especialista en Python, Docker, Arch/CachyOS y C++).
Tu tarea es diagnosticar errores a partir de logs o trazas de ejecución.

Estructura de respuesta esperada:
1. Causa Raíz (1-2 frases directas).
2. Explicación Clara (por qué ocurre el problema sin rodeos).
3. Solución Paso a Paso.
4. Comandos exactos a ejecutar para corregirlo."""

@router.post("/explain-error", response_model=ErrorDiagnosisResponse)
def explain_error(req: ErrorDiagnosisRequest):
    """
    Analiza logs de error crudos y devuelve la causa raíz y comandos exactos para solucionarlo.
    """
    prompt = f"Contexto del entorno:\n{req.context or 'Linux general'}\n\nLog de error a analizar:\n{req.error_log}\n\nDiagnostica la causa raíz y proporciona la solución técnica exacta."
    diagnosis = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2)

    # Extraer comandos recomendados heurísticamente
    import re
    commands = re.findall(r"```(?:bash|sh)?\s*([\s\S]*?)```", diagnosis)
    flat_commands = []
    for c in commands:
        for line in c.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                flat_commands.append(line)

    return ErrorDiagnosisResponse(
        root_cause="Análisis completado",
        explanation=diagnosis,
        suggested_fix=diagnosis,
        recommended_commands=flat_commands[:5]
    )

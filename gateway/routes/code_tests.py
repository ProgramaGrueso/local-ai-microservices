import re
import logging
from typing import Optional, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/code", tags=["14. Generador de Pruebas Unitarias y Docs"])

class CodeTestRequest(BaseModel):
    code_snippet: str = Field(description="Código fuente de la función, clase o módulo")
    language: Literal["python", "typescript", "javascript", "go", "rust", "cpp"] = Field(
        default="python",
        description="Lenguaje de programación del código"
    )
    test_framework: Optional[str] = Field(
        default="pytest",
        description="Framework de pruebas deseado (ej: pytest, unittest, jest, mocha, testing)"
    )

class CodeTestResponse(BaseModel):
    language: str
    framework: str
    unit_tests_code: str
    documented_code: str
    covered_scenarios: list[str]

SYSTEM_PROMPT = """Eres un ingeniero de aseguramiento de calidad (QA Senior) y desarrollador de software experto.
Tu objetivo es analizar un bloque de código y:
1. Generar una suite completa de pruebas unitarias robustas (happy paths, edge cases, errores de entrada, nulls).
2. Generar la versión del código original con documentación formal (Docstrings tipo Google en Python o JSDoc en JS/TS).
3. Resumir los escenarios de prueba cubiertos en una lista.

Responde ÚNICAMENTE en formato JSON con los campos:
- 'unit_tests_code': Código completo de los tests listo para ejecutar.
- 'documented_code': Código original enriquecido con docstrings y anotaciones de tipo.
- 'covered_scenarios': Lista de cadenas describiendo cada escenario probado."""

@router.post("/generate-tests", response_model=CodeTestResponse)
def generate_unit_tests(req: CodeTestRequest):
    """
    Genera tests unitarios exhaustivos y docstrings profesionales para cualquier código.
    """
    import json
    prompt = f"Lenguaje: {req.language}\nFramework: {req.test_framework}\n\nCódigo a testear:\n```\n{req.code_snippet}\n```\n\nGenera los tests y la documentación en JSON."
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.1, format_type="json")

    try:
        data = json.loads(raw)
        return CodeTestResponse(
            language=req.language,
            framework=req.test_framework or "pytest",
            unit_tests_code=data.get("unit_tests_code", ""),
            documented_code=data.get("documented_code", req.code_snippet),
            covered_scenarios=data.get("covered_scenarios", ["Casos estándar"])
        )
    except Exception:
        return CodeTestResponse(
            language=req.language,
            framework=req.test_framework or "pytest",
            unit_tests_code=raw,
            documented_code=req.code_snippet,
            covered_scenarios=["Generación cruda"]
        )

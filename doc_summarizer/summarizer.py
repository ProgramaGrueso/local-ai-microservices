import json
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentSummary(BaseModel):
    title: str = Field(description="Título formal del documento")
    authors: str = Field(default="Autor no identificado", description="Autores del documento")
    year: str = Field(default="s.f.", description="Año de publicación o fecha inferida")
    institution_or_source: str = Field(default="", description="Institución, revista o fuente editorial")
    keywords: List[str] = Field(default_factory=list, description="Palabras clave (4-6 términos)")
    abstract: str = Field(description="Resumen ejecutivo continuo estilo APA 7 (150 a 250 palabras)")
    objective: str = Field(description="Objetivo principal, justificación o problema abordado")
    methodology: str = Field(description="Enfoque metodológico, procedimiento o marco teórico empleado")
    key_findings: List[str] = Field(description="Puntos y hallazgos clave ordenados y detallados")
    conclusions: str = Field(description="Conclusiones principales, implicaciones prácticas o reflexiones finales")
    apa_reference: str = Field(description="Referencia bibliográfica formal del propio documento en estilo APA 7")

KEY_MAPPINGS = {
    "título": "title",
    "titulo": "title",
    "autores": "authors",
    "autor": "authors",
    "año": "year",
    "fecha": "year",
    "institucion": "institution_or_source",
    "institución": "institution_or_source",
    "palabras_clave": "keywords",
    "keywords": "keywords",
    "resumen": "abstract",
    "abstract": "abstract",
    "objetivo": "objective",
    "objetivos": "objective",
    "metodologia": "methodology",
    "metodología": "methodology",
    "hallazgos": "key_findings",
    "hallazgos_clave": "key_findings",
    "key_findings": "key_findings",
    "conclusiones": "conclusions",
    "conclusion": "conclusions",
    "referencia_apa": "apa_reference",
    "referencias": "apa_reference",
    "apa_reference": "apa_reference"
}

def normalize_dict_keys(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Mapea claves en español o variaciones a las esperadas por el modelo Pydantic."""
    normalized = {}
    for k, v in raw.items():
        clean_key = k.strip().lower().replace(" ", "_")
        target_key = KEY_MAPPINGS.get(clean_key, clean_key)
        normalized[target_key] = v
    
    # Asegurar que key_findings sea lista
    if "key_findings" in normalized and isinstance(normalized["key_findings"], str):
        normalized["key_findings"] = [normalized["key_findings"]]
    if "keywords" in normalized and isinstance(normalized["keywords"], str):
        normalized["keywords"] = [k.strip() for k in normalized["keywords"].split(",")]

    return normalized

SYSTEM_PROMPT = """Eres un asistente académico experto en metodología de investigación y normas APA (American Psychological Association, 7.ª edición).
Tu tarea es analizar minuciosamente el texto suministrado y extraer la metadata y el contenido para estructurar una síntesis formal y rigurosa en formato JSON.

Reglas estrictas para el esquema JSON:
- 'title': Título formal exacto del documento o artículo.
- 'authors': Nombres completos de los autores encontrados en el texto (ej: 'Dra. Elena Morales y Dr. Carlos Mendoza'). Solo usa 'Autor no identificado' si no hay ningún autor en el documento.
- 'year': Año de publicación o fecha encontrada (ej: '2025'). Solo usa 's.f.' si no hay ninguna fecha.
- 'institution_or_source': Institución de afiliación, universidad o revista mencionada.
- 'keywords': Lista de 4 a 6 palabras clave pertinentes.
- 'abstract': Párrafo de resumen formal de 150 a 250 palabras que sintetice el problema, métodos y resultados principales.
- 'objective': Objetivos claros y problema de investigación.
- 'methodology': Métodos, participantes, muestra, instrumentos o diseño experimental.
- 'key_findings': Lista de viñetas con los hallazgos empíricos y resultados cuantitativos/cualitativos más importantes.
- 'conclusions': Conclusiones, discusión e implicaciones prácticas o futuras líneas de trabajo.
- 'apa_reference': Referencia bibliográfica canónica del propio documento en estilo APA 7 (Apellido, Inicial. (Año). Título. Editorial o Institución).

DEBES responder estrictamente con el JSON estructurado."""

def prepare_content(markdown_text: str, max_chars: int = 48000) -> str:
    if len(markdown_text) <= max_chars:
        return markdown_text

    logger.warning(f"Documento extenso ({len(markdown_text)} caracteres). Truncando estratégicamente a {max_chars} caracteres.")
    part_size = max_chars // 2
    head = markdown_text[:part_size]
    tail = markdown_text[-part_size:]
    return f"{head}\n\n[... CONTENIDO INTERMEDIO CONDENSADO POR EXTENSIÓN ...]\n\n{tail}"

def generate_summary(
    markdown_text: str,
    model: str = "qwen2.5:7b",
    temperature: float = 0.2,
    max_chars: int = 48000
) -> DocumentSummary:
    content = prepare_content(markdown_text, max_chars=max_chars)
    user_prompt = f"Analiza el siguiente documento y genera el resumen estructurado APA 7 respetando el esquema JSON:\n\n{content}"

    logger.info(f"Enviando solicitud a Ollama (modelo: {model})...")
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        format=DocumentSummary.model_json_schema(),
        options={
            "temperature": temperature,
            "num_ctx": 16384
        }
    )

    raw_response = response["message"]["content"]
    data = json.loads(raw_response)
    clean_data = normalize_dict_keys(data)
    
    summary = DocumentSummary(**clean_data)
    return summary

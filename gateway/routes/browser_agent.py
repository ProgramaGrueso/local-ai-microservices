import logging
import httpx
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/browser", tags=["19. Agente de Extracción Web Estructurada"])

class DynamicScrapeRequest(BaseModel):
    url: str = Field(description="URL de la página a inspeccionar")
    fields_to_extract: List[str] = Field(description="Lista de campos específicos que quieres extraer (ej: ['precio', 'especificaciones', 'stock'])")

class DynamicScrapeResponse(BaseModel):
    url: str
    extracted_data: Dict[str, Any]
    status: str

@router.post("/extract-structured", response_model=DynamicScrapeResponse)
async def extract_structured_web(req: DynamicScrapeRequest):
    """
    Descarga una página web y utiliza el LLM para extraer campos específicos requeridos en formato JSON limpio.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            res = await client.get(req.url, headers=headers)
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"La página respondió con error: {res.status_code}")
            html_text = res.text[:25000]

        import json
        fields_str = ", ".join(req.fields_to_extract)
        prompt = f"De la siguiente página HTML/Texto extrae los siguientes campos: [{fields_str}].\n\nContenido de la página:\n{html_text}\n\nDevuelve ÚNICAMENTE un JSON con los campos extraídos."
        sys = "Eres un extractor de datos de comercio electrónico y páginas web. Devuelve JSON estricto."
        raw = ask_llm(prompt=prompt, system_prompt=sys, temperature=0.1, format_type="json")

        try:
            data = json.loads(raw)
        except Exception:
            data = {"raw_extraction": raw}

        return DynamicScrapeResponse(
            url=req.url,
            extracted_data=data,
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en extracción web: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

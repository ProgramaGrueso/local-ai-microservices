import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl
import trafilatura
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/web", tags=["6. Lector Web y Extractor Markdown"])

class WebExtractRequest(BaseModel):
    url: str = Field(description="URL de la página, blog o artículo a procesar")
    summarize: bool = Field(default=True, description="Generar resumen y puntos clave con IA")

class WebExtractResponse(BaseModel):
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    markdown_content: str
    summary_bullets: Optional[List[str]] = None

@router.post("/extract", response_model=WebExtractResponse)
def extract_web_article(req: WebExtractRequest):
    """
    Descarga cualquier página web, elimina publicidad y trackers, y extrae el texto a Markdown limpio.
    """
    try:
        downloaded = trafilatura.fetch_url(req.url)
        if not downloaded:
            raise HTTPException(status_code=400, detail="No se pudo descargar la URL especificada.")

        # Extracción de metadatos y contenido en formato Markdown
        result = trafilatura.extract(
            downloaded,
            output_format="markdown",
            include_links=True,
            include_images=False,
            include_tables=True,
            with_metadata=True
        )

        if not result:
            raise HTTPException(status_code=422, detail="No se pudo extraer contenido legible de la página.")

        # Extraer metadatos
        metadata = trafilatura.extract_metadata(downloaded)
        title = metadata.title if metadata else None
        author = metadata.author if metadata else None
        date = metadata.date if metadata else None

        bullets = None
        if req.summarize:
            prompt = f"Analiza el siguiente artículo web y resume sus 4 puntos más trascendentales en viñetas directas:\n\n{result[:15000]}"
            sys = "Eres un analista de contenidos que genera resúmenes concisos y de alto impacto en español."
            ai_out = ask_llm(prompt=prompt, system_prompt=sys)
            bullets = [b.strip("-* ").strip() for b in ai_out.split("\n") if b.strip().startswith(("-", "*", "•", "1", "2", "3", "4"))]

        return WebExtractResponse(
            url=req.url,
            title=title,
            author=author,
            date=date,
            markdown_content=result,
            summary_bullets=bullets
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extrayendo artículo web: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

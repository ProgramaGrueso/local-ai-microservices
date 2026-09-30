import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

# Importar los routers de productividad y contenidos
from routes.transcription import router as transcription_router
from routes.semantic_search import router as semantic_search_router
from routes.text_enhancer import router as text_router
from routes.web_reader import router as web_router
from routes.error_diagnostics import router as diagnostics_router
from routes.tts_speech import router as tts_router
from routes.file_organizer import router as organizer_router

# Importar los routers multimedia, devops y PKM
from routes.youtube_summary import router as youtube_router
from routes.bash_copilot import router as bash_router
from routes.email_assistant import router as email_router
from routes.code_tests import router as tests_router
from routes.pii_masking import router as pii_router
from routes.receipt_extractor import router as receipt_router
from routes.voice_cloning import router as voice_router
from routes.podcast_generator import router as podcast_router
from routes.browser_agent import router as browser_router
from routes.image_forensics import router as forensics_router
from routes.obsidian_bridge import router as obsidian_router
from routes.system_resources import router as system_resources_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AIGateway")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
## 🧠 Suite Unificada de Microservicios de IA (Local Monorepo)

Esta API expone 19 microservicios de Inteligencia Artificial de alto rendimiento operando de forma 100% local o híbrida sobre Linux (CachyOS):

### Grupo A: Productividad de Contenidos y Documentos
1. **Transcripción de Audio**: Whisper local + resumen ejecutivo de notas de voz/reuniones.
2. **Búsqueda Semántica (RAG)**: Base de conocimiento vectorial persistente con ChromaDB.
3. **Corrección y Tono**: Proofreading, formalización, modo académico y traducción.
4. **Lector Web**: Extracción limpia de páginas web a Markdown sin publicidad.
5. **Diagnóstico de Errores**: Explicador de stack traces y soluciones paso a paso.
6. **Texto a Voz (TTS)**: Conversión de artículos a audio descargable.
7. **Organización Inteligente**: Renombrado canónico y clasificación de archivos.
8. **Monitoreo de Hardware**: Uso en tiempo real de RAM del sistema y VRAM GPU con purga.

### Grupo B: Multimedia, DevOps, Seguridad y PKM
9. **Resumen de YouTube**: Descarga y síntesis ejecutiva de videos con marcas de tiempo.
10. **Copilot de Terminal Bash**: Generación de comandos shell seguros a partir de lenguaje natural.
11. **Redactor de Correos**: Creación de respuestas y correos profesionales a partir de notas rápidas.
12. **Tests Unitarios & Docs**: Generación de pruebas PyTest/Jest y docstrings para cualquier código.
13. **Anonimización PII**: Detección y reemplazo seguro de datos sensibles (RGPD).
14. **Extractor Financiero**: Parseo estructurado de facturas y tickets a JSON contable.
15. **Clonación de Voz**: Perfiles vocales y síntesis personalizada.
16. **Generador de Podcasts**: Guiones a 2 voces estilo Google NotebookLM.
17. **Extractor Web Dinámico**: Extracción focalizada de campos clave desde páginas web.
18. **Forense de Imágenes**: Detección de metadatos de generación por IA vs fotografía real.
19. **Puente Obsidian (PKM)**: Creación de notas atómicas con YAML Frontmatter y enlaces `[[WikiLinks]]` directo a tus Vaults.
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar los 19 routers
app.include_router(transcription_router)
app.include_router(semantic_search_router)
app.include_router(text_router)
app.include_router(web_router)
app.include_router(diagnostics_router)
app.include_router(tts_router)
app.include_router(organizer_router)
app.include_router(youtube_router)
app.include_router(bash_router)
app.include_router(email_router)
app.include_router(tests_router)
app.include_router(pii_router)
app.include_router(receipt_router)
app.include_router(voice_router)
app.include_router(podcast_router)
app.include_router(browser_router)
app.include_router(forensics_router)
app.include_router(obsidian_router)
app.include_router(system_resources_router)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "swagger_docs": "/docs",
        "endpoints_active": 19
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.py:app", host=settings.HOST, port=settings.PORT, reload=True)

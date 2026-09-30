import os
import uuid
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import chromadb
from core.config import settings
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["2. Búsqueda Semántica Local (RAG)"])

# Cliente persistente local de ChromaDB
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name="personal_knowledge_base")

class DocumentInput(BaseModel):
    title: str = Field(description="Título o referencia del documento")
    content: Optional[str] = Field(default=None, description="Texto completo o párrafo a indexar")
    raw_content: Optional[str] = Field(default=None, description="Alias alternativo para content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos adicionales (categoría, fecha, origen)")

class QueryInput(BaseModel):
    query: str = Field(description="Pregunta o concepto que deseas buscar")
    n_results: int = Field(default=3, description="Número de resultados más relevantes a devolver")
    synthesize_answer: bool = Field(default=True, description="Sintetizar respuesta usando los fragmentos encontrados")

@router.post("/index")
def index_document(doc: DocumentInput):
    """Indexa un fragmento de conocimiento en la base de datos vectorial local."""
    text_to_index = doc.content or doc.raw_content
    if not text_to_index or not text_to_index.strip():
        raise HTTPException(status_code=400, detail="Debes proporcionar 'content' o 'raw_content' con texto a indexar.")

    doc_id = str(uuid.uuid4())
    raw_meta = doc.metadata or {}
    clean_meta: Dict[str, Any] = {"title": doc.title}

    # ChromaDB solo acepta metadatos primitivos (str, int, float, bool).
    # Filtramos placeholders de Swagger como 'additionalProp1: {}'
    for k, v in raw_meta.items():
        if isinstance(v, (str, int, float, bool)):
            clean_meta[k] = v
        elif isinstance(v, (list, tuple)):
            clean_meta[k] = ", ".join(str(x) for x in v)
        elif v is not None and not (isinstance(v, dict) and not v):
            clean_meta[k] = str(v)

    try:
        collection.add(
            documents=[text_to_index.strip()],
            metadatas=[clean_meta],
            ids=[doc_id]
        )
    except Exception as e:
        logger.error(f"Error indexando en ChromaDB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en base de datos vectorial: {str(e)}")

    return {"status": "success", "id": doc_id, "title": doc.title, "total_indexed": collection.count()}

@router.post("/query")
def semantic_search(data: QueryInput):
    """Busca por significado semántico entre todos tus documentos indexados."""
    if collection.count() == 0:
        return {"query": data.query, "results": [], "answer": "La base de conocimientos aún no tiene documentos indexados."}

    results = collection.query(
        query_texts=[data.query],
        n_results=min(data.n_results, collection.count())
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        hits.append({
            "content": doc,
            "metadata": meta,
            "relevance_score": round(1.0 - (dist if dist is not None else 0), 3)
        })

    answer = None
    if data.synthesize_answer and hits:
        context_str = "\n---\n".join([f"Fuente ({h['metadata'].get('title')}): {h['content']}" for h in hits])
        prompt = f"Basándote EXCLUSIVAMENTE en el siguiente contexto recuperado de la base de conocimientos, responde a la pregunta de forma precisa:\n\nContexto:\n{context_str}\n\nPregunta: {data.query}"
        answer = ask_llm(prompt=prompt, system_prompt="Eres un asistente de investigación académica y documental riguroso.")

    return {
        "query": data.query,
        "results": hits,
        "answer": answer
    }

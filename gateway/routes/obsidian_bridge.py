import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/obsidian", tags=["21. Integración con Obsidian (PKM Bridge)"])

KNOWN_VAULTS = {
    "personal": os.path.expanduser(os.getenv("OBSIDIAN_VAULT_PERSONAL", "~/Obsidian/Personal")),
    "maestria": os.path.expanduser(os.getenv("OBSIDIAN_VAULT_MAESTRIA", "~/Obsidian/Maestria"))
}

class CreateNoteRequest(BaseModel):
    title: str = Field(description="Título formal de la nota")
    raw_content: str = Field(description="Idea, apunte, transcripción o texto que deseas convertir en nota permanente")
    vault_name: Literal["personal", "maestria"] = Field(
        default="personal",
        description="Bóveda destino: rutas configurables con OBSIDIAN_VAULT_PERSONAL y OBSIDIAN_VAULT_MAESTRIA"
    )
    status: Literal["borrador", "en-progreso", "completado"] = Field(default="en-progreso")
    auto_link: bool = Field(default=True, description="Enlazar conceptos clave automáticamente con sintaxis [[WikiLink]]")

class CreateNoteResponse(BaseModel):
    vault_path: str
    file_path: str
    title: str
    tags: List[str]
    linked_concepts: List[str]
    markdown_content: str

SYSTEM_PROMPT = """Eres un arquitecto del conocimiento experto en la metodología Zettelkasten y usuario avanzado de Obsidian.
Tu objetivo es transformar el contenido provisto en una Nota Permanente (Permanent Note) impecable.

Reglas:
1. Genera un bloque YAML Frontmatter canónico con:
   - tags: lista de 3 a 5 tags en kebab-case relevantes (ej: ingenieria-software, inteligencia-artificial, productividad).
   - date: fecha actual (YYYY-MM-DD).
   - status: el status provisto.
2. El cuerpo debe comenzar con '# Título'.
3. Si 'auto_link' es verdadero, encierra conceptos clave, disciplinas, autores o temas relevantes entre corchetes dobles de Obsidian (ej: [[Machine Learning]], [[Transformers]], [[Ciberseguridad]]).
4. Mantén tono reflexivo, analítico, estructurado con subtítulos y listas claras.

Responde ÚNICAMENTE con un JSON con los campos:
- 'tags': lista de strings
- 'linked_concepts': lista de conceptos encerrados en [[...]]
- 'full_markdown': el archivo markdown completo listo para guardar."""

@router.get("/vaults")
def list_vaults():
    """
    Lista los Vaults de Obsidian detectados en tu sistema y su estado.
    """
    vaults_info = {}
    for name, path_str in KNOWN_VAULTS.items():
        p = Path(path_str)
        if p.exists() and (p / ".obsidian").exists():
            notes = list(p.glob("*.md"))
            vaults_info[name] = {
                "path": str(p),
                "active": True,
                "total_notes": len(notes),
                "recent_notes": [n.stem for n in sorted(notes, key=lambda f: f.stat().st_mtime, reverse=True)[:5]]
            }
        else:
            vaults_info[name] = {"path": str(p), "active": False}
    return vaults_info

@router.post("/create-note", response_model=CreateNoteResponse)
def create_obsidian_note(req: CreateNoteRequest):
    """
    Transforma cualquier apunte en una nota de Obsidian con Frontmatter YAML y [[enlaces bidireccionales]], guardándola directamente en tu Vault.
    """
    vault_path = KNOWN_VAULTS.get(req.vault_name)
    if not vault_path or not os.path.exists(vault_path):
        raise HTTPException(status_code=404, detail=f"No se encontró el vault '{req.vault_name}' en {vault_path}")

    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"Título: {req.title}\nFecha: {today_str}\nStatus: {req.status}\nAuto-enlaces: {req.auto_link}\n\nContenido base:\n{req.raw_content}\n\nGenera la nota para Obsidian en JSON."
    
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2, format_type="json")

    try:
        data = json.loads(raw)
        md_content = data.get("full_markdown", "")
        tags = data.get("tags", ["general"])
        linked = data.get("linked_concepts", [])
    except Exception:
        # Fallback manual
        tags = ["apuntes", "ia"]
        linked = []
        md_content = f"""---
tags:
  - {tags[0]}
date: {today_str}
status: {req.status}
---

# {req.title}

{req.raw_content}
"""

    # Sanitizar nombre de archivo
    clean_title = re.sub(r'[\\/*?:"<>|]', "", req.title).strip()
    file_path = os.path.join(vault_path, f"{clean_title}.md")

    # Guardar la nota directamente en el Vault de Obsidian
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return CreateNoteResponse(
        vault_path=vault_path,
        file_path=file_path,
        title=clean_title,
        tags=tags,
        linked_concepts=linked,
        markdown_content=md_content
    )

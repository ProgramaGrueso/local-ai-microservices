import logging
from typing import Optional, Dict, Any, List
import ollama
from core.config import settings

logger = logging.getLogger(__name__)

def ask_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.3,
    format_type: Optional[str] = None
) -> str:
    """Helper unificado para llamadas de texto a Ollama."""
    selected_model = model or settings.DEFAULT_LLM
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    kwargs: Dict[str, Any] = {
        "model": selected_model,
        "messages": messages,
        "options": {"temperature": temperature}
    }
    if format_type:
        kwargs["format"] = format_type

    res = ollama.chat(**kwargs)
    return res["message"]["content"]

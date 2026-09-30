import json
import logging
from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.llm import ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/finance", tags=["16. Extractor de Recibos y Facturas"])

class ReceiptItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    total_price: float = 0.0

class ReceiptExtractResponse(BaseModel):
    merchant_name: str
    date: str
    tax_id: Optional[str] = None
    currency: str
    items: List[ReceiptItem]
    subtotal: float
    taxes: float
    total: float
    expense_category: str

class ReceiptTextRequest(BaseModel):
    raw_receipt_text: str = Field(description="Texto OCR o transcripción del ticket o factura")

SYSTEM_PROMPT = """Eres un asistente contable y auditor financiero.
Tu tarea es analizar el texto de una factura o ticket de compra y extraer todos los datos estructurados en JSON.

Categorías de gasto estándar: ['Alimentación', 'Hardware/Tecnología', 'Suscripciones/Software', 'Transporte', 'Servicios', 'Oficina', 'Salud', 'Otros'].

Esquema JSON requerido:
- 'merchant_name': Nombre del comercio o emisor
- 'date': Fecha en formato YYYY-MM-DD (o aproximada)
- 'tax_id': RUC, CIF, NIT o identificación fiscal (o null)
- 'currency': Código de moneda (USD, EUR, PEN, etc.)
- 'items': Lista de objetos con {'description', 'quantity', 'unit_price', 'total_price'}
- 'subtotal': Número decimal
- 'taxes': Número decimal (IVA, IGV, etc.)
- 'total': Número decimal del importe final
- 'expense_category': Una de las categorías estándar"""

@router.post("/extract-receipt", response_model=ReceiptExtractResponse)
def extract_receipt(req: ReceiptTextRequest):
    """
    Convierte el texto desordenado de un ticket o recibo en un registro contable estructurado en JSON.
    """
    prompt = f"Analiza el siguiente comprobante y extrae la información financiera en JSON:\n\n{req.raw_receipt_text}"
    raw = ask_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.1, format_type="json")

    try:
        data = json.loads(raw)
        return ReceiptExtractResponse(**data)
    except Exception as e:
        logger.error(f"Error parseando factura: {e}")
        return ReceiptExtractResponse(
            merchant_name="No identificado",
            date="2026-09-24",
            currency="USD",
            items=[],
            subtotal=0.0,
            taxes=0.0,
            total=0.0,
            expense_category="Otros"
        )

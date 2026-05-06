import json
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from crud import delete_receipt, get_all_receipts, get_receipt, insert_receipt, update_receipt
from schemas import ReceiptOut, ReceiptPatch
from service import ocr_image, parse_receipt

router = APIRouter(prefix="/receipts", tags=["Receipts"])

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}


@router.post("", response_model=ReceiptOut, status_code=201)
async def create_receipt(file: UploadFile = File(..., description="Imagem do recibo")):
    """Faz upload de uma imagem de recibo, extrai os dados via OCR + LLM e salva no banco."""
    suffix = Path(file.filename or "receipt.png").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Formato '{suffix}' não suportado. Aceitos: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        raw_text = ocr_image(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    try:
        parsed = parse_receipt(raw_text)
    except (json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"O modelo retornou uma saída inválida: {exc}",
        )

    receipt = {
        "id": str(uuid.uuid4()),
        "description": parsed.get("description"),
        "amount": parsed.get("amount"),
        "purchase_time": parsed.get("purchase_time"),
        "location": parsed.get("location"),
        "raw_text": raw_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    insert_receipt(receipt)
    return receipt


@router.get("", response_model=list[ReceiptOut])
def list_receipts():
    """Retorna todos os recibos salvos, do mais recente ao mais antigo."""
    return get_all_receipts()


@router.get("/{receipt_id}", response_model=ReceiptOut)
def read_receipt(receipt_id: str):
    """Busca um recibo pelo ID."""
    receipt = get_receipt(receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Recibo não encontrado")
    return receipt


@router.patch("/{receipt_id}", response_model=ReceiptOut)
def patch_receipt(receipt_id: str, data: ReceiptPatch):
    """Atualiza parcialmente os campos de um recibo."""
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Nenhum campo fornecido para atualizar")

    updated = update_receipt(receipt_id, fields)
    if updated is None:
        raise HTTPException(status_code=404, detail="Recibo não encontrado")
    return updated


@router.delete("/{receipt_id}", status_code=204)
def remove_receipt(receipt_id: str):
    """Remove um recibo permanentemente."""
    if not delete_receipt(receipt_id):
        raise HTTPException(status_code=404, detail="Recibo não encontrado")

import json
import logging
import time
from pathlib import Path

import ollama
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

OCR_MODEL = "glm-ocr"
PARSE_MODEL = "gpt-4.1-mini"

_PARSE_PROMPT = """\
You are a receipt data extractor. Given raw OCR text from a receipt, return ONLY a valid JSON object with exactly these keys:

- "description": short summary of what was purchased and the store name (string)
- "amount": total amount paid as a number (float), or null if not found
- "purchase_time": date and/or time of the transaction in ISO 8601 format, or null if not found
- "location": store address or city/state, or null if not found

Do not include any explanation or markdown fencing — just the raw JSON.

OCR text:
{raw_text}
"""


def check_ollama() -> None:
    """Verifica se o Ollama está rodando e se o modelo está disponível."""
    try:
        models = [m.model for m in ollama.list().models]
        logger.info("[Ollama] Modelos instalados: %s", models)
        if not any(OCR_MODEL in m for m in models):
            logger.warning(
                "[Ollama] Modelo '%s' NÃO encontrado. Execute: ollama pull %s",
                OCR_MODEL, OCR_MODEL,
            )
        else:
            logger.info("[Ollama] Modelo '%s' disponível.", OCR_MODEL)
    except Exception as exc:
        logger.error("[Ollama] Não foi possível conectar ao Ollama: %s", exc)
        logger.error("[Ollama] Certifique-se que o Ollama está rodando em http://localhost:11434")


def ocr_image(image_path: Path) -> str:
    size_kb = round(image_path.stat().st_size / 1024, 1)
    logger.info("[OCR] Iniciando — %s (%.1f KB)", image_path.name, size_kb)

    try:
        running = ollama.ps()
        loaded = [m.model for m in (running.models or [])]
        if any(OCR_MODEL in m for m in loaded):
            logger.info("[OCR] '%s' já está carregado na GPU.", OCR_MODEL)
        else:
            logger.info("[OCR] '%s' não está na memória ainda — primeira chamada será mais lenta.", OCR_MODEL)
    except Exception:
        pass

    t0 = time.perf_counter()
    response = ollama.chat(
        model=OCR_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Text Recognition",
                "images": [str(image_path)],
            }
        ],
        options={"temperature": 0, "num_ctx": 8192},
    )
    elapsed = time.perf_counter() - t0
    text = response["message"]["content"]
    logger.info("[OCR] Concluído em %.1fs — %d caracteres extraídos.", elapsed, len(text))
    return text


def parse_receipt(raw_text: str) -> dict:
    logger.info("[LLM] Enviando %d chars para %s...", len(raw_text), PARSE_MODEL)
    t0 = time.perf_counter()

    llm = ChatOpenAI(model=PARSE_MODEL, temperature=0)
    response = llm.invoke([HumanMessage(content=_PARSE_PROMPT.format(raw_text=raw_text))])
    elapsed = time.perf_counter() - t0

    content = response.content.strip()
    logger.info("[LLM] Resposta recebida em %.1fs.", elapsed)

    if content.startswith("```"):
        lines = content.splitlines()
        content = "\n".join(line for line in lines if not line.startswith("```")).strip()

    parsed = json.loads(content)
    logger.info(
        "[LLM] Parsing OK — %r | R$ %s | %r",
        parsed.get("description"),
        parsed.get("amount"),
        parsed.get("location"),
    )
    return parsed

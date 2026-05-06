import json
from pathlib import Path

import ollama
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

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


def ocr_image(image_path: Path) -> str:
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
    return response["message"]["content"]


def parse_receipt(raw_text: str) -> dict:
    llm = ChatOpenAI(model=PARSE_MODEL, temperature=0)
    message = HumanMessage(content=_PARSE_PROMPT.format(raw_text=raw_text))
    response = llm.invoke([message])

    content = response.content.strip()

    # Strip accidental markdown fences the model might add despite instructions
    if content.startswith("```"):
        lines = content.splitlines()
        content = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    return json.loads(content)

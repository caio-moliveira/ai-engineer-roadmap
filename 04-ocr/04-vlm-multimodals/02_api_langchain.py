import base64
import io
import os
from pathlib import Path
import pypdfium2 as pdfium
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


def pdf_para_base64(pdf_path: str, pagina: int = 0, dpi: int = 150) -> str:
    escala = dpi / 72.0
    pdf = pdfium.PdfDocument(pdf_path)
    img = pdf[pagina].render(scale=escala).to_pil()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def rodar_modelo(modelo, imagem_b64: str, prompt: str) -> tuple[str, float]:
    mensagem = HumanMessage(content=[
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{imagem_b64}"}},
        {"type": "text", "text": prompt},
    ])
    resposta = modelo.invoke([mensagem])
    return resposta
    # return resposta.content


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "..", "docs", "1.pdf")

    print("Convertendo PDF para imagem...")
    imagem = pdf_para_base64(pdf_path)

    prompt = (
        "Extract all the text from this document. "
        "If there are any images, charts or diagrams, describe them. "
        "Preserve the document structure as much as possible."
    )

    # modelo = ChatOpenAI(model="gpt-5.4")
    modelo = ChatAnthropic(model="claude-opus-4-7")

    resultado = rodar_modelo(modelo, imagem, prompt)
    # saida = Path(pdf_path).with_suffix(".md")
    # saida.write_text(resultado, encoding="utf-8")

    print(resultado)


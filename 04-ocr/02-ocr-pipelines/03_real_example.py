"""
Extração estruturada de Decreto Orçamentário (PDF escaneado).
Fluxo: PDF → pypdfium2 (renderizar páginas) → Tesseract (OCR) → OpenAI (estruturar) → Markdown

Desafio real deste documento:
  - Pontos (......) são linhas guia de formatação, não conteúdo — o LLM ignora isso.
  - Hierarquia: Órgão > Unidade > Sub-Unidade > Item orçamentário

Dependências: uv add pytesseract pillow pypdfium2 openai python-dotenv
"""

import os
import pytesseract
import pypdfium2 as pdfium
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# =============================================================================
# PASSO 1 — OCR: PDF → texto bruto
# Renderizamos cada página como imagem (alta resolução) e extraímos o texto.
# =============================================================================

def ocr_pdf(caminho_pdf: str) -> str:
    """Renderiza cada página do PDF e extrai texto com Tesseract."""
    pdf = pdfium.PdfDocument(caminho_pdf)
    texto_completo = ""

    for i, pagina in enumerate(pdf):
        img: Image.Image = pagina.render(scale=3).to_pil()  # scale=3 → ~216 DPI
        texto_pagina = pytesseract.image_to_string(img, lang='por', config=r'--oem 3 --psm 6')
        texto_completo += f"\n[ Página {i+1} ]\n{texto_pagina}"

    return texto_completo


# =============================================================================
# PASSO 2 — Estruturação com OpenAI → Markdown
# O texto bruto tem pontos (....) como artefatos de formatação.
# O LLM entende a hierarquia do documento e monta a tabela Markdown.
# =============================================================================

SYSTEM_PROMPT = """Você é um especialista em documentos orçamentários municipais brasileiros.
O texto abaixo foi extraído por OCR de um Decreto Suplementar e pode conter:
- Sequências de pontos (......) que são linhas guia de formatação — ignore-as completamente.
- Erros tipográficos leves do OCR.

Reproduza a estrutura hierárquica do documento em Markdown

Regras:
- Preserve todos os níveis hierárquicos (Órgão, Unidade, Sub-Unidade).
- Cada tabela contém apenas os itens da Sub-Unidade correspondente.
- Use vírgula como separador decimal nos valores (padrão brasileiro).
- Retorne apenas o Markdown. Nenhum texto fora dele."""


def estruturar_decreto(texto_bruto: str) -> str:
    """Envia o texto OCR para a OpenAI e retorna o decreto formatado em Markdown."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": texto_bruto},
        ],
    )

    return response.choices[0].message.content


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf = os.path.join(BASE_DIR, "..", "docs", "1.pdf")

    # Passo 1: OCR
    print("Extraindo texto com Tesseract...")
    texto_bruto = ocr_pdf(pdf)

    # Passo 2: Estruturação
    print("Enviando texto para OpenAI estruturar...\n")
    markdown = estruturar_decreto(texto_bruto)

    print(markdown)

    # Salva o resultado em arquivo
    saida = os.path.join(BASE_DIR, "output.md")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"\nArquivo salvo em: {saida}")

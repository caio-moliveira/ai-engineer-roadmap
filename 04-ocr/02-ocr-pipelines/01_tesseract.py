import time
import os
import pytesseract
from PIL import Image

# Força o caminho do executável do Tesseract no Windows para evitar o erro TesseractNotFoundError
# Caso você tenha instalado em outro diretório, ajuste o caminho abaixo
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def run_tesseract_imagem(image_path: str):
    """Extrai texto de uma imagem simples (JPG, PNG)."""
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Erro: Imagem '{image_path}' não encontrada.")
        return

    start = time.time()
    texto = pytesseract.image_to_string(img, lang='por', config=r'--oem 3 --psm 3')
    tempo = time.time() - start

    print(f"--- Tesseract: Extração de Imagem ---")
    print(f"Tempo: {tempo:.2f}s\n\nTexto Extraído:\n{texto.strip()}\n")


def run_tesseract_pdf(pdf_path: str):
    """
    Extrai texto de um PDF escaneado (Múltiplas páginas).
    OBS: Converte silenciosamente as páginas em imagem usando a lib 'pypdfium2'.
    """
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("Erro: Instale a dependência para trabalhar com PDFs rodando: uv add pypdfium2")
        return

    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except FileNotFoundError:
        print(f"Erro: PDF '{pdf_path}' não encontrado.")
        return

    start = time.time()
    texto_completo = ""
    
    # Fazemos um loop pelas páginas. Usamos scale=3 para aumentar a resolução (DPI) 
    # da imagem gerada, pois o Tesseract exige alta qualidade para não errar letras!
    for i, pagina in enumerate(pdf):
        img_pil = pagina.render(scale=3).to_pil()
        texto_pagina = pytesseract.image_to_string(img_pil, lang='por', config=r'--oem 3 --psm 3')
        texto_completo += f"\n[ --- Página {i+1} --- ]\n{texto_pagina.strip()}\n"

    tempo = time.time() - start
    print(f"--- Tesseract: Extração de PDF Escaneado ---")
    print(f"Tempo: {tempo:.2f}s\n\nTexto Completo Extraído:\n{texto_completo}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    imagem_teste = os.path.join(BASE_DIR, "..", "docs", "logo.png")
    pdf_teste = os.path.join(BASE_DIR, "..", "docs", "1.pdf")

    # run_tesseract_imagem(imagem_teste)
    run_tesseract_pdf(pdf_teste)

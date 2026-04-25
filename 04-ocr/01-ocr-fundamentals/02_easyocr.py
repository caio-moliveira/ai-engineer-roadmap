import time
import os
import easyocr
import numpy as np

def run_easyocr_imagem(image_path: str):
    """Extrai texto de uma imagem simples (JPG, PNG)."""
    start = time.time()
    
    try:
        reader = easyocr.Reader(['pt', 'en'], gpu=True)
        resultados = reader.readtext(image_path, detail=0)
    except Exception as e:
        print(f"Erro ao processar imagem '{image_path}': {e}")
        return

    tempo = time.time() - start
    texto = "\n".join(resultados)

    print(f"--- EasyOCR: Extração de Imagem ---")
    print(f"Tempo: {tempo:.2f}s\n\nTexto Extraído:\n{texto}\n")


def run_easyocr_pdf(pdf_path: str):
    """
    Extrai texto de um PDF escaneado convertendo as páginas na memória.
    OBS: Usa a superleve biblioteca 'pypdfium2' para converter página em imagem.
    """
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("Erro: A biblioteca 'pypdfium2' é necessária para PDFs.")
        print("Instale com: uv add pypdfium2")
        return

    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except FileNotFoundError:
        print(f"Erro: PDF '{pdf_path}' não encontrado.")
        return

    start = time.time()
    try:
        reader = easyocr.Reader(['pt', 'en'], gpu=True)
    except Exception as e:
        print(f"Erro no Reader do EasyOCR: {e}")
        return

    texto_completo = ""

    # Extrai página a página
    for i, pagina in enumerate(pdf):
        # Renderiza com alta qualidade (scale=3)
        img_pil = pagina.render(scale=3).to_pil()
        # O EasyOCR processa a imagem diretamente se a passarmos como Matriz do NumPy
        img_np = np.array(img_pil)
        
        resultados = reader.readtext(img_np, detail=0)
        texto_pagina = "\n".join(resultados)
        texto_completo += f"\n[ --- Página {i+1} --- ]\n{texto_pagina}\n"

    tempo = time.time() - start
    print(f"--- EasyOCR: Extração de PDF Escaneado ---")
    print(f"Tempo: {tempo:.2f}s\n\nTexto Completo Extraído:\n{texto_completo}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    imagem_teste = os.path.join(BASE_DIR, "..", "docs", "1.jpeg")
    pdf_teste = os.path.join(BASE_DIR, "..", "docs", "Caratinga.pdf")

    # ===============================
    # Descomente o que deseja testar:
    # ===============================

    run_easyocr_imagem(imagem_teste)
    # run_easyocr_pdf(pdf_teste)

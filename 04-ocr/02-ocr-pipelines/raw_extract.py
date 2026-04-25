import os
import pypdfium2 as pdfium

def extracao_nativa_pdf(pdf_path: str):

    pdf = pdfium.PdfDocument(pdf_path)
    texto_completo = ""

    for i, pagina in enumerate(pdf):
        textpage = pagina.get_textpage()
        texto_pagina = textpage.get_text_range()
        
        texto_completo += f"\n[ --- Página {i+1} --- ]\n{texto_pagina.strip()}\n"

    print(f"Texto Completo Extraído:\n{texto_completo}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_teste = os.path.join(BASE_DIR, "..", "docs", "Caratinga.pdf")
    
    extracao_nativa_pdf(pdf_teste)

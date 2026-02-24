import fitz

def load_pdf_from_bytes(data: bytes) -> tuple[str, int]:
    """Lê PDF diretamente da memória (bytes) usando PyMuPDF (fitz)."""   
    with fitz.open(stream=data, filetype="pdf") as doc:
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        
        return "\n\n".join(full_text), len(doc)


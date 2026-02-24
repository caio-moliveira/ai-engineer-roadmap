from langchain_community.document_loaders import PyMuPDFLoader
from src.settings import settings
import fitz

def load_pdf_to_text_and_pages(path: str) -> tuple[str, int]:
    loader = PyMuPDFLoader(path)
    docs = loader.load()
    texts = [d.page_content for d in docs]
    full = "\n\n".join(texts)
    return full, len(docs)


def load_pdf_from_bytes(data: bytes) -> tuple[str, int]:
    """Lê PDF diretamente da memória (bytes) usando PyMuPDF (fitz)."""   
    with fitz.open(stream=data, filetype="pdf") as doc:
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        
        return "\n\n".join(full_text), len(doc)


def load_first_page_text(pdf_bytes: bytes) -> str:
    """Extrai texto apenas da primeira página."""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            if len(doc) > 0:
                return doc[0].get_text()
        return ""
    except Exception as e:
        return ""


from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pypdf import PdfReader

def load_pdf_text(filepath):
    """Helper simples para ler o PDF inteiro como string."""
    if not os.path.exists(filepath):
        # Tenta achar no subdiretório
        filepath = os.path.join("02-rag", "02-ingestion-pipeline", filepath)
        
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo {filepath} não encontrado.")
    
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def main():
    pdf_filename = "Understanding_Climate_Change.pdf"
    
    try:
        print(f"--- Lendo {pdf_filename} ---")
        long_text = load_pdf_text(pdf_filename)
        print(f"Texto carregado: {len(long_text)} caracteres.")
        
    except Exception as e:
        print(f"Erro: {e}")
        return
    
    print("\n--- Texto Original (Preview) ---")
    print(long_text[:200] + "...")
    
    # Configuração do Splitter
    # chunk_size: Tamanho alvo do chunk (em caracteres, por padrão).
    # chunk_overlap: Quanto do chunk anterior se repete no próximo (para manter continuidade).
    # separators: A ordem importa! Tenta quebrar por parágrafo, depois linha, depois espaço.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, # Aumentei um pouco pois o texto real é maior
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_text(long_text)
    
    print(f"\n--- Chunks Gerados ({len(chunks)}) ---")
    for i, chunk in enumerate(chunks[:3]): # Mostrando só os 3 primeiros
        print(f"[{i}] len={len(chunk)}: {repr(chunk[:100])}...")
        
    print(f"... e mais {len(chunks)-3} chunks.")

if __name__ == "__main__":
    main()

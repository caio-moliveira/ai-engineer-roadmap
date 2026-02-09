from langchain_text_splitters import TokenTextSplitter, CharacterTextSplitter, RecursiveCharacterTextSplitter
import tiktoken
# ==========================================
# 🔢 04. Token Splitter (Limite Rígido)
# ==========================================
#
# LLMs têm limites em Tokens, não caracteres.
# O TokenTextSplitter usa o tokenizer do modelo (ex: cl100k_base da OpenAI)
# para garantir que o chunk nunca ultrapasse X tokens.
#
# ✅ Vantagens: Garante que cabe no Context Window.
# ❌ Desvantagens: Pode cortar palavras no meio se não configurado com cuidado (embora o tiktoken seja robusto).
#
# Instale: pip install tiktoken

import os
from pypdf import PdfReader

def load_pdf_text(filepath):
    if not os.path.exists(filepath):
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
    except Exception as e:
        print(f"Erro: {e}")
        return

    print(f"--- Texto com {len(long_text)} caracteres ---")
    
    # Configuração: Recursive + Token Limit
    # Isso é o "Melhor dos Dois Mundos":
    # 1. Respeita a semântica (tenta não cortar parágrafos)
    # 2. Respeita o limite duro de tokens (X tokens max)
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4o",
        chunk_size=1000, # Tokens! (aprox 4000 caracteres)
        chunk_overlap=200
    )
    
    
    chunks = splitter.split_text(long_text)
    
    # Validação com tiktoken para mostrar que funcionou
    enc = tiktoken.encoding_for_model("gpt-4.1-mini")

    print(f"\n--- Chunks Gerados ({len(chunks)}) ---")
    for i, chunk in enumerate(chunks[:3]): # Mostrando só os 3 primeiros
        token_count = len(enc.encode(chunk))
        print(f"[{i}] Tokens={token_count} | Caracteres={len(chunk)}")
        print(f"    Preview: {repr(chunk[:100])}...")
        
    print(f"... e mais {len(chunks)-3} chunks.")

if __name__ == "__main__":
    main()
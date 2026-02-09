import os
from pypdf import PdfReader

# ==========================================
# 📄 01. Extração de Texto "Ingênua" (pypdf)
# ==========================================
#
# O PRIMEIRO passo de um RAG é ler o documento.
# Bibliotecas como pypdf, pdfminer ou PyMuPDF (fitz) extraem o texto "cru".
#
# ✅ Vantagens:
# - Muito rápido
# - Roda local (CPU)
# - Gratuito
#
# ❌ Desvantagens:
# - Perde layout (tabelas viram bagunça)
# - Mistura cabeçalho e rodapé no meio do texto
# - Não entende multicolunas direito
#
# Instale: pip install pypdf


def main():
    pdf_path = "Understanding_Climate_Change.pdf"
    
    # Verifica se o arquivo existe no diretório atual
    if not os.path.exists(pdf_path):
        # Tenta achar no diretório relativo caso esteja rodando da raiz
        pdf_path = os.path.join("02-rag", "02-ingestion-pipeline", "Understanding_Climate_Change.pdf")
        
    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo 'Understanding_Climate_Change.pdf' não encontrado.")
        print("Certifique-se de que o arquivo está na pasta '02-rag/02-ingestion-pipeline/'.")
        return

    print(f"--- Lendo {pdf_path} com pypdf ---")
    
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        
        # Limitando a 3 páginas para não poluir o terminal demais no exemplo
        print(f"Total de páginas: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"\n--- Página {i+1} ---")
            print(text[:500] + "..." if len(text) > 500 else text) # Preview
            full_text += text + "\n"
            
        print("\n--- Análise ---")
        print("Note como o texto sai 'chapado'.")
        print("Títulos, tabelas e rodapés se misturam ao corpo do texto.")
        print("Para RAG simples, isso serve. Para documentos complexos, precisamos de Layout Parsing.")
        
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")

if __name__ == "__main__":
    main()

import os
from docling.document_converter import DocumentConverter

# ==========================================
# 📄 02. Layout Parsing Avançado (Docling / Unstructured)
# ==========================================
#
# Em documentos complexos (contratos, papers, relatórios financeiros),
# a posição do texto importa tanto quanto o conteúdo.
#
# "Layout Parsing" usa modelos de visão (OCR + Object Detection) para entender:
# - Que isso é um Título (H1)
# - Que aquilo é uma Tabela (e preserva colunas)
# - Que isso é um Gráfico (e descreve o gráfico)
#
# Ferramentas modernas:
# 1. Unstructured.io (Standard da indústria)
# 2. Docling (IBM - Novo e muito poderoso para tabelas)
# 3. LlamaParse (LlamaIndex - Pago/Cloud)
#
# Instale: pip install docling (Cuidado: é pesado!)


def main():
    pdf_path = "Understanding_Climate_Change.pdf"
    
    # Verifica caminhos
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join("02-rag", "02-ingestion-pipeline", "Understanding_Climate_Change.pdf")

    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo {pdf_path} não encontrado.")
        return

    print(f"--- Processando {pdf_path} com Docling (Conceitual/Exemplo) ---")

    
    
    # O conversor do Docling é inteligente. Ele usa modelos de visão
    # para segmentar a página.
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    
    # O resultado é um documento estruturado, não apenas string.
    # Podemos exportar para Markdown (que preserva a hierarquia # Títulos)
    markdown_output = result.document.export_to_markdown()

    print("\n--- Resultado (Markdown Estruturado) ---")
    print(markdown_output)
    

if __name__ == "__main__":
    main()

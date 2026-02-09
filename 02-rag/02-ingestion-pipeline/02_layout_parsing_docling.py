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
    
    print("\n--- Por que isso é melhor para RAG? ---")
    print("1. O Markdown preserva os headers (#, ##). Isso ajuda no 'MarkdownChunker'.")
    print("2. Tabelas são convertidas para formato Markdown (| Col | Col |), mantendo a relação de dados.")
    print("3. O Chunking semântico funciona muito melhor quando sabe onde começa e termina uma seção.")


    
    print("\n--- Simulação do Output (baseado no PDF) ---")
    print("# Understanding Climate Change\n")
    print("Climate change refers to significant changes in global temperature and weather patterns.\n")
    print("## Causes of Climate Change\n")
    print("The primary cause is the **Greenhouse Effect**.\n")
    print("| Gas | Source | GWP (Global Warming Potential) |")
    print("|---|---|---|")
    print("| CO2 | Fossil Fuels | 1 |")
    print("| Methane | Agriculture | 28 |\n")
    print("> Figure 1: Global Temperature Anomaly (1880-2020)\n")

if __name__ == "__main__":
    main()

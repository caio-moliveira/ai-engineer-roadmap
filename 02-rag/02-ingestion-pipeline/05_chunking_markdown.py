from langchain_text_splitters import MarkdownHeaderTextSplitter

# ==========================================
# 📑 05. Markdown Header Splitter (Semântico)
# ==========================================
#
# Para documentos estruturados (como este código ou READMEs),
# a melhor estratégia é cortar por seções lógicas (# Título, ## Subtítulo).
#
# O MarkdownHeaderTextSplitter preserva a hierarquia, mantendo o contexto.
# Ex: Um chunk "Instalação" saberá que pertence ao Título "Guia do Usuário".


def main():
    # Simulação: Como se tivéssemos passado o Understanding_Climate_Change.pdf pelo Docling/Unstructured
    # e obtido este Markdown.
    markdown_document = """
# Understanding Climate Change

## Introduction
Climate change refers to long-term shifts in temperatures and weather patterns. These shifts may be natural, but since the 1800s, human activities have been the main driver of climate change, primarily due to the burning of fossil fuels (like coal, oil, and gas) which produces heat-trapping gases.

## Causes of Climate Change

### Greenhouse Gases
The main driver of climate change is the greenhouse effect. Some gases in the Earth's atmosphere act a bit like the glass in a greenhouse, trapping the sun's heat and stopping it from leaking back into space.
Many of these gases occur naturally, but human activity is increasing the concentrations of some of them in the atmosphere, in particular:
* Carbon dioxide (CO2)
* Methane
* Nitrous oxide
* Fluorinated gases

### Deforestation
Trees regulate the climate by absorbing CO2 from the atmosphere. When they are cut down, that beneficial effect is lost and the carbon stored in the trees is released into the atmosphere, adding to the greenhouse effect.

## Effects of Climate Change

### Hotter Temperatures
As greenhouse gas concentrations rise, so does the global surface temperature. The last decade, 2011-2020, is the warmest on record. Since the 1980s, each decade has been warmer than the previous one.

### More Severe Storms
Destructive storms have become more intense and more frequent in many regions. As temperatures rise, more moisture evaporates, which exacerbates extreme rainfall and flooding, causing more destructive storms.
"""
    
    print("--- Documento Markdown (Simulado do PDF) ---")
    print(markdown_document[:200] + "...")
    
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    chunks = splitter.split_text(markdown_document)
    
    print(f"\n--- Chunks Gerados ({len(chunks)}) ---")
    for chunk in chunks:
        # O metadata guarda o contexto hierárquico!
        print(f"Content: {chunk.page_content}")
        print(f"Metadata: {chunk.metadata}")
        print("-" * 20)

if __name__ == "__main__":
    main()

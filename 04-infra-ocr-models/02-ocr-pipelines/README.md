# 🏭 Módulo 7: Frameworks e Pipelines de OCR

> **Goal:** Construir uma fábrica de processamento de documentos.  
> **Status:** Mão na massa.

## 1. Ferramentas (O Menu)

| Ferramenta | Custo | Qualidade | Uso |
|:---|:---|:---|:---|
| **Tesseract** | Zero | Baixa | Textos simples, limpos, linha única. |
| **Unstructured.io** | Médio | Alta | Melhor biblioteca Open Source para pipelines híbridos. |
| **Azure AI Doc Intel** | Alto | Muito Alta | Tabelas complexas, formulários bancários. |
| **GPT-4o Vision** | Altíssimo | Estado da Arte | Documentos manuscritos, gráficos, slides. |

## 2. O Pipeline Híbrido (Padrão Ouro)
Não use GPT-4o para tudo (caro demais). Não use Tesseract para tudo (ruim demais).
**Use Routing:**

1.  **Classificador Leve:** O documento é texto digital ou imagem escaneada?
    - Se digital: Use `pypdf` (Zero custo).
    - Se imagem: Avalie densidade.
2.  **Tabelas:** Detectou tabela? Mande a crop da tabela para GPT-4o converter em Markdown.
3.  **Texto:** Use OCR padrão (Tesseract/PaddleOCR) para o corpo do texto.
4.  **Merge:** Junte o Markdown da tabela com o texto do OCR.

## 3. Armazenamento
- Guarde o **Raw Text** (para busca puramente lexical).
- Guarde o **Structured JSON** (para extração de entidades).
- Guarde o **Markdown** (para chunking e RAG).

## 🧠 Mental Model: "ETL de Documentos"
Trate OCR como um pipeline de ETL (Extract, Transform, Load).
Documento -> (OCR) -> Texto Sujo -> (LLM Cleaning) -> Texto Limpo -> Vector DB.

## ⏭️ Próximo Passo
Como colocar isso em produção sem travar?
Vá para **[Módulo 8: Document Intelligence em Produção](../08-document-intelligence)**.

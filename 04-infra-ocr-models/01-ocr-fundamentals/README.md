# 📄 Módulo 6: Fundamentos de OCR (A Realidade)

> **Goal:** Transformar pixels em conhecimento.  
> **Status:** A parte mais frustrante da IA.

## 1. A Ilusão do "Extract Text"
Você acha que é só rodar `pdf_to_text()`.
A realidade:
- **Layouts Complexos:** Colunas duplas que se misturam.
- **Tabelas:** Linhas invisíveis, células mescladas.
- **Artefatos:** Marcas de scanner, riscos, café derramado.
- **Rotação:** Páginas de cabeça para baixo.

## 2. Taxonomia de OCR
1.  **OCR Clássico (Tesseract):** Lê caractere por caractere. Ignora layout. Resultado: "Sopa de letrinhas".
2.  **Layout-Aware (Azure DI / AWS Textract):** Entende caixas, tabelas e formulários.
3.  **Vision LLMs (GPT-4o):** "Vê" a página como um humano. Entende até gráficos.

## 3. Métricas de Qualidade
- **CER (Character Error Rate):** Útil para placas de carro. Inútil para RAG.
- **Semantic Reach:** "O RAG conseguiu responder a pergunta com esse texto extraído?" (A única métrica que importa).

## 🧠 Mental Model: "PDFs são Vetores Pintados"
Um PDF não tem estrutura lógica (como HTML). Ele tem instruções de pintura ("Desenhe 'A' na posição 10,10").
OCR é o processo de engenharia reversa dessa pintura para tentar adivinhar a estrutura lógica original.

## ⏭️ Próximo Passo
Quais ferramentas usar?
Vá para **[Módulo 7: Frameworks e Pipelines de OCR](../07-ocr-pipelines)**.

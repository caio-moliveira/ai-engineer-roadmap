# 📥 Módulo 02: Ingestion Pipeline

> **Goal:** "Garbage In, Garbage Out". Se o seu RAG falha, 80% das vezes a culpa é do Ingestion.
> 
> **Foco:** Transformar documentos não estruturados (PDF, HTML) em pedaços de texto semanticamente úteis (Chunks).

---

## 🛠️ O Pipeline de Ingestão

Antes de embeddar e salvar no Qdrant, precisamos preparar os dados.

1.  **Parsing (Extração):** Tira o texto do arquivo.
2.  **Chunking (Divisão):** Quebra o texto em pedaços que cabem no contexto do LLM.

### 📂 Scripts deste Módulo

| Arquivo | Tópico | Descrição |
| :--- | :--- | :--- |
| **[01_text_extraction_pypdf.py](./01_text_extraction_pypdf.py)** | **Raw Text** | Extração simples e rápida com `pypdf`. Perde tabelas e layout. |
| **[02_layout_parsing_docling.py](./02_layout_parsing_docling.py)** | **Layout Aware** | Extração inteligente com `Docling` (preserva tabelas e headers). |
| **[03_chunking_recursive.py](./03_chunking_recursive.py)** | **Recursive** | O chunker padrão do LangChain. Bom para textos gerais. |
| **[04_chunking_token.py](./04_chunking_token.py)** | **Token Limit** | Garante que o chunk respeita o limite do modelo (ex: OpenAI `tiktoken`). |
| **[05_chunking_markdown.py](./05_chunking_markdown.py)** | **Structure** | Usa headers Markdown (#, ##) como fronteira semântica. O melhor para docs técnicos. |

---

## 🧠 Parsing: Texto "Burro" vs Layout "Inteligente"

*   **Pypdf:** Só lê strings. Se tiver uma tabela com duas colunas, ele pode ler a linha 1 da col 1 e depois a linha 1 da col 2, misturando tudo.
*   **Docling / Unstructured:** Entendem que aquilo é uma tabela. Convertem para Markdown ou JSON estruturado, preservando a relação entre os dados.

> **Regra de Ouro:** Para contratos, relatórios financeiros e papers científicos, use Layout Parsing. Para e-mails ou textos simples, use extração básica.

---

## ✂️ Chunking Strategies

Não existe "tamanho ideal de chunk". Existe o tamanho certo para sua pergunta.

1.  **Chunks Pequenos (128-256 tokens):** Ótimos para perguntas precisas ("Qual a data do contrato?"). Perdem contexto amplo.
2.  **Chunks Grandes (512-1024 tokens):** Ótimos para resumo ou perguntas gerais ("Sobre o que é o documento?"). Custa mais e pode confundir a busca (muito ruído).
3.  **Semantic Chunking:** Quebra onde o assunto muda (avançado).
4.  **Markdown/Structure Chunking:** Quebra por seção lógica (Introdução, Conclusão).

---
## Explicação do Módulo 2

> **Goal:** Lixo entra, Lixo sai. Domine a arte de limpar dados.  
> **Status:** A parte mais subestimada da IA.

## 1. O Documento é o Inimigo
PDFs são feitos para impressão, não para leitura.
- Eles têm cabeçalhos, rodapés, colunas múltiplas e imagens.
- Se você extrair texto cegamente, recebe: `Cabeçalho Pag 1 Conteúdo Cabeçalho Pag 2`.
- Isso destrói o significado semântico.

### Estratégias de Parsing
1.  **Text Extraction (pypdf):** Rápido, grátis, perde tabelas/layout. Use para contratos simples.
2.  **OCR (Tesseract):** Essencial para docs escaneados. Lento.
3.  **Vision Models (GPT-4o / Claude Vision):** Envia a imagem da página. Caro, mas 99% preciso.
4.  **Layout Parsing (Unstructured.io / Microsoft Azure DI):** Detecta "Título", "Tabela", "Barra Lateral". A escolha profissional.

## 2. Filosofia de Chunking
Você não pode enviar um livro de 100 páginas para o modelo de embedding (contexto limitado). Você deve "fatiar" (chunk). [Text splitter Langchain Docs](https://docs.langchain.com/oss/python/integrations/splitters)

### Estratégia A: Fixed Size (O jeito "ingênuo")
- Dividir a cada 500 caracteres.
- **Problema:** Corta frases no meio. Quebra contexto.

### Estratégia B: Recursive Character (Padrão LangChain)
- Divide por Parágrafos (`\n\n`) -> Frases (`.`) -> Palavras (` `).
- **Veredito:** Bom baseline.

### Estratégia C: Semantic Chunking (Avançado)
- Usa um modelo de embedding para escanear o documento.
- Inicia um novo chunk quando o *tópico muda* (similaridade de cosseno cai).
- **Veredito:** Alta qualidade, indexação mais lenta.

### Estratégia D: Hierarchical Indexing (Parent-Child)
- **Store:** A página inteira (Pai).
- **Search:** Pequenos chunks de 200 chars (Filhos).
- **Retrieval:** Se um filho é encontrado, retorne o *Pai*.
- **Por que:** Chunks pequenos casam melhor com a busca. Chunks grandes dão melhor contexto pro LLM.

## 3. Extração de Metadados
**Se você não extrai metadados, sua busca é burra.**

Exemplo: "Qual foi a receita em 2023?"
- **Sem Metadados:** Busca em todos os docs "receita". Retorna 2021, 2022, 2024.
- **Com Metadados:** Filtra `year == 2023`.

**Como extrair?**
- Use um LLM barato (GPT-4o-mini) durante a ingestão para extrair JSON:
  ```json
  {
    "title": "Relatório Q3",
    "year": 2023,
    "department": "Vendas",
    "summary": "Receita subiu 20%"
  }
  ```

## 4. Arquitetura Real de Pipeline
Não escreva um script. Construa um pipeline.

1.  **Trigger:** Usuário sobe arquivo.
2.  **Queue:** Arquivo vai para Redis/SQS.
3.  **Worker:**
    - Detecta tipo (MIME).
    - Parse (Unstructured).
    - Extrai Metadados (LLM).
    - Chunk (Recursive).
    - Embed (OpenAI).
    - Upsert (Qdrant).
4.  **Status:** Notifica Usuário "Arquivo Pronto".

## 🧠 Mental Model: "Fragmentação"
Se você picotar um romance de mistério aleatoriamente, pode pegar um pedaço que diz:
*"Ele fez isso."*
Quem é "Ele"? O contexto foi perdido.
**Overlap** ajuda (manter 50 chars do anterior), mas **Parent-Child** é a correção real.

## ⏭️ Próximo Passo
Como transformamos texto em matemática?
Vá para **[Módulo 3: Embeddings](../03-embeddings)**.

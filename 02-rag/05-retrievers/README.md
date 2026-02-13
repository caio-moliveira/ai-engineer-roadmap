# Módulo 05: Retrievers (Recuperadores) e Estratégias de Busca

Este módulo é dedicado à engenharia de **Sistemas de Recuperação (Retrieval Systems)**, o componente crítico fundamenta arquiteturas RAG (Retrieval-Augmented Generation).

Em um pipeline RAG, a qualidade da resposta do LLM é diretamente proporcional à relevância dos documentos recuperados ("Garbage In, Garbage Out"). Se o Retriever falhar em trazer o contexto correto, nenhuma engenharia de prompt salvará a resposta final.

Este diretório implementa padrões de projeto avançados para lidar com diferentes desafios de indexação e busca, utilizando os frameworks **LangChain** e **LlamaIndex**.

## 🧠 Conceitos Fundamentais de Recuperação

A recuperação de informação moderna vai muito além de simples busca por palavras-chave.

1.  **Dense Retrieval (Busca Vetorial)**:
    -   Utiliza **Embeddings** (vetores densos de alta dimensão) para representar o significado semântico do texto.
    -   Calcula a similaridade (cosseno, produto escalar, distância euclidiana) entre a query do usuário e os documentos.
    -   *Vantagem*: Entende sinônimos e contexto ("carro" ≈ "automóvel").
    -   *Desvantagem*: Pode falhar em matches exatos de IDs, acrônimos ou termos muito específicos.

2.  **Sparse Retrieval (Busca Lexical / Keyword)**:
    -   Utiliza algoritmos clássicos como **BM25** ou **TF-IDF**.
    -   Foca na frequência exata de termos nos documentos.
    -   *Vantagem*: Extremamente preciso para nomes próprios, códigos técnicos e queries específicas.
    -   *Desvantagem*: Não entende semântica; "banco" (assento) e "banco" (financeiro) são tratados apenas como a string "banco".

3.  **Hybrid Search (Busca Híbrida)**:
    -   Combina Scores de Dense + Sparse (geralmente com um algoritmo de re-ranking como RRF - Reciprocal Rank Fusion) para obter o "melhor dos dois mundos".

4.  **Structured Retrieval (Self-Querying)**:
    -   Utiliza um LLM para converter uma pergunta em linguagem natural em uma query estruturada (SQL-like).
    -   Permite filtragem precisa por metadados (ex: `date > 2023 AND status == 'active'`) antes ou durante a busca vetorial.

5.  **Hierarchical / Recursive Retrieval**:
    -   Estratégia onde se indexa resumos de documentos, e ao recuperar um resumo relevante, o sistema expande para buscar nos chunks detalhados associados àquele resumo. Implementado aqui através do `TreeIndex` e `SummaryIndex` do LlamaIndex.

---


## 📂 Estrutura dos Arquivos

### 🛠️ Utilitários

- **`utils.py`**:
  - Script central que gerencia carrega o PDF `Understanding_Climate_Change.pdf`.
  - Conecta ao **Qdrant** (rodando localmente na porta 6333).
  - Indexa os dados na collection `climate_change_collection` para uso nos exemplos com LangChain.

### 🦜 Exemplos com LangChain

1.  **`01_basic_vector_retriever.py`**
    -   **Conceito**: Recuperação Vetorial (Vector Search / Dense Retrieval).
    -   **O que faz**: Busca chunks semanticamente similares à pergunta do usuário armazenados no Qdrant.
    -   **Destaque**: Compara `similarity_search` (retorno direto de lista) vs `as_retriever` (interface Runnable para Chains).
    -   **Docs**: [Vector Stores (LangChain)](https://docs.langchain.com/oss/python/langchain/knowledge-base)

2.  **`02_keyword_retriever_langchain.py`**
    -   **Conceito**: Recuperação por Palavras-Chave (Keyword Search / Sparse Retrieval).
    -   **O que faz**: Usa o algoritmo **BM25** para encontrar documentos baseados na frequência exata de termos (semântica léxica).
    -   **Ideal para**: Termos técnicos específicos, nomes próprios ou quando a busca semântica falha em precisão exata.
    -   **Docs**: [BM25 Retriever](https://python.langchain.com/docs/integrations/retrievers/bm25)

3.  **`03_self_query_retriever_langchain.py`**
    -   **Conceito**: Self-Querying (Busca Estruturada).
    -   **O que faz**: Usa um LLM para transformar a pergunta em linguagem natural do usuário em uma query estruturada (com filtros de metadados).
    -   **Exemplo**: "Súmulas de 2014" -> Filtra `ano == 2014`.
    -   **Nota**: Este exemplo usa uma configuração específica de metadados (como `num_sumula`, `ano`, etc.), servindo como template avançado.
    -   **Docs**: [Self-querying Retrievers](https://python.langchain.com/docs/modules/data_connection/retrievers/self_query/)

### 🦙 Exemplos com LlamaIndex

4.  **`04_summary_retrieval_llamaindex.py`**
    -   **Conceito**: Summary Index (List Index).
    -   **O que faz**: Armazena nós como uma lista sequencial.
    -   **Modo de Retenção**: `retriever_mode="llm"`. O LLM verifica cada nó (ou um subconjunto) para decidir se é relevante.
    -   **Uso**: Perguntas que exigem "ler tudo" ou sumarização global (alto custo computacional).
    -   **Docs**: [Summary Index](https://developers.llamaindex.ai/python/examples/index_structs/doc_summary/docsummary/)

5.  **`05_vector_retrieval_llamaindex.py`**
    -   **Conceito**: Vector Store Index.
    -   **O que faz**: Equivalente ao exemplo 01 do LangChain, mas usando a abstração do LlamaIndex. Cria embeddings e busca por similaridade de cosseno.
    -   **Docs**: [VectorStoreIndex](https://docs.llamaindex.ai/en/stable/module_guides/indexing/vector_store_index/)

6.  **`06_tree_retrieval_llamaindex.py`**
    -   **Conceito**: Tree Index (Hierarchical).
    -   **O que faz**: Constrói uma árvore de resumos. A raiz resume os filhos, permitindo navegar do geral para o específico.
    -   **Modo**: `select_leaf_embedding`. Usa embeddings para percorrer a árvore até os nós folha mais relevantes.
    -   **Docs**: [Tree Index](https://developers.llamaindex.ai/python/examples/response_synthesizers/tree_summarize/)


### Rodando um script

```bash
# Exemplo LangChain
python 02-rag/05-retrievers/01_basic_vector_retriever.py

# Exemplo LlamaIndex
python 02-rag/05-retrievers/05_vector_retrieval_llamaindex.py
```

## 📚 Referências Oficiais

- **LangChain Retrievers**: [https://python.langchain.com/docs/modules/data_connection/retrievers/](https://python.langchain.com/docs/modules/data_connection/retrievers/)
- **LlamaIndex Indexing & Retrieval**: [https://docs.llamaindex.ai/en/stable/module_guides/indexing/](https://docs.llamaindex.ai/en/stable/module_guides/indexing/)

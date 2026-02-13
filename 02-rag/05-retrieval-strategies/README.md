# 🔎 Módulo 5: Estratégias de Retrieval (Crítico)

> **Goal:** Achar a agulha no palheiro.  
> **Status:** A diferença entre uma Demo e um Produto.

## 1. A Limitação da Busca Semântica
Dense Retrieval (Vetores) falha em matches exatos.
- **Query:** "Código de erro 0x5f3"
- **Busca Vetorial:** "Falha de sistema", "Bug report". (Perde o código específico).
- **Keyword Search (BM25):** "0x5f3". (Match perfeito).

### Solução: Hybrid Search
Combine os scores: `Score = 0.7 * Vetor + 0.3 * BM25`.
Qdrant e Weaviate suportam isso nativamente.

## 2. Reranking (A Bala de Prata)
Busca vetorial é "Rápida mas bruta". Retorna os top 50 candidatos.
Reranking é "Lento mas preciso". Reordena esses 50 candidatos usando um Cross-Encoder (BERT).

**Processo:**
1. Recupere 50 docs (Vetores).
2. Passe Query + 50 Docs para API Cohere Rerank.
3. Pegue os top 5.

**Resultado:** Aumento massivo no MRR (Mean Reciprocal Rank).

## 3. Query Transformation
Queries de usuários são preguiçosas. "Não funcionou."
O sistema de Retrieval precisa de "contexto".

### Multi-Query Retrieval
- **LLM Rewrite:** Transforme "Não funcionou" em:
  1. "Troubleshooting falha de login"
  2. "Erro de conexão crash sistema"
  3. "Correção timeout autenticação"
- **Execução:** Rode todas as 3 buscas. Deduplique os resultados.

### Decomposition
- **Query:** "Compare a receita da Tesla vs Ford em 2023."
- **Decomposed:**
  1. "Qual foi a receita da Tesla 2023?"
  2. "Qual foi a receita da Ford 2023?"
- **Resposta:** Combine os contextos.

## 4. Contextual Retrieval (Novo em 2025)
**Problema:** Um chunk diz "A empresa caiu."
**Contexto:** Qual empresa? Quando?
**Fix:** Adicione contexto durante a indexação.
- Use um LLM para resumir o documento e adicione o resumo a *cada* chunk antes de embeddar.
- Chunk vira: "[Relatório Apple Q3] A empresa caiu."

## 🧠 Mental Model: "O Funil"
Retrieval é um funil.
1.  **Database:** 1,000,000 docs.
2.  **Filter:** 10,000 docs (Metadata: year=2024).
3.  **Vector Search:** 100 docs (Aproximado).
4.  **Reranker:** 10 docs (Preciso).
5.  **LLM:** 1 resposta.

## ⚠️ Erros Comuns
- **k=4 é padrão:** Por quê? A maioria dos tutoriais usa top_k=4. Tente k=20 e Rerank.
- **Ignorar Keywords:** RAG sem BM25 vai falhar em SKUs, Ids e siglas.


### 3. Retrieval Augmented Generation

With RAG, LLMs retrieve contextual documents from a database to improve the accuracy of their answers. RAG is a popular way of augmenting the model's knowledge without any fine-tuning.

* **Orchestrators**: Orchestrators like [LangChain](https://python.langchain.com/docs/get_started/introduction) and [LlamaIndex](https://docs.llamaindex.ai/en/stable/) are popular frameworks to connect your LLMs with tools and databases. The Model Context Protocol (MCP) introduces a new standard to pass data and context to models across providers.
* **Retrievers**: Query rewriters and generative retrievers like CoRAG and HyDE enhance search by transforming user queries. Multi-vector and hybrid retrieval methods combine embeddings with keyword signals to improve recall and precision.
* **Memory**: To remember previous instructions and answers, LLMs and chatbots like ChatGPT add this history to their context window. This buffer can be improved with summarization (e.g., using a smaller LLM), a vector store + RAG, etc.
* **Evaluation**: We need to evaluate both the document retrieval (context precision and recall) and the generation stages (faithfulness and answer relevancy). It can be simplified with tools [Ragas](https://github.com/explodinggradients/ragas/tree/main) and [DeepEval](https://github.com/confident-ai/deepeval) (assessing quality).

📚 **References**:
* [Llamaindex - High-level concepts](https://docs.llamaindex.ai/en/stable/getting_started/concepts.html): Main concepts to know when building RAG pipelines.
* [Model Context Protocol](https://modelcontextprotocol.io/introduction): Introduction to MCP with motivate, architecture, and quick starts.
* [Pinecone - Retrieval Augmentation](https://www.pinecone.io/learn/series/langchain/langchain-retrieval-augmentation/): Overview of the retrieval augmentation process. 
* [LangChain - Q&A with RAG](https://python.langchain.com/docs/tutorials/rag/): Step-by-step tutorial to build a typical RAG pipeline.
* [LangChain - Memory types](https://python.langchain.com/docs/how_to/chatbots_memory/): List of different types of memories with relevant usage.
* [RAG pipeline - Metrics](https://docs.ragas.io/en/stable/concepts/metrics/index.html): Overview of the main metrics used to evaluate RAG pipelines.

## ⏭️ Próximo Passo
Vamos juntar isso com código.
Vá para **[Módulo 6: LangChain v1](../06-langchain-v1)**.

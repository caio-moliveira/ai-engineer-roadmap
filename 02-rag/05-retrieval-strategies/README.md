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

## ⏭️ Próximo Passo
Vamos juntar isso com código.
Vá para **[Módulo 6: LangChain v1](../06-langchain-v1)**.

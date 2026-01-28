# 🔹 Bloco 2: Sistemas RAG (Retrieval-Augmented Generation)

> **Objetivo:** Conectar LLMs aos seus dados privados.  
> **Status:** A arquitetura mais comum em produção hoje.

## 🛑 Pare. Leia isto.
RAG não é apenas "jogar PDF no Vector DB".
RAG em produção exige:
1.  **Estratégia de Chunking:** Como quebrar o texto sem perder o sentido?
2.  **Reranking:** Como filtrar os 100 documentos retornados para os 5 melhores?
3.  **Avaliação:** Como saber se a resposta está certa sem ler tudo?

Aqui vamos além do tutorial básico de "Chat with PDF".

---

## 📚 Ementa do Módulo

### [Módulo 1: Fundamentos de RAG e Modelos Mentais](./01-rag-fundamentals)
- **Definição:** RAG = Busca (Retrieval) + Geração (Generation).
- **Por que RAG?** Superando alucinações e data de corte (knowledge cutoff).
- **Arquitetura Padrão:** Ingestion -> Store -> Retrieve -> Generate.

### [Módulo 2: Ingestão de Dados e Pipelines](./02-ingestion-pipeline)
- **ETL para IA:** Extrair texto limpo de PDFs, HTML e Markdown.
- **Chunking:** Estratégias (Fixed-size, Recursive, Semantic) e seus impactos.
- **Metadados:** Por que metadados são mais importantes que o texto em si.

### [Módulo 3: Embeddings (Visão Moderna)](./03-embeddings)
- **Conceito:** Transformando texto em vetores numéricos.
- **Modelos:** OpenAI vs Open Source (bge-m3, e5).
- **Multilingual:** Lidando com português e inglês misturados.

### [Módulo 4: Vetor Databases (Vector DBs)](./04-vector-dbs)
- **Opções:** Qdrant (Rust/Performance) vs pgvector (Simplicidade/Postgres).
- **Indexação:** HNSW explicado para humanos.
- **Tradeoffs:** Memória vs Disco vs Velocidade.

### [Módulo 5: Estratégias de Retrieval (Crítico)](./05-retrieval-strategies)
- **Hybrid Search:** Misturando busca semântica (Vetores) com busca exata (BM25/Keywords).
- **Reranking:** O segredo para dobrar a precisão. (Cohere Rerank / Cross Encoders).
- **Query Expansion:** Melhorando a pergunta do usuário antes de buscar.

### [Módulo 6: LangChain v1 (LCEL)](./06-langchain-v1)
- **Modern LangChain:** Esqueça `RetrievalQAChain`. Use LCEL (LangChain Expression Language).
- **Composabilidade:** Pipelines declarativos e transparentes.
- **Runnables:** O protocolo padrão para invocar cadeias.

### [Módulo 7: LangGraph (Orquestração RAG)](./07-langgraph)
- **Loops:** Quando a busca linear falha, precisamos de loops (agentes).
- **Corrective RAG:** Se a busca for ruim, pesquise na web. (Flow condicional).
- **Estado:** Mantendo memória durante a execução do grafo.

### [Módulo 8: LlamaIndex](./08-llamaindex)
- **Foco em Dados:** Quando usar LlamaIndex em vez de LangChain.
- **Advanced Indexing:** Hierarchical Indices, Document Summary Index.
- **Query Engine:** Abstrações poderosas para dados complexos.

### [Módulo 9: Avaliação e Observabilidade](./09-evaluation)
- **Ragas:** Framework de avaliação automática (Faithfulness, Answer Relevancy).
- **Tracing:** Visualizando cada passo com Langsmith/Langfuse.
- **Golden Datasets:** Criando um conjunto de testes confiável.

### [Módulo 10: RAG em Produção](./10-rag-production)
- **Otimização:** Cache Semântico, Streaming, Latência.
- **Segurança:** Prompt Injection em RAG.
- **Custos:** Estimando tokens de input/output em escala.

---

## 🛠️ Stack RAG (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Orquestração** | LangChain / LangGraph | Flexibilidade e ecossistema. |
| **Vector DB** | Qdrant / pgvector | Performance e facilidade de uso. |
| **Embeddings** | OpenAI (text-3) / Cohere | Qualidade e facilidade. |
| **LLM** | GPT-4o / Claude 3.5 Sonnet | Raciocínio superior para síntese. |
| **Eval** | Ragas | Padrão de mercado para métricas RAG. |

## 🧠 Mudanças Mentais Necessárias
- **Busca Semântica não é Mágica:** Ela falha em "termos exatos" (IDs, SKUs). Por isso usamos Hybrid Search.
- **Garbage In, Garbage Out:** Se seu chunking cortar a frase no meio, o LLM não vai entender. Invista tempo na Ingestão.

## 🚀 Como começar
Vá para **[Módulo 1: Fundamentos de RAG](./01-rag-fundamentals)**.

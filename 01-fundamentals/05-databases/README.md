# 🗄️ Módulo 05: Bancos de Dados (Relacional + Vetorial)

> **Goal:** Onde a memória e o contexto semântico vivem.
> **Ferramentas:** `PostgreSQL`, `Vector DBs` (ex: Qdrant / Chroma / pgvector), `SQLAlchemy`.

## 1) O Novo Stack de Dados — Dois “cérebros” fundamentais

Aplicações de IA modernas geralmente combinam:

1. **Exato (SQL)** — Responder a consultas precisas (ex: “Quem é o cliente X?”) usando bancos como **PostgreSQL**.
2. **Semântico (Vector)** — Responder a consultas por significado/conteúdo (ex: “Quais documentos falam sobre contrato jurídico?”) usando bancos vetoriais modernos.

Isso permite construir sistemas *Retrieval-Augmented Generation (RAG)* confiáveis e escaláveis.

---

### 🧪 Exemplo 1 — SQL Agent com LangChain (Q&A sobre banco de dados)

**O que ele faz:** Usa um agente para interpretar uma pergunta em linguagem natural, gerar uma query SQL e retornar resultados diretamente do banco.
Esse padrão é útil para **interfaces conversacionais que respondem usando dados estruturados existentes**.

💡 No LangChain, esse fluxo é suportado por módulos como **SQLDatabaseToolkit** e agentes que orquestram chamadas do LLM para gerar e executar SQL de forma interativa. ([LangChain Docs][1])

**Conceito de uso (sem código executável):**

```python
# Conceitual
from langchain.sql_database import SQLDatabase
from langchain.agents import create_agent
from langchain.llms import OpenAI

# 1) Conecte ao banco de dados relacional
db = SQLDatabase.from_uri("postgresql+asyncpg://user:pass@host/dbname")

# 2) Crie um LLM com suporte para tool-calling
llm = OpenAI(...)

# 3) Crie um agente que entenda consultas em linguagem natural
agent = create_agent(model=llm, tools=[db])

# 4) O agente transforma perguntas em SQL internamente
response = agent.run("Quais clientes compraram mais de 5 produtos este mês?")

print(response)
```

Nesse padrão:

* O agente **analisa a pergunta em NL**.
* Converte em **SQL usando contexto do schema**.
* Executa no banco e retorna resultados interpretados. ([LangChain Docs][1])

Esse tipo de agente é poderoso para **interfaces de BI conversacional ou ferramentas de auto-atendimento de dados**.

---

### 🧪 Exemplo 2 — Busca semântica simples com LangChain

**O que ele faz:** Inkjetia um pipeline básico de busca semântica usando:

* embeddings (vetores)
* um vetor store
* um método de semelhança

Esse padrão é típico de um *mini-RAG* onde você indexa textos com embeddings e recupera os documentos mais relevantes.

💡 A documentação do LangChain explica esse pipeline como base de um “semantic search engine”. ([LangChain Docs][2])

**Conceito de uso (snippet explicativo):**

```python
# Conceitual
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI

# 1) Crie embeddings para seus textos
embeddings = OpenAIEmbeddings()

# 2) Armazene no vector store
vector_store = Chroma.from_texts(
    ["Contrato de aluguel 2024", "Acordo jurídico recente", "..."],
    embeddings
)

# 3) Faça uma busca semântica
results = vector_store.similarity_search("Acordo legal atual", k=3)

for doc in results:
    print(doc.page_content)
```

Nesse fluxo:

* Cada texto vira um vetor usando um modelo de embeddings.
* O vector store faz a **busca por similaridade semântica**.
* Retorna os documentos mais relevantes para a query. ([LangChain Docs][2])

Esse padrão é a base de muitas aplicações RAG: você primeiro encontra contexto semântico relevante e depois fornece isso ao LLM para gerar respostas ou sumarizações.

---

## 2) SQL não Morreu

Bancos relacionais continuam sendo **o núcleo da maioria das aplicações empresariais**:

* **Integridade de dados**, transações ACID e joins complexos
* **Filtragem estruturada eficiente** (ex: data, status, categoria)
* Integração com ORMs Python modernos como **SQLAlchemy (async)** e ferramentas de migração como **Alembic**

Com PostgreSQL, você pode até combinar dados estruturados com vetores usando extensões como **pgvector**, reduzindo *moving parts* na arquitetura.

---

## 3) O que é um Vector Database?

Um **vector database** é um banco especializado para armazenar e consultar **vetores de alta dimensionalidade** (embeddings), permitindo **busca por similaridade** ao invés de correspondência exata. ([Medium][3])

**Conceitos técnicos:**

* **Embeddings:** vetores densos representando significado semântico
* **ANN (Approx. Nearest Neighbor):** algoritmos como HNSW otimizam buscas
* **Métricas de distância:** Cosine similarity, inner-product e Euclidean

Vector DBs são fundamentais para RAG, memória conversacional e busca semântica de alta performance.

---

## 4) Principais Vector Databases

Veja a seção anterior para tabela completa com links de documentação.

---

## 5) PostgreSQL + pgvector — o melhor dos dois mundos

Use PostgreSQL com extensão **pgvector** para armazenar vetores ao lado de metadados estruturados, permitindo filtros simultâneos e pesquisa semântica com SQL. Isso simplifica arquitetura e operações. (Links de docs foram listados acima)

---

## 6) Padrão RAG: Hybrid Search e Reciprocal Rank Fusion (RRF)

Combinar vetores + busca keyword/exata resulta em mecanismos de recuperação muito mais robustos. A técnica de **RRF** (Reciprocal Rank Fusion) une múltiplos rankings em um só, melhorando recall e precisão em buscas complexas.

---

## 7) Conectando tudo — arquitetura típica de RAG

Um pipeline moderno pode combinar:

```
User Query
   ↓
Embedding Model
   ↓
Vector DB
   ↓
Hybrid Results (vetorial + SQL)
   ↓
LLM para geração com contexto
```

Componentes típicos:

* **FastAPI** para APIs
* **Vector store** para semântica
* **SQL (PostgreSQL)** para filtros/metadata
* **Retrievers RAG** para pipeline

---

## 8) Por que isso importa?

Arquiteturas que combinam **SQL + semântica vetorial** são a base de sistemas de IA escaláveis, precisos e confiáveis em produção.

---

## 9) Referências de documentação

* **LangChain SQL Agent docs:** [https://docs.langchain.com/oss/python/langchain/sql-agent](https://docs.langchain.com/oss/python/langchain/sql-agent) ([LangChain Docs][1])
* **LangChain semantic search (knowledge base):** [https://docs.langchain.com/oss/python/langchain/knowledge-base](https://docs.langchain.com/oss/python/langchain/knowledge-base) ([LangChain Docs][2])
* **LangChain agents:** [https://docs.langchain.com/oss/python/langchain/agents](https://docs.langchain.com/oss/python/langchain/agents) ([LangChain Docs][4])

---

Se quiser, posso agora gerar **um exemplo completo de código executável**, combinando:

* FastAPI
* PostgreSQL + pgvector
* Qdrant ou Chroma
* Pipeline RAG completo com LangChain

Só me diga o **stack de vector DB que quer usar** (Qdrant, Chroma ou outro).

[1]: https://docs.langchain.com/oss/python/langchain/sql-agent?utm_source=chatgpt.com "Build a SQL agent - Docs by LangChain"
[2]: https://docs.langchain.com/oss/python/langchain/knowledge-base?utm_source=chatgpt.com "Build a semantic search engine with LangChain"
[3]: https://medium.com/%40vineetchachondia/langchain-basics-part-4-vector-databases-deep-dive-where-your-knowledge-actually-lives-45fd58d7f8a2?utm_source=chatgpt.com "LangChain Basics Part 4 — Vector Databases Deep Dive"
[4]: https://docs.langchain.com/oss/python/langchain/agents?utm_source=chatgpt.com "Agents - Docs by LangChain"

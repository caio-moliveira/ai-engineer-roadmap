# Módulo 07: Graph RAG (Retrieval-Augmented Generation com Grafos)

Este módulo explora o paradigma de **Graph RAG**, uma evolução do RAG tradicional que combina a busca vetorial (não estruturada) com Grafos de Conhecimento (estruturados) para melhorar a recuperação de contexto complexo.

## 🕸️ O que é Graph RAG?

Enquanto o RAG tradicional trata documentos como pedaços isolados de texto (chunks), o **Graph RAG** entende as **relações** entre esses pedaços.

Imagine que você tem documentos sobre "Mudanças Climáticas".
- **RAG Vetorial**: Busca chunks que falam sobre "efeito estufa".
- **Graph RAG**: Sabe que "efeito estufa" *causa* "aquecimento global" e *é causado por* "emissões de CO2", e pode trazer documentos conectados a esses conceitos, mesmo que não tenham as palavras exatas da busca inicial.

### Principais Vantagens
1.  **Multi-hop Reasoning**: Permite responder perguntas que exigem conectar fatos distantes ("Qual a relação entre o autor do documento A e a empresa mencionada no documento B?").
2.  **Contexto Global**: Entende a estrutura macro do conhecimento, não apenas a similaridade semântica local.
3.  **Redução de Alucinações**: Ancora as respostas em fatos e relações explícitas.

## 📂 Implementações

### 🦜 LangChain: `langchain-graph-retriever`

- **Arquivo**: `01_graph_rag_langchain.py`
- **Conceito**: Traversal RAG.
- **Como funciona**:
    1.  Cria-se um grafo de conexões entre documentos (ex: metadados explícitos, links, ou extração via LLM).
    2.  A busca inicial recupera nós iniciais (seeds).
    3.  O algoritmo expande a busca navegando pelas arestas do grafo (DFS/BFS) para encontrar documentos semanticamente distantes, mas estruturalmente conectados.
- **Lib**: Utiliza a biblioteca `langchain-graph-retriever`.

### 🦙 LlamaIndex: `KnowledgeGraphRAGQueryEngine`

- **Arquivo**: `02_graph_rag_llamaindex.py`
- **Conceito**: Knowledge Graph RAG.
- **Como funciona**:
    1.  Constrói um Grafo de Conhecimento (Triplets: Sujeito -> Predicado -> Objeto) a partir dos seus dados.
    2.  Busca entidades relevantes na query do usuário.
    3.  Recupera o sub-grafo ao redor dessas entidades para dar contexto rico ao LLM.
- **Lib**: Utiliza as abstrações nativas de `PropertyGraphIndex` ou `KnowledgeGraphIndex`.

## 🚀 Como Executar com UV

Este projeto utiliza `uv` para gerenciamento de dependências rápido.

### 1. Instalar Dependências
```bash
uv pip install langchain langchain-community langchain-openai llama-index llama-index-graph-stores-nebula langchain-graph-retriever
```

### 2. Rodar os Exemplos

#### LangChain (Traversal Graph)
```bash
uv run 02-rag/07-graph-rag/01_graph_rag_langchain.py
```

#### LlamaIndex (Knowledge Graph)
```bash
uv run 02-rag/07-graph-rag/02_graph_rag_llamaindex.py
```

## 📚 Referências

- **LangChain Graph RAG**: [https://python.langchain.com/docs/integrations/retrievers/graph_rag/](https://python.langchain.com/docs/integrations/retrievers/graph_rag/)
- **LlamaIndex KG RAG**: [https://developers.llamaindex.ai/python/examples/query_engine/knowledge_graph_rag_query_engine/](https://developers.llamaindex.ai/python/examples/query_engine/knowledge_graph_rag_query_engine/)

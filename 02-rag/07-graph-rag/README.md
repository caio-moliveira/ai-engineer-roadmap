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


#### Parâmetros do `GraphRetriever` (LangChain): `edges`, `strategy` e `transformers`

Abaixo está o trecho principal do exemplo **Traversal Graph RAG** onde configuramos o `GraphRetriever`:

```python
traversal_retriever = GraphRetriever(
    store=vector_store,
    edges=[("related_to", "related_to")],
    strategy=Eager(k=15, start_k=2, max_depth=3),
)
```

##### 1) `edges` (como os documentos viram um grafo) [Link da documentação](https://datastax.github.io/graph-rag/guide/edges/)

`edges` define **como criar ligações (arestas) entre conteúdos** usando campos estruturados — normalmente metadados.  
A documentação do GraphRAG descreve `edges` como a forma de “linkar” conteúdos (ex.: por autores, keywords, citações, IDs), e destaca que as arestas podem ser escolhidas dinamicamente por pergunta. citeturn0view0

**Formato mental (bem prático):** cada tupla `(start_attr, end_attr)` diz *“use o valor do atributo `start_attr` de um documento para encontrar/ligar documentos cujo atributo `end_attr` ‘case’ com esse valor”*. Exemplos clássicos da própria doc incluem:  
- `("keywords", "keywords")` → conecta documentos com *keywords* em comum  
- `("authors", "primary_author")` → conecta por relação “autor → autor principal”  
- `("cites", "$id")` e `("$id", "cites")` → conecta por citações via ID citeturn0view0

No nosso exemplo, usamos `edges=[("related_to", "related_to")]` porque nossos documentos têm `metadata["related_to"]` com IDs/labels que também aparecem em outros docs. Isso cria um grafo navegável a partir dessas conexões.

**Edge Functions (quando o metadado existe, mas precisa de “adaptação”):** se o metadado não está num formato bom para travessia (ex.: lista com informação extra, string mal formatada), você pode definir uma `EdgeFunction` customizada para “extrair” as arestas do jeito certo antes da travessia. citeturn0view0

##### 2) `strategy` (como a travessia escolhe nós/adjacências) [Link da Documentação](https://datastax.github.io/graph-rag/guide/strategies/)

`strategy` define **a política de seleção de nós durante a travessia** — ou seja, como o retriever expande o grafo a partir dos nós iniciais (seeds). citeturn2view0

No GraphRAG, as estratégias são responsáveis por coisas como:
- **Quantos nós iniciais** buscar por similaridade (`start_k`)  
- **Quantos vizinhos por aresta** buscar em cada passo (`adjacent_k`)  
- **Profundidade máxima** de expansão (`max_depth`)  
- **Quantos nós retornar no total** (`select_k` / `k`) citeturn2view0

**No exemplo usamos `Eager(...)`:** é uma estratégia *breadth-first* (camada por camada) que seleciona todos os nós descobertos em cada passo, garantindo “largura” antes de aprofundar. citeturn2view0

**Alternativa útil: `Mmr(...)`:** a estratégia MMR seleciona nós balanceando **relevância** com **diversidade** (reduz redundância), usando `lambda_mult` para controlar esse trade-off (mais perto de 1 = mais relevância, mais perto de 0 = mais diversidade). citeturn3view0

##### 3) `transformers` (como “preencher” metadados para ter arestas boas) [Link da Documentação](https://datastax.github.io/graph-rag/guide/transformers/)

Graph traversal funciona em cima de **metadados estruturados**. Os *transformers* são ferramentas opcionais para **popular/enriquecer esses metadados**, mas não são obrigatórios se você já tem metadados bons. citeturn1view0

A documentação divide transformers em dois grupos: citeturn1view0turn1view1
- **Information Extractors**: extraem informação do texto e gravam em `metadata` (ex.: entidades, keywords, hyperlinks)
- **Metadata Utilities**: ajustam/normalizam metadados para habilitar features (ex.: hierarquia de pai/filho, “shredding” de listas)

Exemplos citados na doc:
- `KeyBERTTransformer` → gera `metadata["keywords"]` a partir do texto citeturn1view1  
- `SpacyNERTransformer` / `GLiNERTransformer` → extraem entidades/labels para `metadata` citeturn1view1  
- `ParentTransformer` → adiciona um campo `parent` para representar hierarquia (`path` → `parent`) citeturn1view1  
- `ShreddingTransformer` → transforma campos “coleção” (listas) em múltiplos pares chave-valor, útil para vector stores sem suporte nativo a listas (e permite restaurar depois). citeturn1view1

**Como isso se encaixa no nosso exemplo:** hoje nós já criamos `metadata["related_to"]` manualmente. Em dados reais, você pode usar transformers para criar metadados como `keywords`, `entities`, `citations` etc., e então apontar `edges` para esses campos — assim a travessia passa a “andar” por relações extraídas do próprio conteúdo.

> Referências usadas: Edges/Edge Functions, Strategies (incluindo MMR) e Transformers/Metadata utilities no GraphRAG da DataStax.


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

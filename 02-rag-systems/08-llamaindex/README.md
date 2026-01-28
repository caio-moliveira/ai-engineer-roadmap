# 🦙 Módulo 8: LlamaIndex

> **Goal:** Estruturação Avançada de Dados.  
> **Status:** Ótimo para dados complexos, as vezes Overkill.

## 1. Quando usar LlamaIndex vs LangChain?
- **LangChain:** Melhor para **Lógica de Aplicação** (Chamada de API, fluxos, agentes).
- **LlamaIndex:** Melhor para **Lógica de Dados** (Parsing, Estratégia de Indexação, Retrieval types).

> **Regra de Ouro:**
> Se você tem uma bagunça de PDFs, HTML e SQL e precisa "consultar isso", LlamaIndex é poderoso.
> Se você está construindo um Agente complexo que usa 5 ferramentas + RAG, LangChain/LangGraph geralmente é melhor.

## 2. Features Chave
### Data Connectors (LlamaHub)
O melhor ecossistema de ingestão. Loaders de uma linha para Notion, Slack, Discord, SQL.

### Recursive Retrieval (A "Killer Feature")
- **Node References:** Indexe um resumo do documento. Quando recuperado, busque os chunks *inteiros* do documento.
- **Resultado:** Você busca pelo resumo (alto match semântico) mas alimenta o LLM com os chunks detalhados (alto contexto).

### Knowledge Graphs
LlamaIndex cria estruturas GraphRAG (Triplets: Sujeito -> Predicado -> Objeto) automaticamente.
Útil para perguntas como "Como a entidade A se relaciona com a entidade B?", onde vetores falham.

## 3. Integração
Você não precisa escolher.
Você pode construir um **LlamaIndex Retriever** e usá-lo dentro de um **LangChain Agent**.

```python
# Criar Index no LlamaIndex
index = VectorStoreIndex.from_documents(docs)

# Converter para Retriever do LangChain
retriever = index.as_retriever()

# Usar no LangChain
chain = retriever | prompt | llm
```

## 🧠 Mental Model: "O Arquivista"
LlamaIndex é o arquivista obsessivo que organiza documentos em pastas perfeitas, subpastas e fichas catalográficas.
LangChain é o gerente que coordena a equipe.

## ⏭️ Próximo Passo
Nós construímos. Funciona?
Vá para **[Módulo 9: Avaliação](../09-evaluation)**.

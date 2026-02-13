# Módulo 06: Agentes RAG (RAG Agents)

Este módulo avança do conceito de **RAG Pipelines** (sequências lineares de recuperação + geração) para **RAG Agents** (sistemas autônomos que usam razocinío para decidir *quando* e *o quê* buscar).

Enquanto um pipeline tradicional faz "Retrieval -> Generation" sempre, um Agente pode:
1.  Receber uma pergunta complexa.
2.  Decidir que precisa buscar informações no banco vetorial.
3.  Formular a query de busca (que pode ser diferente da pergunta do usuário).
4.  Analisar os documentos retornados.
5.  Se a informação for insuficiente, realizar uma nova busca ou responder que não sabe.

## 📂 Estrutura dos Arquivos

### 🛠️ Utilitários

- **`utils.py`**:
  - Script compartilhado que gerencia a conexão com o **Qdrant** e indexa o PDF `Understanding_Climate_Change.pdf` (localizado em `02-rag/05-retrievers/`).
  - Garante que a collection `climate_change_collection` exista.

### 🦜 Agente com LangChain (LangGraph)

- **Arquivo**: `01_rag_agent_langchain.py`
- **Framework**: Usa componentes modernos do **LangGraph** (a evolução dos agentes no LangChain).
- **Tooling**:
  - Define uma *Custom Tool* usando o decorador `@tool`.
  - A ferramenta `retrieve_context` acessa o Qdrant para buscar chunks relevantes.
- **Arquitetura**: **ReAct (Reasoning + Acting)**. O modelo (GPT-4o) recebe a descrição da ferramenta e decide chamá-la se a pergunta do usuário exigir contexto externo.
- **Destaque**: Uso de `.stream()` com `stream_mode="values"` para visualizar o processo de raciocínio passo-a-passo.
- **Docs**:
  - [LangChain RAG-Agent](https://docs.langchain.com/oss/python/langchain/rag#rag-chains)
  - [LangGraph RAG-Agent](https://docs.langchain.com/oss/python/langgraph/agentic-rag)

### 🦙 Agente com LlamaIndex

- **Arquivo**: `02_rag_agent_llamaindex.py`
- **Framework**: **LlamaIndex Agents**.
- **Tooling**:
  - Usa `QueryEngineTool`. O LlamaIndex encapsula todo o pipeline de busca (Index -> Retriever -> Response Synthesizer) em uma única ferramenta.
  - O agente enxerga essa ferramenta como uma "API" para consultar sua base de conhecimento.
- **Arquitetura**: **Function Calling Agent**. Otimizado para LLMs que suportam chamada de função nativa (como GPT-3.5/4o), permitindo chamadas de ferramentas mais robustas e estruturadas.
- **Destaque**: A facilidade de conectar o `VectorStoreIndex` diretamente como uma ferramenta para o agente.
- **Docs**:
  - [LlamaIndex Agents](https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/)


### Executando os Agentes

```bash
# Versão LangChain
python 02-rag/06-rag-agent/01_rag_agent_langchain.py

# Versão LlamaIndex
python 02-rag/06-rag-agent/02_rag_agent_llamaindex.py
```

## 🧠 Pipeline vs Agente: Qual escolher?

| Característica | RAG Pipeline (Chain) | RAG Agent |
| :--- | :--- | :--- |
| **Fluxo** | Linear (Retrieval -> Generate) | Dinâmico (ReAct, Loop) |
| **Previsibilidade** | Alta (Sempre faz a mesma coisa) | Média (O modelo decide o caminho) |
| **Custo** | Baixo (1 chamada LLM geralmente) | Médio/Alto (Múltiplas chamadas/loops) |
| **Complexidade** | Simples | Alta |
| **Uso Ideal** | Perguntas diretas ("O que é X?") | Perguntas multi-step ("Compare X com Y e resuma") |

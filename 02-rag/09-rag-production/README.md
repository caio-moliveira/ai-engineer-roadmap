# Agentic RAG com Qdrant & LangGraph (Produção)

Este módulo representa o projeto final da nossa trilha de *Retrieval-Augmented Generation* (RAG). Aqui, elevamos o sistema RAG tradicional para uma arquitetura **Agentic RAG**, pronta para produção, que une a força de bancos de dados vetoriais locais (Qdrant), frameworks de agentes (LangGraph e LangChain), e uma API moderna (FastAPI).

## 🎯 Objetivo Arquitetural

No RAG Tradicional, o fluxo é fixo: o usuário pergunta, o sistema sempre busca no banco de dados vetorial, anexa o contexto e envia ao LLM.

**No nosso projeto (Agentic RAG):** 
Nós utilizamos o **LangGraph** para criar um Agente (LLM) que toma decisões. Através de *Tools* (ferramentas), o modelo decide proativamente:
1. **Devo responder diretamente?** (Para bate-papo, saudações "Olá, bom dia").
2. **Devo invocar a ferramenta de busca?** (Para perguntas técnicas ou sobre o acervo documental).

Isso resulta em um sistema mais inteligente, que não gasta tokens e tempo fazendo buscas desnecessárias, mas realiza *queries* cirúrgicas na base vetorial quando precisada de contexto.

## 🛠️ Stack Tecnológica e Ferramentas

O ecossistema que construímos envolve as seguintes tecnologias:

*   **FastAPI**: Servidor web assíncrono hiper-rápido, provendo os endpoints da nossa aplicação Restful.
*   **Qdrant**: Nosso Banco de Dados Vetorial *Open Source*. Estamos rodando o Qdrant via Docker localmente (porta 6333) para persistir nossos embeddings de alta dimensão.
*   **LangChain & LangGraph**: Orquestração do agente. O `LangGraph` gerencia o Estado da nossa conversa (StateGraph) e o ciclo dinâmico contínuo entre invocações diretas ao LLM e o *ToolNode* (nossa ferramenta de busca).
*   **OpenAI Embeddings (text-embedding-3-large)**: Criação de vetores para mapeamento semântico dos textos.
*   **OpenAI LLM (gpt-4o-mini)**: O "Cérebro" do Agente, encarregado de interpretar requests e executar chamadas da ferramenta de retrieve.
*   **Langfuse**: Plataforma de Observabilidade e Monitoramento de LLMs. Usado através de callbacks para traçar e analisar cada token gerado e tempo de inferência nas requisições.

## 🗂️ Estrutura do Projeto

```text
09-rag-production/
├── index.html                  # Interface Web Frontend simples para testes (Chat + Upload).
├── main.py                     # Entrypoint do Uvicorn que sobe a aplicação FastAPI.
├── src/
│   ├── api.py                  # Definição do FastAPI, CORS e inclusão de Routers.
│   ├── models.py               # Contratos de dados (Pydantic Models) para as Requisições/Respostas.
│   ├── settings.py             # Gerenciamento de Variáveis de Ambiente e chaves de API.
│   ├── pdf_utils.py            # Utilitários de extração de texto em memória (PyMuPDF - fitz).
│   ├── customlogger.py         # Configuração de Logs padronizado para console.
│   ├── chat/
│   │   ├── chat.py             # Core do Agentic RAG: Graph State, Agente LLM, e a Tool de Retrieve.
│   │   ├── llm_models.py       # Instanciação centralizada das LLMs e Embeddings conectados ao Langfuse.
│   │   └── qdrant.py           # Conexão AsyncGlobal com o serviço Qdrant.
│   ├── embedder/
│   │   ├── client.py           # Operações de Banco (Criar collection, Upsert Vetores).
│   │   └── processor.py        # Processamento Inteligente: Chunking Dinâmico, Extração Meta-Info + LLM.
│   └── routers/
│       ├── chat.py             # Endpoint /chat/ask -> Conecta o cliente Frontend ao agente.
│       ├── embedder.py         # Endpoints de Upload, Processamento e Coleções.
│       └── qdrant.py           # (Antigo/Legado) Rotas adicionais de administração CRUD do Qdrant.
```

## ⚙️ Novidades e Funcionalidades Core

### 1. Ingestão Dinâmica de Documentos
Foi criado um motor flexível no `processor.py` para ingestão:
*   Os administradores podem através de Endpoints subir PDFs diretamente para *Collections* específicas.
*   Pode ser decidido em tempo-de-requisição se usaremos divisores Recursivos (`RecursiveCharacterTextSplitter`) ou por blocos fechados.
*   Tamanho de Chunks, Overlap e tokenizadores locais (`tiktoken`) são parametrizados via API dinamicamente.

### 2. Auto-Extração de Metadados via LLM
Ao enviar um documento para o vetor, o sistema lê automaticamente a primeira página e solicita dinamicamente a outro LLM (via `with_structured_output`) que emita:
*   `classificacao`: Qual o tipo do arquivo em 3 palavras.
*   `descricao`: Resumo funcional em 2 frases.
* Isso entra como metadados enriquecidos no banco, facilitando filtros e aumentando contexto de leitura futura.

### 3. Agente com Tool Calling e Multi-Collections
O chat mudou radicalmente nesta versão. Usamos a magia do `StateGraph` do LangGraph.
*   O estado gerencia a lista de mensagens (`messages`) e também o arquivo contextual (`file_context`).
*   O Endpoints aceita no payload `collection_name`, passando dinamicamente essa variável na configuração de Runtime do LangGraph para a ferramenta `retrieve_documents`. Assim o usuário pesquisa na base que quiser sem reescrever código.
*   **O Agente pensa:** Se a requisição requerer, o agente ativa a *tool*, varre o banco, junta o resultado retornado pela Tool, formata com citações ("Fonte: arquivo X, pág Y") e molda a resposta final.

### 4. Observabilidade Real (Langfuse)
As chamadas da Rota `/chat/ask` instanciam um `CallbackHandler()` do Langfuse especificamente e dinamicamente para aquela requisição, rotulando com Tags o nome da coleção acessada e atrelando tudo a `session_id`'s independentes.


## 🚀 Como Executar Localmente

### Pré-requisitos
1.  **Docker**: Necessário para rodar o Qdrant local.
2.  **uv** (ou pip): Gerenciador de dependências python moderno.
3.  **Ambiente configurado**: Crie um arquivo `.env` na raiz da pasta `09-rag-production` baseado nas chaves pedidas. (OpenAI API e Langfuse)

### Passos:

1.  **Subir o Qdrant pelo Docker:**
    ```bash
    docker run -p 6333:6333 -p 6334:6334 -v qdrant_data:/qdrant/storage:z qdrant/qdrant
    ```

2.  **Instalar e ativar ambiente virtual (se usando UV):**
    ```bash
    uv venv
    uv pip sync requirements.txt
    uv pip install pymupdf  # Garantir compatibilidade do processador PDF
    ```

3.  **Rodar a aplicação FastAPI:**
    ```bash
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

4.  **Testar via UI Própria!**
    *   Vá no explorador de arquivos, ache o `index.html` deixado na raiz da pasta `09-rag-production`.
    *   Dê um duplo-clique para abrir no Google Chrome / Edge.
    *   No painel esquerdo: Crie uma coleção "base_estudo" e envie seus PDFs ou TXTs.
    *   No painel direito: Troque o campo "Coleção" para "base_estudo" e interaja com o agente em tempo real!

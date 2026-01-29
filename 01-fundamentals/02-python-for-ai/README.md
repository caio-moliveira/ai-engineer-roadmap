# 🐍 Python para Sistemas de IA: O Framework de Engenharia

> **Objetivo:** Estabelecer a fundação técnica para construção de sistemas de IA, indo além de notebooks e scripts experimentais. Aqui, Python é tratado como a infraestrutura de aplicações críticas.

Este módulo define como um AI Engineer Sênior estrutura seu ambiente e escolhe suas ferramentas para construir LLMs, RAGs e Agentes em produção.

---

## 🏗️ Parte 1: Setup do Workspace (Nível AI Engineer)

Esqueça o tutorial básico de `pip install`. Em sistemas complexos de IA, **reprodutibilidade e isolamento** são inegociáveis. O caos de dependências é o maior inimigo da estabilidade operacional.

### Por que o modelo tradicional falha?
O método antigo (`venv` + `requirements.txt` gerado manualmente ou com `pip freeze`) não garante determinismo. Builds quebram porque bibliotecas "filhas" atualizaram sem aviso. Em IA, onde pacotes como `torch` ou `cuda` são massivos e sensíveis, isso é fatal.

### O Stack Moderno

#### **1. Gerenciamento de Dependências: `uv`**
O novo padrão industrial. Escrito em Rust, substitui `pip`, `poetry`, `pyenv` e `virtualenv` de uma só vez.
- **Lockfiles Universais:** Garante que a versão exata (hash) instalada no seu laptop seja a mesma do container em produção.
- **Workspaces:** Suporte nativo a monorepos, permitindo ter múltiplos pacotes (ex: `core`, `api`, `workers`) compartilhando dependências base.
- **Velocidade:** Instala pacotes pesados de ML (GBs) em segundos, não minutos.

#### **2. Estrutura de Projeto (Separation of Concerns)**
- **Dev/Test/Prod:** Separação rígida de dependências via grupos no `pyproject.toml`.
- **Configuração Centralizada:** Todas as ferramentas (`ruff`, `mypy`, `pytest`) leem do mesmo `pyproject.toml`. Nada de arquivos de config espalhados.

> **Mindset:** "Meu ambiente de desenvolvimento é uma réplica determinística da produção. Se funciona aqui, o container sobe lá."

---

## 🛠️ Parte 2: Bibliotecas Core para Sistemas de IA

Antes de falar de LLMs, precisamos de uma base sólida de Engenharia de Software. Estas são as ferramentas que sustentam o sistema.

| Biblioteca | Função no Sistema de IA |
| :--- | :--- |
| **Pydantic** | **O Contrato de Dados.** Define a estrutura de inputs/outputs, valida respostas de LLMs e garante integridade. Essencial para *Structured Outputs*. |
| **FastAPI** | **A Camada de Serviço.** Padrão para servir modelos e APIs de RAG devido ao suporte nativo a AsyncIO e injeção de dependência. |
| **HTTPX** | **O Cliente Web.** O substituto moderno do `requests`. Totalmente assíncrono, perfeito para orquestrar chamadas paralelas a APIs de LLM. |
| **AsyncIO** | **A Concorrência.** LLMs são lentos (I/O bound). AsyncIO permite processar milhares de requests enquanto aguarda a inferência. |
| **Tenacity** | **A Resiliência.** Retries inteligentes com *exponential backoff*. Obrigatório, pois APIs de IA falham frequentemente. |
| **Logging** | **A Observabilidade.** Logs estruturados. Vital para rastrear o fluxo de execução em produção. |
| **Python-Dotenv** | **A Segurança.** Carrega segredos de ambiente. Chaves de API nunca devem estar no código. |

---

## 🧠 Parte 3: Frameworks de Sistemas de IA

Aqui entram as ferramentas específicas para construir a inteligência da aplicação. O segredo é saber **quando** usar cada uma.

### 1. Frameworks de Orquestração de LLM
*O "cérebro" que conecta o modelo ao código.*

- **LangChain:** O pioneiro. Excelente para prototipagem rápida e integrações amplas.
  - *Docs:* [python.langchain.com](https://python.langchain.com/)
- **LangGraph:** A evolução para produção. Focado em **grafos de estado** e loops de controle. Ideal para agentes complexos e fluxos cíclicos.
  - *Docs:* [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)
- **LlamaIndex:** O especialista em dados. Focado em ingestão, indexação e estratégias avançadas de RAG.
  - *Docs:* [docs.llamaindex.ai](https://docs.llamaindex.ai/)

### 2. Frameworks de Agentes
*Sistemas que agem, não apenas respondem.*

- **LangGraph (Agentes):** Permite construir agentes com controle granular de estado e memória. O padrão para sistemas robustos.
- **CrewAI:** Focado em orquestração de "equipes" de agentes com papéis definidos (Pesquisador, Escritor). Mais alto nível.
  - *Docs:* [docs.crewai.com](https://docs.crewai.com/)
- **AutoGen (Microsoft):** Padrão conversacional entre múltiplos agentes. Ótimo para simulações complexas.
  - *Docs:* [microsoft.github.io/autogen](https://microsoft.github.io/autogen/)

### 3. Frameworks de RAG
*Conectando dados proprietários.*

- **LangChain/LlamaIndex:** Ambos oferecem pipelines completos de RAG.
- **Docling:** Especialista em parsing de documentos complexos (PDFs com tabelas). Transforma arquivos em JSON/Markdown estruturado para RAG.
  - *Docs:* [ds4sd.github.io/docling](https://docling-project.github.io/docling/)

### 4. Frameworks de Modelo & Inferência
*Rodando o modelo (se você não usa API proprietária).*

- **Hugging Face Transformers:** A biblioteca de fato para manipular modelos open-source.
  - *Docs:* [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers)
- **vLLM:** Servidor de inferência focado em alto throughput e gerenciamento de memória (PagedAttention). Essencial para self-hosting.
  - *Docs:* [docs.vllm.ai](https://docs.vllm.ai/)
- **Unsloth:** Acelerador de Fine-Tuning. Treina modelos (Llama, Mistral) até 5x mais rápido com menos memória.
  - *Docs:* [github.com/unslothai/unsloth](https://github.com/unslothai/unsloth)

### 5. Ecossistema de Vetores
*A memória de longo prazo.*

- **Qdrant / Weaviate / Milvus:** Bancos vetoriais dedicados para produção em escala.
- **FAISS:** Biblioteca para busca vetorial local e eficiente (bom para datasets estáticos).

---

## 🔗 Parte 4: Como tudo se encaixa (Arquitetura de Referência)

Um sistema de IA real em produção não é um script único. Ele é composto por camadas especializadas trabalhando em harmonia:

1.  **Camada de Serviço (FastAPI + Pydantic):** Recebe a requisição do usuário, valida o schema de entrada e autentica.
2.  **Camada de Orquestração (LangGraph):** Recebe o input limpo. O grafo decide o fluxo: "Preciso buscar documentos?" ou "Posso responder direto?".
3.  **Camada de Recuperação (Qdrant + LlamaIndex):** Se decidir buscar, consulta o Banco Vetorial usando embeddings.
4.  **Camada de Geração (HTTPX + LLM API):** Envia o prompt montado (contexto + pergunta) para o LLM via requisição assíncrona.
5.  **Camada de Observabilidade (Logging + Langfuse):** Registra cada passo (latência, tokens usados, decisão do agente) para análise no painel.

> **Resumo:** O AI Engineer usa Python para costurar esses componentes com robustez, transformando componentes probabilísticos (LLMs) em sistemas de software confiáveis.

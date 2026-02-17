<div align="center">
    <img src="../assets/jornada.png" alt="Jornada de Dados" width="200"/>



# **Bloco 1 — Fundamentos da Engenharia de IA**

### Base técnica para construção de sistemas de IA probabilísticos, assíncronos e orientados a produção

</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-Data%20Validation-e92063?style=for-the-badge)](https://docs.pydantic.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-LLM%20API-lightgrey?style=for-the-badge&logo=openai)](https://platform.openai.com/docs)
[![LangChain](https://img.shields.io/badge/LangChain-Orchestration-blueviolet?style=for-the-badge)](https://python.langchain.com/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-blue?style=for-the-badge)](https://docs.llamaindex.ai/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/docs/transformers)
[![uv](https://img.shields.io/badge/uv-Python%20Package%20Manager-black?style=for-the-badge)](https://github.com/astral-sh/uv)

</div>

---

<div align="center">

### Tecnologias e padrões utilizados ao longo do bloco

Python moderno • APIs assíncronas • validação estruturada • LLM orchestration • RAG pipelines • bancos relacionais e vetoriais

</div>


<div align="center">
<img src="../assets/fundamentos.png" alt="Fundamentos" width="1000"/>
</div>

---
## 📚 Ementa do Módulo

### [Módulo 01: A Profissão de AI Engineer & Mercado](./01-ai-engineer-profession)
- **O Papel:** A diferença entre AI Engineer, ML Engineer e Backend Dev. Foco em **Produto** e **Sistemas**.
- **Os 3 Pilares:** Fluência em Foundation Models (Prompting, Structured Outputs), Arquitetura de Sistemas (RAG, Agentes) e Engenharia de Produção.
- **Mindset:** Construção de software robusto em cima de componentes não-determinísticos.

### [Módulo 02: Fundamentos de LLMs & GenAI](./02-llm-fundamentals)
- **A "Física" dos LLMs:** Tokens, Context Window, Temperature, Top-P e o conceito de *Autoregressive*.
- **Prompt Engineering:** Ciência, não arte. Zero-shot, Few-shot, Chain-of-Thought (CoT).
- **Agentes & Tools:** Tool Calling como a base para agentes autônomos que interagem com o mundo.
- **Estratégia:** Quando usar RAG vs Fine-tuning.

### [Módulo 03: Python Moderno para AI Engineers](./03-python-for-ai)
- **Stack de Engenharia:** Gerenciamento de dependências com `uv` e estrutura de monorepo.
- **Bibliotecas Core:** Pydantic, HTTPX, AsyncIO, Tenacity para resiliência.
- **Frameworks de IA:** Visão geral de LangChain, LangGraph, LlamaIndex e Agno.
- **Observabilidade:** A importância de logs estruturados e tracing em sistemas estocásticos.

### [Módulo 04: APIs & Backend com FastAPI](./04-fastapi)
- **Produção:** Construção de APIs assíncronas de alta performance para servir modelos e RAG.
- **Design:** Injeção de dependência, validação com Pydantic e OpenAPI (Swagger).
- **Integração:** Conectando OpenAI/LangChain via endpoints HTTP seguros e escaláveis.

### [Módulo 05: Modelagem e Contratos de Dados (Pydantic V2)](./05-data-modeling)
- **Contratos de Dados:** Schemas rigorosos como a "camada de confiabilidade" para outputs de LLM.
- **Features Avançadas:** Validadores customizados, Tipos Ricos (Enum, URL, UUID) e Unions Discriminadas.
- **Pipeline de Extração:** Implementando retries automáticos com feedback de erro estruturado.
- **Configuração:** Gerenciamento de variáveis de ambiente com `pydantic-settings`.

### [Módulo 06: Bancos de Dados (SQL + Vetorial)](./06-databases)
- **Vector Databases:** Conceitos de Embeddings, Busca Semântica vs Busca Exata e `Payload`.
- **Métricas:** Distância de Cosseno, Dot Product e indexação HNSW.
- **Qdrant:** Setup e uso prático (Local em memória vs Docker em produção) com filtragem de metadados.
- **Arquitetura Híbrida:** Quando integrar SQL (Postgres) com Vector DBs.
---

## 🚀 Como Começar
Acesse os módulos sequencialmente. O conhecimento é cumulativo.
Comece pelo **[Módulo 01: A Profissão de AI Engineer & Mercado](./01-ai-engineer-profession)**.

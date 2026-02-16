<div align="center">
  <img src="./assets/jornada.png" alt="Jornada de Dados" width="200"/>

# **Trilha Completa: Engenharia de IA**

### Construção profissional de sistemas de IA, RAGs e agentes em produção

**Formação prática focada em arquitetura, orquestração, observabilidade e deploy de aplicações de IA modernas**

</div>

---

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)

[**Site Oficial**](https://suajornadadedados.com.br/) • [**Comunidade**](https://suajornadadedados.com.br/) • [**Documentação**](https://suajornadadedados.com.br/)
</div>

---

## 🚀 O Manifesto do Engenheiro de IA (Edição 2026)

O mercado de "Power Users" de chat saturou. Em 2026, a barreira de entrada não é mais saber o que é um prompt, mas sim como garantir **determinismo, segurança e custo-eficiência** em sistemas não-determinísticos.

### 🎯 Onde você se posiciona?
Diferente do **Cientista de Dados** (focado em *Training & Fine-tuning*) e do **ML Engineer** (focado em *Infrastructure & Serving*), o **AI Engineer** é o engenheiro de software especializado na composição de Modelos de Fundação.

> **"Nossa missão não é criar inteligência bruta, mas arquitetar o contexto necessário para que ela seja útil."**

### 💎 Pilares da Engenharia de IA Moderna

Para mover o ponteiro em projetos reais, atacamos os três pilares que separam demos de produtos:

1.  **Fidelidade (Grounding):** Implementação de RAG (Retrieval-Augmented Generation) multicamadas para eliminar alucinações.
2.  **Autonomia (Agency):** Evolução de fluxos lineares para grafos cíclicos com **LangGraph**, permitindo raciocínio complexo e correção de erros em tempo real.
3.  **LLMOps & Observabilidade:** Se você não mede, você não gerencia. Utilizamos **Langfuse** e **Arize Phoenix** para rastreabilidade total de tokens, latência e custo.

---

## 🛠️ O Tech Stack do Especialista
Não ensinamos apenas ferramentas; ensinamos os padrões de design de software aplicados à IA:

* **Linguagem & Base:** Python Pro (AsyncIO), Pydantic (Validação de Dados) e Docker.
* **Vector Architecture:** Qdrant, Pinecone e ChromaDB para busca semântica e híbrida.
* **Orquestração de Estado:** LangChain e LangGraph para fluxos de agentes com memória persistente.
* **Engenharia de Prompt:** Chain-of-Thought, Few-shot prompting e técnicas de compressão de contexto.

---

## 📚 A Trilha de Formação
<div align="center">
<img src="./assets/roadmap.png" alt="Roadmap" width="1000"/>
</div>


### [🔹 Bloco 1: Fundamentos Reais](./01-fundamentals)

Este bloco define a base conceitual e técnica necessária para construir sistemas modernos de Inteligência Artificial em produção.

Não é um bloco sobre sintaxe, bibliotecas isoladas ou experimentação em notebooks.
É sobre entender como desenvolver software quando o componente central do sistema é **probabilístico, assíncrono e com custo operacional variável**.

A engenharia de sistemas baseados em Large Language Models difere fundamentalmente do desenvolvimento tradicional porque:

* a saída não é determinística
* erros podem parecer respostas válidas
* latência depende de inferência externa
* custo depende diretamente de tokens consumidos

A própria OpenAI enfatiza que o trabalho real com IA não é treinar modelos, mas construir sistemas ao redor deles:
[https://cookbook.openai.com/](https://cookbook.openai.com/)

Arquiteturas corporativas modernas seguem o mesmo princípio, tratando LLMs como apenas um componente dentro de pipelines maiores (AWS Generative AI Reference Architecture):
[https://aws.amazon.com/architecture/generative-ai/](https://aws.amazon.com/architecture/generative-ai/)

Este bloco existe para estabelecer os fundamentos que tornam possível construir sistemas confiáveis nessas condições.

---

### Estrutura do Bloco 

#### [Módulo 01: A Profissão de AI Engineer & Mercado](./01-fundamentals/01-ai-engineer-profession)

Este módulo define o papel profissional do AI Engineer no ecossistema moderno de software.

Ele aborda:

* a diferença entre AI Engineer, ML Engineer e Backend Engineer
* as expectativas reais do mercado corporativo
* o perfil técnico necessário para operar sistemas de IA

A distinção entre construir modelos e construir sistemas é central para a indústria atual. Documentação de plataformas corporativas como Azure AI Architecture Guide enfatiza explicitamente a necessidade de integração, observabilidade e governança como partes essenciais do desenvolvimento:
[https://learn.microsoft.com/en-us/azure/architecture/ai-ml/](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/)

A noção de engenharia orientada a produto também aparece em relatórios de mercado como McKinsey AI Adoption Report:
[https://www.mckinsey.com/capabilities/quantumblack/our-insights](https://www.mckinsey.com/capabilities/quantumblack/our-insights)

O objetivo deste módulo é alinhar o aluno com a realidade operacional da profissão antes de qualquer ferramenta.

---

#### [Módulo 02: Fundamentos de LLMs & GenAI](./01-fundamentals/02-llm-fundamentals)

Este módulo apresenta os princípios matemáticos e operacionais dos Large Language Models.

Ele cobre:

* tokenização e representação textual
* janelas de contexto
* parâmetros de geração como temperature e sampling
* técnicas modernas de prompt engineering
* tool calling e execução externa

A arquitetura dominante dos LLMs modernos é baseada no Transformer, introduzido em:

Attention Is All You Need
[https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)

A capacidade de aprendizado por exemplos no contexto foi demonstrada no paper do GPT-3:

Language Models are Few-Shot Learners
[https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)

O uso de raciocínio explícito em prompts é discutido em:

Chain-of-Thought Prompting
[https://arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)

E a integração entre raciocínio e ação via ferramentas aparece em:

ReAct: Synergizing Reasoning and Acting
[https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

Este módulo estabelece o entendimento necessário para tratar LLMs como componentes de engenharia, não interfaces conversacionais.

---

#### [Módulo 03: Python Moderno para AI Engineers](./01-fundamentals/03-python-for-ai)

Este módulo estabelece o ambiente de engenharia necessário para sistemas de IA em produção.

Ele cobre:

* gerenciamento moderno de dependências
* tipagem estática
* arquitetura modular de projetos
* padrões de organização de código

Sistemas de IA possuem dependências pesadas e altamente sensíveis (CUDA, Torch, bibliotecas nativas).
Por esse motivo, a reprodutibilidade do ambiente é considerada requisito operacional básico em engenharia de ML moderna (ver MLOps Principles, Google Cloud):
[https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

O módulo também introduz bibliotecas fundamentais para aplicações assíncronas e orientadas a serviços, alinhadas com práticas modernas de backend Python.

---

#### [Módulo 04: APIs & Backend com FastAPI](./01-fundamentals/04-fastapi-backend)

Este módulo cobre a construção da camada de serviço responsável por expor sistemas de IA.

Ele aborda:

* programação assíncrona com async/await
* injeção de dependência
* definição automática de contratos OpenAPI
* tratamento de concorrência

Aplicações de IA são tipicamente I/O bound, dependendo de chamadas externas para inferência.
Frameworks assíncronos são recomendados para esse cenário, conforme documentado no próprio FastAPI:

[https://fastapi.tiangolo.com/async/](https://fastapi.tiangolo.com/async/)

A geração automática de documentação via OpenAPI também segue padrões amplamente adotados na indústria de APIs:
[https://swagger.io/specification/](https://swagger.io/specification/)

Este módulo ensina como transformar pipelines de IA em serviços acessíveis e escaláveis.

---

#### [Módulo 05: Modelagem e Contratos de Dados](./01-fundamentals/05-data-modeling)

Este módulo aborda a camada crítica de confiabilidade de sistemas baseados em LLM.

Ele cobre:

* JSON Schema
* serialização estruturada
* validação automática
* definição de contratos rígidos para entrada e saída

Modelos de linguagem não garantem consistência estrutural na saída.
Por isso, a validação de schemas é considerada prática essencial na documentação oficial de Structured Outputs da OpenAI:

[https://platform.openai.com/docs/guides/structured-outputs](https://platform.openai.com/docs/guides/structured-outputs)

O módulo utiliza Pydantic v2 para formalizar contratos de dados e garantir integridade em pipelines probabilísticos.

---

#### [Módulo 06: Bancos de Dados (SQL + Vetorial)](./01-fundamentals/06-databases)

Este módulo introduz a arquitetura de armazenamento híbrido necessária para aplicações modernas de IA.

Ele cobre:

* integração entre banco relacional e banco vetorial
* embeddings e representação semântica
* distância de cosseno
* filtragem por metadados

A estratégia de Retrieval-Augmented Generation foi formalizada em:

Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
[https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

A busca vetorial em larga escala normalmente utiliza algoritmos Approximate Nearest Neighbor como HNSW, descritos em:

Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs
[https://arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)

Este módulo estabelece a base de armazenamento necessária para construir sistemas conectados a dados proprietários.

---

## Referências Complementares

Run an LLM locally with LM Studio [https://www.kdnuggets.com/run-an-llm-locally-with-lm-studio](https://www.kdnuggets.com/run-an-llm-locally-with-lm-studio)
Prompt Engineering Guide[https://www.promptingguide.ai/](https://www.promptingguide.ai/)
Outlines Quickstart[https://dottxt-ai.github.io/outlines/latest/quickstart/](https://dottxt-ai.github.io/outlines/latest/quickstart/)
LMQL Overview[https://lmql.ai/docs/language/overview.html](https://lmql.ai/docs/language/overview.html)


### [🔹 Bloco 2: Sistemas RAG](./02-rag)
Este não é apenas "Chat with PDF". RAG em produção exige estratégias de Chunking, Reranking e Avaliação.

#### [Módulo 01: Fundamentos de RAG e Modelos Mentais](./02-rag/01-rag-fundamentals)
- **Definição:** RAG = Busca (Retrieval) + Geração (Generation).
- **Por que RAG?** Superando alucinações e data de corte (knowledge cutoff).
- **Arquitetura Padrão:** Ingestion -> Store -> Retrieve -> Generate.

#### [Módulo 02: Ingestão de Dados e Pipelines](./02-rag/02-ingestion-pipeline)
- **ETL para IA:** Extrair texto limpo de PDFs, HTML e Markdown.
- **Chunking:** Estratégias (Fixed-size, Recursive, Semantic) e seus impactos.
- **Metadados:** Por que metadados são mais importantes que o texto em si.

#### [Módulo 03: Embeddings (Visão Moderna)](./02-rag/03-embeddings)
- **Conceito:** Transformando texto em vetores numéricos.
- **Modelos:** OpenAI vs Open Source (bge-m3, e5).
- **Multilingual:** Lidando com português e inglês misturados.

#### [Módulo 04: Vetor Databases (Vector DBs)](./02-rag/04-vector-dbs)
- **Opções:** Qdrant (Rust/Performance) vs pgvector (Simplicidade/Postgres).
- **Indexação:** HNSW explicado para humanos.
- **Tradeoffs:** Memória vs Disco vs Velocidade.

#### [Módulo 05: Estratégias de Retrieval (Crítico)](./02-rag/05-retrieval-strategies)
- **Hybrid Search:** Misturando busca semântica (Vetores) com busca exata (BM25/Keywords).
- **Reranking:** O segredo para dobrar a precisão. (Cohere Rerank / Cross Encoders).
- **Query Expansion:** Melhorando a pergunta do usuário antes de buscar.

#### [Módulo 06: LangChain v1 (LCEL)](./02-rag/06-langchain-v1)
- **Modern LangChain:** Esqueça `RetrievalQAChain`. Use LCEL (LangChain Expression Language).
- **Composabilidade:** Pipelines declarativos e transparentes.
- **Runnables:** O protocolo padrão para invocar cadeias.

#### [Módulo 07: LangGraph (Orquestração RAG)](./02-rag/07-langgraph)
- **Loops:** Quando a busca linear falha, precisamos de loops (agentes).
- **Corrective RAG:** Se a busca for ruim, pesquise na web. (Flow condicional).
- **Estado:** Mantendo memória durante a execução do grafo.

#### [Módulo 08: LlamaIndex](./02-rag/08-llamaindex)
- **Foco em Dados:** Quando usar LlamaIndex em vez de LangChain.
- **Advanced Indexing:** Hierarchical Indices, Document Summary Index.
- **Query Engine:** Abstrações poderosas para dados complexos.

#### [Módulo 09: Avaliação e Observabilidade](./02-rag/09-evaluation)
- **Ragas:** Framework de avaliação automática (Faithfulness, Answer Relevancy).
- **Tracing:** Visualizando cada passo com Langsmith/Langfuse.
- **Golden Datasets:** Criando um conjunto de testes confiável.

#### [Módulo 10: RAG em Produção](./02-rag/10-rag-production)
- **Otimização:** Cache Semântico, Streaming, Latência.
- **Segurança:** Prompt Injection em RAG.
- **Custos:** Estimando tokens de input/output em escala.

---

### 🛠️ Stack RAG (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Orquestração** | LangChain / LangGraph | Flexibilidade e ecossistema. |
| **Vector DB** | Qdrant / pgvector | Performance e facilidade de uso. |
| **Embeddings** | OpenAI (text-3) / Cohere | Qualidade e facilidade. |
| **LLM** | GPT-4o / Claude 3.5 Sonnet | Raciocínio superior para síntese. |
| **Eval** | Ragas | Padrão de mercado para métricas RAG. |

### 🧠 Mudanças Mentais Necessárias
- **Busca Semântica não é Mágica:** Ela falha em "termos exatos" (IDs, SKUs). Por isso usamos Hybrid Search.
- **Garbage In, Garbage Out:** Se seu chunking cortar a frase no meio, o LLM não vai entender. Invista tempo na Ingestão.

### 📚 Referências Recomendadas
* [LangChain - Text splitters](https://python.langchain.com/docs/how_to/#text-splitters): Lista de diferentes divididores de texto no LangChain.
* [Sentence Transformers library](https://www.sbert.net/): Biblioteca popular para modelos de embedding.
* [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard): Leaderboard para modelos de embedding.
* [The Top 7 Vector Databases](https://www.datacamp.com/blog/the-top-5-vector-databases) por Moez Ali: Comparação dos melhores bancos de dados vetoriais.
* [Llamaindex - High-level concepts](https://docs.llamaindex.ai/en/stable/getting_started/concepts.html): Conceitos principais de RAG.
* [Model Context Protocol](https://modelcontextprotocol.io/introduction): Introdução ao MCP.
* [Pinecone - Retrieval Augmentation](https://www.pinecone.io/learn/series/langchain/langchain-retrieval-augmentation/): Visão geral de RAG.
* [LangChain - Q&A with RAG](https://python.langchain.com/docs/tutorials/rag/): Tutorial passo-a-passo de RAG.
* [LangChain - Query Construction](https://blog.langchain.dev/query-construction/): Tipos de construção de consulta.
* [LangChain - SQL](https://python.langchain.com/docs/tutorials/sql_qa/): Interagindo com SQL via LLMs.
* [Pinecone - LLM agents](https://www.pinecone.io/learn/series/langchain/langchain-agents/): Introdução a agentes e ferramentas.
* [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) por Lilian Weng: Artigo teórico sobre agentes.
* [DSPy in 8 Steps](https://dspy-docs.vercel.app/docs/building-blocks/solving_your_task): Guia de DSPy.

---

### [🔹 Bloco 3: Agentes de IA](./03-ai-agents)
Agentes não são mágicos. São **Sistemas de Software** com **Autonomia Controlada**.

#### [Módulo 01: O que são Agentes de IA (Realmente)](./03-ai-agents/01-agent-definitions)
- **Definição:** A diferença entre um Workflow (RAG) e um Agente (Loop de Raciocínio).
- **Realidade:** Por que a maioria das demos de agentes falha miseravelmente em produção.
- **Spectrum:** De "Router Simples" a "Multi-Agent Swarm".

#### [Módulo 02: Arquiteturas de Agentes](./03-ai-agents/02-agent-architectures)
- **Patterns:** ReAct, Plan-and-Solve, Reflection.
- **Design:** Agentes Reativos vs Agentes Deliberativos.
- **Tradeoffs:** Quando usar um grafo (LangGraph) vs uma chain linear.

#### [Módulo 03: LangChain v1 para Agentes](./03-ai-agents/03-langchain-agents)
- **Tool Calling:** Como definir ferramentas com schemas Pydantic rigorosos.
- **Structured Output:** Forçando o agente a responder JSON validado, não texto livre.
- **Controle:** Separando o Prompt do Sistema da execução da ferramenta.

#### [Módulo 04: LangGraph (O Coração)](./03-ai-agents/04-langgraph-orchestration)
- **State Machines:** Por que abandonamos "Chains" e usamos "Grafos de Estado".
- **Controle de Fluxo:** Loops, condicionais, retries e persistência de estado.
- **Orquestração:** Como desenhar um fluxo que se recupera de erros sozinho.

#### [Módulo 05: Sistemas de Memória](./03-ai-agents/05-memory-systems)
- **Short-term:** O contexto da conversa atual.
- **Long-term:** Usando Vector DBs para lembrar preferências do usuário meses depois.
- **Engenharia:** Memória como um problema de Engenharia de Dados, não de prompt.

#### [Módulo 06: MCP (Model Context Protocol)](./03-ai-agents/06-mcp-protocol)
- **O Novo Padrão:** Padronizando como IAs se conectam a dados (Slack, GitHub, Postgres).
- **Desacoplamento:** Trocando o modelo sem quebrar a integração com as ferramentas.

#### [Módulo 07: Single-Agent vs Multi-Agent](./03-ai-agents/07-multi-agent-systems)
- **O Mito:** "Mais agentes = Melhor". (Geralmente é mentira).
- **Padrões de Delegação:** Supervisor, Hierárquico e Colaborativo.
- **Custo:** Como sistemas multi-agente multiplicam latência e tokens.

#### [Módulo 08: Avaliação & Segurança](./03-ai-agents/08-safety-evals)
- **Perigos:** Loops infinitos, Alucinação de Tools, Prompt Injection.
- **Guardrails:** Colocando cercas elétricas em volta do agente.
- **Timeouts:** Nunca deixe um agente rodar para sempre.

#### [Módulo 09: Human-in-the-Loop](./03-ai-agents/09-human-in-the-loop)
- **Aprovação:** O agente *propõe* uma ação (enviar email), o humano *aprova*.
- **Interrupção:** Como pausar o grafo e esperar input do usuário.
- **Auditoria:** Quem autorizou essa transação?

#### [Módulo 10: Agentes em Produção](./03-ai-agents/10-agents-in-production)
- **Observabilidade:** Rastreando o pensamento do agente passo-a-passo (Langfuse).
- **Versionamento:** Como fazer deploy de uma nova versão do "cérebro".
- **Rollback:** O que fazer quando o agente enlouquece sexta-feira à noite.

---

### 🛠️ Stack de Agentes (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Orquestração** | LangGraph | Controle de estado, loops e persistência nativa. |
| **Definição de Tools** | Pydantic v2 | Validação rigorosa de input/output. |
| **Modelo** | GPT-4o / Claude 3.5 Sonnet | Modelos "inteligentes" são obrigatórios para agentes complexos. |
| **Memória** | Redis / Postgres | Persistência de estado rápida e confiável. |
| **Protocolo** | MCP | Para conectar com ferramentas externas de forma padronizada. |
| **Tracing** | Langfuse | Visualizar o loop de pensamento é vital. |

### 🧠 Mudanças Mentais Necessárias
- **Determinismo Morreu:** Agentes são probabilísticos. Seu código precisa lidar com incerteza.
- **Mais Código, Menos Prompt:** A lógica de controle deve estar em Python (Edges do Grafo), não no Prompt.
- **Falha é o Padrão:** O agente VAI errar. O sistema deve ser desenhado para se recuperar.

### 📚 Referências Recomendadas
* [Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction): Curso popular sobre agentes da Hugging Face.
* [LangGraph](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/): Como construir agentes com LangGraph.
* [LlamaIndex Agents](https://docs.llamaindex.ai/en/stable/use_cases/agents/): Agentes com LlamaIndex.

---

### [🔹 Bloco 4: Infraestrutura & Modelos](./04-infra-ocr-models)
Onde a engenharia de software encontra o "Metal". Rodando modelos de forma eficiente e barata.

#### [Módulo 01: Ecossistema Moderno de Modelos](./04-infra-ocr-models/01-model-ecosystem)
- **Decisão:** API Proprietária (OpenAI/Anthropic) vs Open Source (Llama/Mistral).
- **Critérios:** Privacidade, Latência, Custo e Complexidade Operacional.
- **Estratégia:** "Good Enough" models e padrões de roteamento.

#### [Módulo 02: Ecossistema Hugging Face](./04-infra-ocr-models/02-hugging-face)
- **Abase:** O que são Safetensors, Tokenizers e Transformers na prática.
- **Formatos:** FP16, INT8, GGUF, AWQ. O que usar e quando.
- **Realidade:** Quando o Hugging Face é essencial e quando é complexidade desnecessária.

#### [Módulo 03: Ollama (Dev Locals)](./04-infra-ocr-models/03-ollama)
- **Prototipagem:** Como rodar Llama 3 no seu MacBook em 5 minutos.
- **Limites:** Por que você (provavelmente) não deve usar Ollama em produção de alta escala.
- **Workflow:** De local (Ollama) para staging (vLLM).

#### [Módulo 04: vLLM (Inferência de Produção)](./04-infra-ocr-models/04-vllm)
- **O Padrão:** Continuous Batching e PagedAttention.
- **Servindo:** Como subir um servidor compatível com OpenAI API que aguenta 1000 requests/seg.
- **Tunning:** Ajustando KV Cache e Max Tokens para throughput máximo.

#### [Módulo 05: Hardware & Performance](./04-infra-ocr-models/05-hardware-performance)
- **VRAM is King:** Por que a memória da GPU importa mais que o Compute.
- **Unit Economics:** Quanto custa 1 milhão de tokens self-hosted vs API?
- **Quantização:** As trocas entre precisão e velocidade.

#### [Módulo 06: Fundamentos de OCR](./04-infra-ocr-models/06-ocr-fundamentals)
- **A Mentira:** OCR não é apenas extrair texto. É extrair layout, tabelas e estrutura.
- **Desafios:** Rotação, ruído, caligrafia e formatação complexa.
- **Métricas:** Quando CER/WER importam e quando são irrelevantes.

#### [Módulo 07: Frameworks e Pipelines de OCR](./04-infra-ocr-models/07-ocr-pipelines)
- **Ferramentas:** Tesseract vs Azure DI vs Vision LLMs (GPT-4o).
- **Arquitetura:** Pré-processamento, OCR, Pós-processamento e Chunking.
- **Tradeoffs:** Custo (Vision LLM) vs Qualidade vs Velocidade.

#### [Módulo 08: Document Intelligence em Produção](./04-infra-ocr-models/08-document-intelligence)
- **End-to-End:** Ingestão, Fila (SQS), Processamento Idempotente e Indexação.
- **Falhas:** Dead Level Queues e estratégias de retry.
- **Monitoramento:** Como saber se o seu pipeline de PDF parou.

---

### 🛠️ Stack de Infra (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Inferência Local** | Ollama | DX imbatível para desenvolvimento. |
| **Inferência Prod** | vLLM | Padrão ouro para throughput em GPUs NVIDIA. |
| **Model Registry** | Hugging Face | O GitHub dos modelos. |
| **Container** | Docker (NVIDIA Runtime) | Isolamento e portabilidade. |
| **OCR** | Híbrido (Layout Parser + Vision LLM) | Melhor custo-benefício para documentos complexos. |

### 🧠 Mudanças Mentais Necessárias
- **GPU não é CPU:** O gargalo quase sempre é largura de banda de memória (VRAM Bandwidth), não FLOPs.
- **Pipeline > Modelo:** Um modelo médio com um pipeline de dados excelente bate um modelo state-of-the-art com dados ruins.
- **Assíncrono é Obrigatório:** Modelos são lentos. OCR é lento. Se seu sistema for síncrono, ele vai cair.

### 📚 Referências Recomendadas
* [GPU Inference](https://huggingface.co/docs/transformers/main/en/perf_infer_gpu_one) por Hugging Face: Otimizando inferência em GPUs.
* [LLM Inference](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices) por Databricks: Melhores práticas de inferência.
* [Optimizing LLMs for Speed and Memory](https://huggingface.co/docs/transformers/main/en/llm_tutorial_optimization): Quantização, Flash Attention, etc.
* [Assisted Generation](https://huggingface.co/blog/assisted-generation): Decodificação especulativa.
* [EAGLE-3 paper](https://arxiv.org/abs/2503.01840?utm_source=chatgpt.com): Paper do EAGLE-3.
* [Speculators](https://github.com/vllm-project/speculators): Biblioteca vLLM para decodificação especulativa.
* [Streamlit - Build a basic LLM app](https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps): Tutorial de app Streamlit.
* [HF LLM Inference Container](https://huggingface.co/blog/sagemaker-huggingface-llm): Deploy no SageMaker.
* [Philschmid blog](https://www.philschmid.de/): Artigos sobre deploy de LLMs.
* [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/): Vulnerabilidades críticas.
* [Prompt Injection Primer](https://github.com/jthack/PIPE): Guia de prompt injection.
* [Red teaming LLMs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/red-teaming): Guia de red teaming da Microsoft.

---

### [🔹 Bloco 5: Fine-Tuning](./05-fine-tuning)
Onde a engenharia de software encontra a especialização. Saber quando treinar — e principalmente quando NÃO treinar.

#### [Módulo 01: O que é Fine-Tuning (Realmente)](./05-fine-tuning/01-finetuning-concepts)
- **Realidade:** Adaptação de pesos vs Injeção de Conhecimento.
- **Mito:** "Vou treinar o modelo nos meus PDFs para ele saber sobre minha empresa." (Spoiler: Não vai funcionar).
- **Fato:** Fine-Tuning ensina o modelo a FALAR como um médico, não a SER um médico.

#### [Módulo 02: Fine-Tuning vs RAG vs Prompting](./05-fine-tuning/02-rag-vs-finetuning)
- **Matriz de Decisão:** O framework definitivo para escolher a abordagem.
- **RAG:** Para fatos novos e dinâmicos.
- **Fine-Tuning:** Para estilo consistente e redução de latência/custo.
- **Prompting:** Onde você deve gastar 90% do seu tempo inicial.

#### [Módulo 03: Tipos de Adaptação](./05-fine-tuning/03-adaptation-types)
- **Full Fine-Tuning:** Por que você quase nunca vai fazer isso.
- **PEFT / LoRA:** Como treinar modelos gigantes com pouco VRAM.
- **Instruction Tuning:** Ensinando o modelo a seguir ordens.
- **Likelihood Training (DPO/ORPO):** Ensinando o modelo o que você prefere.

#### [Módulo 04: Dados são o Modelo](./05-fine-tuning/04-data-prep)
- **A Verdade:** O modelo é apenas um espelho dos seus dados.
- **Qualidade > Quantidade:** 100 exemplos perfeitos valem mais que 10.000 exemplos ruins.
- **Instruction Datasets:** Como formatar seus dados corretamente.

#### [Módulo 05: Avaliação antes do Treino](./05-fine-tuning/05-evaluation)
- **Regra:** Se você não consegue medir, não treine.
- **Baselines:** Como saber se o treino piorou o modelo (Catastrophic Forgetting).
- **LLM-as-a-Judge:** Usando GPT-4 para dar nota no seu Llama-3 finetunado.

#### [Módulo 06: Unsloth (Prático)](./05-fine-tuning/06-unsloth)
- **A Ferramenta:** Por que Unsloth é o padrão ouro hoje.
- **Eficiência:** Treinando 2x mais rápido com 70% menos memória.
- **Workflow:** Do notebook para o GGUF/LoRA Adapter.

#### [Módulo 07: Infra de Treino & Custo Real](./05-fine-tuning/07-training-ops)
- **Hardware:** Quanto de VRAM você realmente precisa.
- **Spot Instances:** Economizando 70% na AWS/RunPod.
- **Custo Oculto:** O tempo de engenharia para limpar dados vs o custo de GPU.

#### [Módulo 08: Deploy & Inferência Pós-Treino](./05-fine-tuning/08-deploy-adapters)
- **Adapters:** Como carregar LoRA adapters no vLLM sem duplicar o modelo base.
- **Merge:** Quando fundir os pesos (Mergekit) e quando carregar dinamicamente.
- **Drift:** Monitorando se o modelo "desaprendeu" coisas importantes.

#### [Módulo 09: Riscos & Manutenção](./05-fine-tuning/09-risks-maintenance)
- **Catastrophic Forgetting:** O modelo ficou ótimo em SQL, mas esqueceu como falar inglês.
- **Manutenção:** Modelo treinado é modelo "congelado". Como atualizar?

#### [Módulo 10: Enterprise & Gov](./05-fine-tuning/10-enterprise-gov)
- **Compliance:** Quando o Fine-Tuning é obrigatório por lei (On-premise total).
- **Privacidade:** Garantindo que dados sensíveis não vazem.

---

### 🛠️ Stack de Treino (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Framework** | Unsloth | Velocidade e eficiência de memória imbatíveis. |
| **Técnica** | QLoRA (4-bit) | Permite treinar 70B em GPUs "baratas" (A6000/A100). |
| **Eval** | Ragas / LLM-as-Judge | Avaliação escalável antes de deploy. |
| **Dataset** | Hugging Face Datasets | Gerenciamento e versionamento de dados. |

### 🧠 Mudanças Mentais Necessárias
- **Menos é Mais:** Comece com 50 exemplos. Teste. Se melhorar, adicione mais.
- **Dados são Código:** Trate seu dataset com o mesmo rigor que trata seu código (versionamento, code review, linting).
- **Você provavelmente não precisa de Fine-Tuning:** Sério. RAG + Few-Shot Prompting resolve 95% dos casos.

---

## 🏗️ Arquitetura & Filosofia
Este repositório é construído como um **Monorepo** representando uma Plataforma de IA Enterprise completa.

- **Production-First:** Todo exemplo trata erros, logs e variáveis de ambiente.
- **Escalável:** Estrutura de pastas que você veria na Netflix, Uber ou startups de alto crescimento.
- **Opinativo:** Escolhemos o stack que *funciona* (ex: Pydantic sobre dataclasses, FastAPI sobre Flask).

> **"Amadores falam sobre algoritmos. Profissionais falam sobre logística (infraestrutura, custo, latência)."**

---

## 🚀 Como Começar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seususuario/ai-engineer-roadmap.git
   cd ai-engineer-roadmap
   ```

2. **Configure o ambiente (usando `uv`):**
   ```bash
   # Recomendamos uv pela velocidade
   uv venv
   source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
   uv pip install -r requirements.txt
   ```

3. **Navegue para o Bloco 1:**
   ```bash
   cd 01-foundations
   ```

## 🤝 Contribuindo
Exigimos padrões altos. Este não é um lugar para scripts "hello world".

## 📝 Licença
MIT. Construa coisas incríveis. Ganhe dinheiro. Mude o mundo.

## 🙏 Agradecimentos

Este roadmap foi inspirado no excelente [DevOps Roadmap](https://github.com/milanm/DevOps-Roadmap) de Milan Milanović e Romano Roth.

Agradecimentos especiais a:
* Thomas Thelen por me motivar a criar um roadmap
* André Frade por sua contribuição e revisão do primeiro esboço
* Dino Dunn por fornecer recursos sobre segurança LLM
* Magdalena Kuhn por melhorar a parte de "avaliação humana"
* Odoverdose por sugerir o vídeo de 3Blue1Brown sobre Transformers
* Todos que contribuíram para as referências educacionais neste curso :)

*Aviso Legal: Eu não sou afiliado a nenhuma fonte listada aqui.*
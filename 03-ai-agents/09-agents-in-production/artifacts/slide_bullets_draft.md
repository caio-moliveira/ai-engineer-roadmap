# Draft — Course Slides (bullets)

## 1) Capa
- Construção profissional de sistemas de IA, RAG e agentes em produção
- Arquitetura, orquestração, observabilidade e deploy
- De desenvolvedor → AI Engineer

## 3) Course intro
- AI Engineer: arquiteta contexto, dados, fluxos e validações para LLMs
- Transformar probabilístico → determinístico e confiável
- Domínios práticos: Python assíncrono, APIs, dados, Vector DB, observabilidade
- Desafios reais: alucinações, custos, latência e segurança

## 4) Bloco 1 intro
- Base técnica para sistemas probabilísticos, assíncronos e orientados a produção
- Contratos estruturados para outputs de LLM (Pydantic/JSON Schema)
- APIs assíncronas e integração com RAG/Modelos
- Armazenamento híbrido: SQL + Vector DB

## 5) Bloco 1 (síntese)
- Papel profissional e mindset de produto/sistemas
- Física dos LLMs + estratégias (quando RAG vs fine-tuning)
- Python moderno: tipagem, AsyncIO, resiliência (retries)
- FastAPI: contratos, validação e OpenAPI
- Modelagem e contratos de dados: schemas, validadores e parsing com retries
- Databases: embeddings, métricas (cosseno/dot) e arquitetura híbrida SQL+Vetorial

## 6) Bloco 2 intro
- Objetivo: conectar LLMs aos seus dados privados
- Arquitetura mais comum em produção
- Pipeline: Ingestão → Store → Retrieve → Generate
- Avaliação e observabilidade como parte do sistema

## 7) Bloco 2 (síntese)
- Ingestão/ETL e chunking + metadados
- Embeddings e suporte a multimodalidade linguística
- Vector DBs (Qdrant/pgvector) e indexação (HNSW)
- Retrieval: hybrid search, reranking e query expansion
- RAG Agents e Graph RAG
- Avaliação (RAGAS) + tracing + produção (segurança/custos)

## 8) Bloco 3 intro
- Agentes têm autonomia controlada
- Fronteira da Engenharia de IA (2026)
- Tool calling + state machines + guardrails
- Observabilidade e human-in-the-loop

## 9) Bloco 3 (síntese)
- Workflow vs agente + padrões (ReAct/Plan-Solve/Reflection)
- Tool calling com schemas e structured outputs
- LangGraph: grafos de estado, loops, retries e persistência
- Memória: curto vs longo prazo
- Integrações via MCP
- Human-in-the-loop
- Multi-agents: delegação e custo
- Guardrails e avaliação
- Produção: deploy/monitoramento

## 10) Bloco 4 intro
- Rodar modelos eficiente, barata e confiavelmente
- OCR moderno: layout/tabelas/estrutura
- Performance: GPU (VRAM), throughput e unit economics

## 11) Bloco 4 (síntese)
- OCR Fundamentals: layout, ruído e métricas
- OCR Pipelines: pré/pós, chunking e tradeoffs
- Document Intelligence: fila, idempotência, retries e monitoramento
- Hugging Face: formatos/quantização e Transformers
- Ollama (protótipo) e workflow local→staging
- vLLM: serving e throughput
- Hardware & Performance: VRAM, quantização e economia

## 12) Bloco 5 intro
- Saber quando treinar — e principalmente quando NÃO treinar
- Especialização como última milha
- LoRA/QLoRA e dataset curation
- Deploy, riscos e governança

## 13) Bloco 5 (síntese)
- Fine-tuning vs RAG/prompting (matriz de decisão)
- Adaptação: PEFT/LoRA/QLoRA/full
- Unsloth workflow eficiente
- Dataset engineering
- Avaliação: baselines e LLM-as-a-Judge
- Deploy: adapters no vLLM e merge
- Produção: ops/custos, riscos e compliance

## 14) Conclusão
- Conexão dos blocos para sistemas operáveis em produção
- Fundamentos → RAG → Agentes → OCR/Infra → Fine-tuning

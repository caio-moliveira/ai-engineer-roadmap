# 🧭 O Guia Definitivo do Engenheiro de IA

> **De Iniciante a Engenheiro de IA em Produção.**  
> *A diferença entre rodar um notebook e construir um sistema.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 A Missão
Este repositório é o manual definitivo, "livre de hype", para construir sistemas de IA que funcionam no mundo real.

Ele foi desenhado para:
- **Engenheiros de Software** migrando para IA.
- **Cientistas de Dados** que precisam colocar modelos em produção.
- **CTOs & Tech Leads** definindo seu stack de IA.

### 🚫 O que este guia NÃO é
- ❌ **Não é Acadêmico:** Sem provas matemáticas, sem teoria inútil.
- ❌ **Não é Teórico:** Se não roda em produção, não está aqui.
- ❌ **Não é apenas Código:** É sobre **Modelos Mentais**, **Arquitetura** e **Confiabilidade**.

---

## 📚 A Jornada (O Sistema de Blocos)
Seguimos uma progressão estrita. Não pule etapas.

### [🔹 Bloco 1: Fundamentos Reais](./01-fundamentals)
Onde tudo começa. Esqueça Jupyter Notebooks.
- **Tópicos:** Python Assíncrono, FastAPI, Docker, `uv`, Pydantic, Engenharia de Software para IA.

### [🔹 Bloco 2: Sistemas RAG](./02-rag-systems)
Retrieval Augmented Generation é o feijão com arroz da IA moderna.
- **Tópicos:** Vector DBs (Qdrant), Retrievers Avançados, Reranking, Busca Híbrida, Observabilidade.

### [🔹 Bloco 3: Agentes de IA](./03-ai-agents)
O futuro da automação. De ferramentas simples a sistemas autônomos.
- **Tópicos:** LangGraph, Tool Calling, MCP (Model Context Protocol), Memória, Human-in-the-loop.

### [🔹 Bloco 4: Infraestrutura & Modelos](./04-infra-ocr-models)
Rodando modelos com eficiência e lidando com dados não estruturados.
- **Tópicos:** vLLM, Ollama, HuggingFace, Otimização de Inferência, Document AI (OCR).

### [🔹 Bloco 5: Fine-Tuning](./05-fine-tuning)
Quando o RAG não é suficiente. A arte de customizar modelos.
- **Tópicos:** Unsloth, PEFT/LoRA, Curadoria de Datasets, Análise de Custo-Benefício.

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
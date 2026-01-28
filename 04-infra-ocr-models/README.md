# 🔹 Bloco 4: Infra, OCR e Modelos (Inferência em Produção)

> **Objetivo:** Rodar modelos de forma eficiente, barata e confiável.  
> **Status:** Onde a engenharia de software encontra o "Metal".

## 🛑 Pare. Leia isto.
Este bloco não é sobre "como treinar modelos".  
É sobre **como operar modelos**.

A maioria dos projetos de IA morre porque:
1.  **Custo:** A conta da AWS/OpenAI torna o produto inviável.
2.  **Latência:** O usuário desiste de esperar 10 segundos pela resposta.
3.  **Dados Sujos:** O pipeline de OCR falha em ler o PDF do cliente.

Aqui você vai aprender a ser um **Engenheiro de Infraestrutura de IA**.

---

## 📚 Ementa do Módulo

### [Módulo 1: Ecossistema Moderno de Modelos](./01-model-ecosystem)
- **Decisão:** API Proprietária (OpenAI/Anthropic) vs Open Source (Llama/Mistral).
- **Critérios:** Privacidade, Latência, Custo e Complexidade Operacional.
- **Estratégia:** "Good Enough" models e padrões de roteamento.

### [Módulo 2: Ecossistema Hugging Face](./02-hugging-face)
- **Abase:** O que são Safetensors, Tokenizers e Transformers na prática.
- **Formatos:** FP16, INT8, GGUF, AWQ. O que usar e quando.
- **Realidade:** Quando o Hugging Face é essencial e quando é complexidade desnecessária.

### [Módulo 3: Ollama (Dev Locals)](./03-ollama)
- **Prototipagem:** Como rodar Llama 3 no seu MacBook em 5 minutos.
- **Limites:** Por que você (provavelmente) não deve usar Ollama em produção de alta escala.
- **Workflow:** De local (Ollama) para staging (vLLM).

### [Módulo 4: vLLM (Inferência de Produção)](./04-vllm)
- **O Padrão:** Continuous Batching e PagedAttention.
- **Servindo:** Como subir um servidor compatível com OpenAI API que aguenta 1000 requests/seg.
- **Tunning:** Ajustando KV Cache e Max Tokens para throughput máximo.

### [Módulo 5: Hardware & Performance](./05-hardware-performance)
- **VRAM is King:** Por que a memória da GPU importa mais que o Compute.
- **Unit Economics:** Quanto custa 1 milhão de tokens self-hosted vs API?
- **Quantização:** As trocas entre precisão e velocidade.

### [Módulo 6: Fundamentos de OCR](./06-ocr-fundamentals)
- **A Mentira:** OCR não é apenas extrair texto. É extrair layout, tabelas e estrutura.
- **Desafios:** Rotação, ruído, caligrafia e formatação complexa.
- **Métricas:** Quando CER/WER importam e quando são irrelevantes.

### [Módulo 7: Frameworks e Pipelines de OCR](./07-ocr-pipelines)
- **Ferramentas:** Tesseract vs Azure DI vs Vision LLMs (GPT-4o).
- **Arquitetura:** Pré-processamento, OCR, Pós-processamento e Chunking.
- **Tradeoffs:** Custo (Vision LLM) vs Qualidade vs Velocidade.

### [Módulo 8: Document Intelligence em Produção](./08-document-intelligence)
- **End-to-End:** Ingestão, Fila (SQS), Processamento Idempotente e Indexação.
- **Falhas:** Dead Level Queues e estratégias de retry.
- **Monitoramento:** Como saber se o seu pipeline de PDF parou.

---

## 🛠️ Stack de Infra (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Inferência Local** | Ollama | DX imbatível para desenvolvimento. |
| **Inferência Prod** | vLLM | Padrão ouro para throughput em GPUs NVIDIA. |
| **Model Registry** | Hugging Face | O GitHub dos modelos. |
| **Container** | Docker (NVIDIA Runtime) | Isolamento e portabilidade. |
| **OCR** | Híbrido (Layout Parser + Vision LLM) | Melhor custo-benefício para documentos complexos. |

## 🧠 Mudanças Mentais Necessárias
- **GPU não é CPU:** O gargalo quase sempre é largura de banda de memória (VRAM Bandwidth), não FLOPs.
- **Pipeline > Modelo:** Um modelo médio com um pipeline de dados excelente bate um modelo state-of-the-art com dados ruins.
- **Assíncrono é Obrigatório:** Modelos são lentos. OCR é lento. Se seu sistema for síncrono, ele vai cair.

## 🚀 Como começar
Vá para **[Módulo 1: Ecossistema Moderno de Modelos](./01-model-ecosystem)**.

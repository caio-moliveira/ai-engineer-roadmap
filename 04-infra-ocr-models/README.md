<div align="center">
    <img src="../assets/jornada.png" alt="Jornada de Dados" width="200"/>

# 🔹 Bloco 4: Infra, OCR e Modelos (Inferência em Produção)

> **Objetivo:** Rodar modelos de forma eficiente, barata e confiável.  
> **Status:** Onde a engenharia de software encontra o "Metal".

<p align="center">
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  </a>
  <a href="https://docling-project.github.io/docling/">
    <img alt="Docling" src="https://img.shields.io/badge/Docling-Document%20AI-2563EB?style=for-the-badge" />
  </a>
  <a href="https://huggingface.co/docs/transformers">
    <img alt="Hugging Face" src="https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000000" />
  </a>
  <a href="https://ollama.com/">
    <img alt="Ollama" src="https://img.shields.io/badge/Ollama-Local%20LLMs-000000?style=for-the-badge" />
  </a>
  <a href="https://github.com/vllm-project/vllm">
    <img alt="vLLM" src="https://img.shields.io/badge/vLLM-High%20Performance%20Inference-0EA5E9?style=for-the-badge" />
  </a>
  <a href="https://www.deepseek.com/">
    <img alt="DeepSeek" src="https://img.shields.io/badge/DeepSeek-VLM%20Models-111111?style=for-the-badge" />
  </a>
  <a href="https://huggingface.co/Qwen">
    <img alt="Qwen" src="https://img.shields.io/badge/Qwen-VLM%20Models-F97316?style=for-the-badge" />
  </a>
  <a href="https://github.com/unslothai/unsloth">
    <img alt="Unsloth" src="https://img.shields.io/badge/Unsloth-Fast%20Fine--Tuning-10B981?style=for-the-badge" />
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img alt="uv" src="https://img.shields.io/badge/uv-Python%20Package%20Manager-111111?style=for-the-badge&logo=astral&logoColor=white" />
  </a>
</p>

<div align="center">

### Tecnologias e padrões utilizados ao longo do módulo

OCR pipelines • Document AI • Vision-Language Models (VLMs) • parsing de PDFs e imagens  
extração estruturada de documentos • inferência local de modelos • otimização de hardware  
processamento de documentos em larga escala • avaliação de extração de dados

</div>


<div align="center">
<img src="../assets/ocr.png" alt="OCR" width="1000"/>
</div>

</div>
</div>




## 📚 Ementa do Módulo

### [Módulo 1: OCR Fundamentals](./01-ocr-fundamentals)
- **A Mentira:** OCR não é apenas extrair texto. É extrair layout, tabelas e estrutura.
- **Desafios:** Rotação, ruído, caligrafia e formatação complexa.
- **Métricas:** Quando CER/WER importam e quando são irrelevantes.

### [Módulo 2: OCR Pipelines](./02-ocr-pipelines)
- **Ferramentas:** Tesseract vs Azure DI vs Vision LLMs (GPT-4o).
- **Arquitetura:** Pré-processamento, OCR, Pós-processamento e Chunking.
- **Tradeoffs:** Custo (Vision LLM) vs Qualidade vs Velocidade.

### [Módulo 3: Document Intelligence](./03-document-intelligence)
- **End-to-End:** Ingestão, Fila (SQS), Processamento Idempotente e Indexação.
- **Falhas:** Dead Level Queues e estratégias de retry.
- **Monitoramento:** Como saber se o seu pipeline de PDF parou.

### [Módulo 4: Hugging Face](./04-hugging-face)
- **A Base:** O que são Safetensors, Tokenizers e Transformers na prática.
- **Formatos:** FP16, INT8, GGUF, AWQ. O que usar e quando.

### [Módulo 5: Ollama](./05-ollama)
- **Prototipagem:** Como rodar Llama 3 no seu MacBook em 5 minutos.
- **Limites:** Por que você (provavelmente) não deve usar Ollama em produção de alta escala.
- **Workflow:** De local (Ollama) para staging (vLLM).

### [Módulo 6: vLLM](./06-vllm)
- **O Padrão:** Continuous Batching e PagedAttention.
- **Servindo:** Como subir um servidor compatível com OpenAI API que aguenta 1000 requests/seg.
- **Tunning:** Ajustando KV Cache e Max Tokens para throughput máximo.

### [Módulo 7: Hardware & Performance](./07-hardware-performance)
- **VRAM is King:** Por que a memória da GPU importa mais que o Compute.
- **Unit Economics:** Quanto custa 1 milhão de tokens self-hosted vs API?
- **Quantização:** As trocas entre precisão e velocidade.

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
Vá para **[Módulo 1: OCR Fundamentals](./01-ocr-fundamentals)**.

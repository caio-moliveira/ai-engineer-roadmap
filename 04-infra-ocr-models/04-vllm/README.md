# 🚀 Módulo 4: vLLM (Core de Inferência)

> **Goal:** Extrair máximo de tokens por segundo da sua GPU.  
> **Status:** O padrão industrial para self-hosting.

## 1. Por que vLLM?
Servir LLMs é difícil por causa da memória.
O **KV Cache** (memória da conversa) cresce e diminui dinamicamente.
Engines antigas alocavam memória estática (desperdiçavam VRAM).
**vLLM** introduziu **PagedAttention** (inspirado em memória virtual de OS), permitindo ocupar 95% da VRAM com eficiência.

**Resultado:** 20x mais throughput que HuggingFace Transformers padrão.

## 2. Conceitos Core
- **Continuous Batching:** Não espera um pedido terminar para começar outro. Encaixa novos pedidos nos "buracos" de processamento.
- **Quantization (AWQ/GPTQ):** vLLM roda modelos quantizados de forma super otimizada.

## 3. Pattern de Deploy (Docker)
Não instale vLLM no bare metal. Use Docker.

```yaml
services:
  llm:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    environment:
      - HUGGING_FACE_HUB_TOKEN=...
    command: --model meta-llama/Meta-Llama-3-8B-Instruct --quantization awq --max-model-len 4096
    ports:
      - "8000:8000"
```

## 4. Confiabilidade em Produção
- **Max Tokens:** Limite isso! Se um usuário pedir 1 milhão de tokens, seu servidor trava.
- **Timeout:** Configure timeouts agressivos no cliente.
- **Load Shedding:** Se a fila estiver cheia (HTTP 503), rejeite novos requests imediatamente para não derrubar o serviço.

## 🧠 Mental Model: "O Ônibus Lotado"
O Continuous Batching é como um ônibus.
Em vez de esperar o ônibus esvaziar para pegar novos passageiros, o vLLM deixa gente entrar e sair em cada ponto (token). O ônibus está sempre cheio (GPU sempre em 100%), maximizando a eficiência.

## ⏭️ Próximo Passo
Quanto custa esse ônibus?
Vá para **[Módulo 5: Hardware & Performance](../05-hardware-performance)**.

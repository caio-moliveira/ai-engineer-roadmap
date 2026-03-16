# 🤗 Módulo 2: Ecossistema Hugging Face (Prático)

> **Goal:** O GitHub da IA.  
> **Status:** Essencial para quem não usa apenas APIs.

## 1. O que o HF realmente oferece?
Não é só um site para baixar modelos. É a infraestrutura padrão.
- **Transformers:** A lib Python padrão para rodar qualquer modelo.
- **Tokenizers:** Quem transforma texto em números.
- **Safetensors:** O formato de arquivo seguro (sem pickle/execução de código).

## 2. Model Formats (O que quebra?)
Você baixou um modelo e deu erro de RAM. Por quê?

- **FP32 (Float 32):** Precisão total. Gigante. (4 bytes por parâmetro). Ninguém usa em inferência.
- **FP16 / BF16:** Padrão de treino/inferência. (2 bytes por parâmetro).
- **INT8 / INT4 (Quantização):** Compressão absurda. Perda mínima de qualidade. Essencial para rodar em GPUs "normais".

## 3. GGUF (O formato Local)
Criado por Georgi Gerganov (llama.cpp).
- **Goal:** Rodar em CPU + Apple Silicon.
- **Como funciona:** Mapeia o modelo direto na memória (mmap).
- **Uso:** Use com Ollama ou LM Studio. Não use em produção de alta performance (prefira AWQ/GPTQ em vLLM).

## 4. O Checklist "HF em Produção"
Se for baixar do HF para produção:
- [ ] Use `.safetensors` (nunca `.bin` ou `.pt` se possível, risco de segurança).
- [ ] Verifique a licença (Apache 2.0 / MIT vs Llama Community).
- [ ] Cache: Configure `HF_HOME` para não lotar seu disco de OS.

## 🧠 Mental Model: "Pesos Congelados"
Um modelo no HF é um arquivo estático de pesos (bilhões de números).
Para "rodar", você precisa de uma **Engine** (vLLM, Ollama, Transformers) que carrega esses números na VRAM e faz as contas de matrizes.

## ⏭️ Próximo Passo
Como rodar isso localmente sem dor de cabeça?
Vá para **[Módulo 3: Ollama](../03-ollama)**.

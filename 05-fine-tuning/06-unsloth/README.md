# 🦥 Módulo 6: Unsloth (Prático)

> **Goal:** O jeito certo de treinar em 2025.  
> **Status:** Essencial.

## 1. O que é Unsloth?
É uma biblioteca que reescreveu os kernels de backpropagation do Llama/Mistral manualmente.
- **Resultado:** Treina 2x mais rápido. Usa 70% menos memória VRAM.
- **Mágica:** Permite treino de contexto longo (8k, 16k) sem estourar a memória.

## 2. O Workflow
1.  **Instalação:** `pip install unsloth`
2.  **Load:** `FastLanguageModel.from_pretrained(..., load_in_4bit=True)`
3.  **PEFT:** `model = FastLanguageModel.get_peft_model(...)`
4.  **Train:** `Trainer.train()` (HuggingFace padrão).
5.  **Save:** `model.save_pretrained("lora_adapters")` e `model.save_pretrained_gguf(...)`.

## 3. Merging vs Adapter
- **Adapter Only (Recomendado):** Salve apenas os 100MB do LoRA. Carregue dinamicamente no vLLM.
- **Merged Model:** Funda os pesos (100MB + 70GB) em um novo arquivo de 70GB. Use apenas se a engine de inferência não suportar LoRA.

## 🧠 Mental Model: "Unsloth é o Turbo"
Não use `bitsandbytes` puro ou `transformers` puro se você puder usar Unsloth.
É a mesma matemática, só que otimizada. Não há perda de precisão.

## ⏭️ Próximo Passo
Onde rodar isso?
Vá para **[Módulo 7: Infra de Treino & Custo Real](../07-training-ops)**.

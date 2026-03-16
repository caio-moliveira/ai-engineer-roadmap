# 🧬 Módulo 3: Tipos de Adaptação (PEFT/LoRA)

> **Goal:** Treinar modelos gigantes em GPUs mortais.  
> **Status:** O estado da arte da eficiência.

## 1. Full Fine-Tuning (O jeito antigo)
Atualiza todos os 70 bilhões de parâmetros.
- **Problema:** Requer centenas de GBs de memória (vários clusters A100).
- **Risco:** Catastrophic Forgetting alto. O modelo esquece o que sabia antes.
- **Uso:** Quase nunca, a menos que você seja a OpenAI ou Google.

## 2. PEFT (Parameter-Efficient Fine-Tuning)
Congela o modelo base. Treina apenas pequenas camadas extras.

### LoRA (Low-Rank Adaptation)
Injeta pequenas matrizes treináveis nas camadas do modelo.
- **Tamanho:** O "adapter" final tem ~100MB.
- **Vantagem:** Você pode ter 1 modelo base e 50 adapters (um para SQL, um para Poesia, um para Jurídico).
- **Custo:** Treina em uma única GPU consumer (RTX 3090/4090).

### QLoRA (Quantized LoRA)
Carrega o modelo base em 4-bit (perda mínima) e treina o LoRA em cima.
- **Revolução:** Permite treinar Llama 3 70B em uma única GPU A100 (80GB) ou 2x RTX 3090.

## 3. Instruction Tuning vs Preference Tuning
- **Instruction Tuning (SFT - Supervised Fine-Tuning):**
    - Dataset: Pergunta -> Resposta Correta.
    - Goal: Ensinar a seguir instruções.
- **Preference Tuning (DPO / ORPO):**
    - Dataset: Pergunta -> Resposta Boa vs Resposta Ruim.
    - Goal: Alinhar o modelo com preferências humanas (evitar toxicidade, verbosidade).

## 🧠 Mental Model: "O Plugin"
Pense no LoRA como um arquivo DLC de um jogo.
O jogo base (Llama 3) tem 70GB.
O DLC (LoRA Adapter) tem 100MB e muda as roupas e diálogos dos personagens.

## ⏭️ Próximo Passo
O segredo não é o algoritmo. É o dataset.
Vá para **[Módulo 4: Dados são o Modelo](../04-data-prep)**.

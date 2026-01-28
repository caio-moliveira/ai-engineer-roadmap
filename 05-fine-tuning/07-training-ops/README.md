# 🏗️ Módulo 7: Infra de Treino & Custo Real

> **Goal:** Não falir a startup.  
> **Status:** FinOps.

## 1. Spot Instances (O Segredo)
Uma GPU A100 80GB custa ~$4.00/hora "On-Demand".
A mesma GPU custa ~$1.30/hora em "Spot" (Leilão).
Como o treinamento com Unsloth leva 1-2 horas para datasets médios, o risco de interrupção é baixo e a economia é brutal.

## 2. Quanto de VRAM eu preciso? (Com Unsloth/QLoRA)
- **Llama-3-8B:** ~8GB VRAM (Cabe na Colab Grátis / RTX 3060).
- **Llama-3-70B:** ~40GB VRAM (Precisa de 1x A6000 ou 1x A100).
- **Gemma-2B:** ~4GB VRAM.

## 3. Checklist: "Vale a pena treinar?"
- Custo de Engenharia (Salário): $1000 (2 dias preparando dados).
- Custo de GPU: $5 (2 horas de A100).
- Custo de Eval: $50 (GPT-4 avaliando).

> **O custo não é a GPU.** É o seu tempo limpando dados.

## 🧠 Mental Model: "A Fábrica"
Não trate treinamento como "Rodei um script no meu notebook".
Trate como uma fábrica.
Matéria Prima (Dados) -> Máquina (Unsloth) -> Controle de Qualidade (Eval) -> Produto (Adapter).

## ⏭️ Próximo Passo
Como colocar isso na frente do usuário?
Vá para **[Módulo 8: Deploy & Inferência Pós-Treino](../08-deploy-adapters)**.

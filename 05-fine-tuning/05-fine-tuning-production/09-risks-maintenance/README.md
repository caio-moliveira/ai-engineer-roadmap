# ⚠️ Módulo 9: Riscos, Falhas & Manutenção

> **Goal:** Gerenciar o ciclo de vida.  
> **Status:** Prevenção de desastres.

## 1. Catastrophic Forgetting
Você treina o modelo para falar "Engraçado".
De repente, ele não sabe mais programar em Python.
**Causa:** O treino alterou pesos que eram cruciais para a lógica, em favor do estilo.
**Solução:** Adicione 10-20% de dados gerais de alta qualidade no seu dataset de treino (Dataset Replay) para "lembrar" o modelo de ser inteligente.

## 2. Data Staleness (Dados Velhos)
Se você treinou o modelo com dados de 2023.
Em 2025, o usuário pergunta "Quem é o presidente?".
O modelo responde com convicção (porque é Fine-Tuning) o nome errado.
**Solução:** NUNCA use FT para fatos temporais. Use RAG.

## 3. Feedback Loops
Se você usa dados gerados pelo modelo para treinar a próxima versão do modelo...
O modelo vai colapsar (Model Collapse). As idiossincrasias se amplificam.
Sempre mantenha dados humanos ou dados de um modelo superior (Oracle) no loop.

## 🧠 Mental Model: "Entropia"
Modelos finetunados tendem a degradar com o tempo se não forem cuidados.
A "inteligência geral" é frágil. Proteja-a.

## ⏭️ Próximo Passo
Como grandes empresas fazem isso?
Vá para **[Módulo 10: Fine-Tuning em Enterprise & Gov](../10-enterprise-gov)**.

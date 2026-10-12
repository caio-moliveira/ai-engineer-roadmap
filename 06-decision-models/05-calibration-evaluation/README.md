# 🎯 Módulo 5: Calibração, Limiares e Avaliação

> **Objetivo:** transformar probabilidade em decisão de engenharia.
> **Pergunta-chave:** com limiar 0,85, quanto você automatiza e com que precisão?

---

## 📚 Índice Prático e Documentação

1. **[Golden set](#1-golden-set)**
   * Exemplo: `01_golden_set.py`
2. **[Calibração](#2-calibração)**
   * Docs: [Guo et al. (2017), On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599) | [scikit-learn: calibração](https://scikit-learn.org/stable/modules/calibration.html)
   * Exemplo: `02_calibration.py`
3. **[Curva de automação](#3-limiar)**
   * Exemplo: `03_threshold_curve.py`
4. **[Harness de comparação justa](#4-o-harness)**
   * Exemplo: `04_fair_comparison.py`
5. **[Gravação de fixtures](#5-replay)**
   * Exemplo: `05_replay_record.py`

---

## 1. Golden set

O gabarito. Sem ele, "o Jev é melhor" ou "o LLM é melhor" é opinião. O formato do bloco tem um item por exemplo, com `state` (o que o modelo vê), `labels` (uma chave por **pergunta**, com o valor certo) e `tags` para fatiar a métrica. O script valida todos os golden sets contra as perguntas de `common/specs.py` e mostra a distribuição.

| Arquivo | Itens | Usado em |
|---|---|---|
| `golden_tickets.json` | 60 tickets de um SaaS fictício | fila, categoria, urgência, rota, multirrótulo, churn |
| `golden_spam.json` | 36 e-mails | spam e seis sinais |
| `golden_sales.json` | 80 perguntas do `workshop-jev` | tool, guardrail, projeto final |
| `golden_verify.json` | 24 respostas de LLM | verificação e qualidade |
| `golden_rerank.json` | 6 perguntas × 10 trechos | rerank |
| `golden_tool_calls.json` | 12 chamadas de tool | gate de risco |

Nenhum dado pessoal real: empresas, domínios e pessoas são fictícios.

## 2. Calibração

| Métrica | O que mede | Bom |
|---|---|---|
| **ECE** | distância média entre confiança e acerto, por faixa | perto de 0 |
| **Brier** | erro quadrático da probabilidade; mistura acerto e calibração | menor |
| **Diagrama de confiabilidade** | confiança média × acurácia por faixa | na diagonal |

A confiança do LLM é autorrelatada. A do Laya multilíngue vem sem calibração de fábrica. O fim do script mostra o remédio clássico, **ajuste de temperatura**: escolhe T numa metade do golden set e mede o ECE na outra.

## 3. Limiar

Acima do limiar, o sistema decide sozinho; abaixo, vai para um humano ou para um modelo maior. A curva mostra a troca entre **% automatizado** e **acurácia no automatizado**.

O limiar é **escolhido numa metade** do golden set e **relatado na outra**. Escolher e relatar no mesmo dado é otimismo garantido. Um provider mal calibrado faz a curva mentir: subir o limiar só reduz a cobertura, sem ganhar acurácia.

## 4. O harness

```bash
python 05-calibration-evaluation/04_fair_comparison.py
python 05-calibration-evaluation/04_fair_comparison.py --tarefas fila,spam --alvos laya,jev --limite 20
```

Mesma spec, mesmos dados, todos os providers. Os tokens vêm da resposta, a latência do relógio e o preço de `common/pricing.yaml`. O harness exporta `saida/comparacao.csv` com uma linha por (tarefa, item, provider). Em modo live, ele estima o custo antes e pede `--confirmar` acima de US$ 1.

## 5. Replay

```bash
python 05-calibration-evaluation/05_replay_record.py                 # grava o que estiver disponível
python 05-calibration-evaluation/05_replay_record.py --alvos jev      # só o Jev
```

Roda cada script com `DECISION_PROVIDER=record`. O que já foi gravado é reaproveitado, então você não paga duas vezes. Depois de gravar, faça um commit explícito (`data: regrava fixtures do jev`).

---

## 🏋️ Exercício

Entregue a curva de automação sobre o **seu** golden set:

1. Monte um golden set de pelo menos 100 itens do seu domínio, com tags de dificuldade.
2. Rode o harness com Jev, Laya e um LLM.
3. Escolha um limiar por provider para a acurácia que o seu negócio exige, numa metade, e relate na outra.
4. Justifique em um parágrafo: quanto custa um erro automatizado e quanto custa mandar para um humano?

## ⏭️ Próximo Passo
Juntando tudo num agente medido ponta a ponta: **[Módulo 6: Projeto final](../06-final-project-hybrid-agent)**.

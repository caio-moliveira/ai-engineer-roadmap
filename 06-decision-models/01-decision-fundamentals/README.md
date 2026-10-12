# 🧭 Módulo 1: Fundamentos de Modelos de Decisão

> **Objetivo:** entender o que é um modelo de decisão, de onde vem e quando usar.
> **Pergunta-chave:** por que gerar texto para responder uma pergunta de múltipla escolha?

---

## 📚 Índice Prático e Documentação

1. **[A chamada HTTP crua](#1-não-há-mágica-um-endpoint)**
   * Docs: [TypeSafe: System One](https://docs.typesafe.ai/concepts/system-one) | [Laya: HTTP API](https://nandhakishorm.github.io/laya/http-api/)
   * Exemplo: `01_http_direct.py` (`python 01_http_direct.py laya` para o Laya)
2. **[O SDK oficial e o Choice](#2-os-três-primitivos)**
   * Docs: [SDK Python](https://docs.typesafe.ai/sdk/python/) | [Choice](https://docs.typesafe.ai/primitives/choice)
   * Exemplo: `02_sdk_first_call.py`
3. **[A mesma pergunta num LLM](#3-a-mesma-decisão-num-llm)**
   * Docs: [LangChain: structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
   * Exemplo: `03_llm_same_question.py`
4. **[O Laya local](#4-laya-o-mesmo-código-na-sua-máquina)**
   * Docs: [Laya: Docker](https://nandhakishorm.github.io/laya/docker/) | [model card](https://huggingface.co/convaiinnovations/laya-multilingual)
   * Exemplo: `04_laya_local.py`
5. **[Exercício: a matriz de decisão](#5-código-decisão-llm-ou-classificador)**
   * Exemplo: `05_decision_matrix.py`

Rode da pasta `06-decision-models`. Em replay (padrão), nada vai para a rede.

---

## 1. Não há mágica: um endpoint

Um modelo de decisão é um `POST /v1/systemone` com duas coisas: um **estado** (texto, objeto JSON ou lista) e **perguntas tipadas**. A resposta é uma distribuição por pergunta. Não há texto a parsear, não há JSON quebrado, não há opção inventada: o modelo só consegue responder dentro das opções que você deu.

```json
{"state": {"ticket": "Fui cobrado duas vezes..."},
 "model": "jev-1.13.0",
 "questions": {"fila": {"type": "choice", "instructions": "Qual fila?", "criteria": {"financeiro": "...", "tecnico": "..."}}}}
```

## 2. Os três primitivos

| Primitivo | Pergunta | Resposta | Exemplo |
|---|---|---|---|
| **Choice** | qual destas opções? | opção, confiança, probabilidade de cada opção | fila do ticket |
| **Noul** | isto é verdade? | P(verdadeiro), de 0 a 1 | "o cliente ameaça cancelar?" |
| **Score** | em que degrau desta rubrica ordenada? | distribuição por nível e valor esperado | urgência 0, 1 ou 2 |

**Noul × Score** confunde muita gente. Noul é uma afirmação que é verdadeira ou falsa. Score é uma escada: o nível 2 é mais que o 1. "Pede reembolso?" é Noul. "Quão urgente?" é Score.

## 3. A mesma decisão num LLM

O `03` manda a **mesma** `DecisionSpec` para um LLM com `with_structured_output` e mede lado a lado: latência, tokens de entrada e saída, custo e se o JSON veio válido. A confiança do LLM é um número que ele escreveu. O módulo 05 mostra o que isso significa medindo calibração.

## 4. Laya: o mesmo código na sua máquina

```bash
docker compose --profile decision up laya   # da raiz; ou: uv run laya-serve
```

O `04` repete o `02` trocando só a `base_url`. Fatos do model card que o curso não esconde: o checkpoint multilíngue tem 322M de parâmetros (mmBERT-base), contexto padrão de 1.024 tokens por pergunta, sai **sem calibração** e é fraco zero-shot em decisões de domínio. A acurácia medida no nosso golden set está no módulo 02.

## 5. Código, decisão, LLM ou classificador?

| Use | Quando |
|---|---|
| **Código** | regra determinística resolve: parse, lookup, conta, limiar sobre probabilidades já calculadas |
| **Modelo de decisão** | pergunta fechada sobre texto livre, opções conhecidas, precisa de probabilidade |
| **LLM** | precisa **gerar** texto ou raciocinar em vários passos com ferramentas |
| **Classificador treinado** | pergunta fechada, volume enorme, rótulos estáveis e milhares de exemplos |

O exercício `05_decision_matrix.py` quebra o agente de e-mail do Bloco 3 em dez etapas. No gabarito, só uma precisa gerar texto.

### De onde vem

LM prevê o próximo token. LLM escala isso. RLHF e RLVR treinam o LLM a dar a resposta que agrada ou que passa num verificador. **RLCD** (Reinforcement Learning for Calibrated Decisions) treina um modelo a dar a **probabilidade honesta** de cada opção, com recompensa de regra de pontuação própria. É o treino do Jev e do Laya.

---

## ⏭️ Próximo Passo
Com os primitivos na mão, vamos trocar decisões de "qual" por um Choice: **[Módulo 2: Choice, roteamento e seleção](../02-choice-routing)**.

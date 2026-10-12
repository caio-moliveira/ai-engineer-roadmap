# 🔀 Módulo 2: Choice, Roteamento e Seleção

> **Objetivo:** substituir decisões de "qual" por um Choice.
> **Pergunta-chave:** quantas vezes o seu agente lê 10 descrições de tool só para escolher uma?

---

## 📚 Índice Prático e Documentação

1. **[Fila de tickets](#1-um-choice-medido)**
   * Docs: [Choice](https://docs.typesafe.ai/primitives/choice)
   * Exemplo: `01_classify_tickets.py`
2. **[Escolha de tool](#2-tool-selection-sem-function-calling)**
   * Docs: [LangChain: tool calling](https://docs.langchain.com/oss/python/langchain/tools)
   * Exemplo: `02_tool_selection.py`
3. **[Roteamento de modelo](#3-roteamento-barato-ou-caro)**
   * Exemplo: `03_model_routing.py`
4. **[TypeSafeClassifier e ModelRouterMiddleware](#4-pelo-langchain)**
   * Docs: [langchain-typesafe](https://docs.langchain.com/oss/python/integrations/providers/typesafe) | [LangSmith](https://docs.smith.langchain.com/)
   * Exemplo: `04_langchain_classifier.py`
5. **[Classificação hierárquica](#5-dois-níveis)**
   * Exemplo: `05_hierarchical.py`

---

## 1. Um Choice, medido

Quatro filas, 60 tickets rotulados (`data/golden_tickets.json`), a mesma spec para Jev, Laya e LLM (`common/specs.py: FILA`). O script imprime acurácia, F1 macro, Brier, ECE, latência p50/p95 e custo por mil decisões, e lista os erros. Repare que boa parte dos erros cai nos tickets marcados como `ambiguo`.

## 2. Tool selection sem function calling

O catálogo de tools do agente de vendas vira o `criteria` de um Choice. Comparamos com o caminho clássico: o LLM recebe as tools por `bind_tools` e escolhe qual chamar. São 80 perguntas do golden set do `workshop-jev`, com 20 adversariais.

> **Por que o agente de vendas e não o do Bloco 3?** O agente de vendas tem um catálogo de tools fechado e 80 perguntas rotuladas com a tool certa. Sem rótulo, não dá para medir. O exercício abaixo leva o padrão de volta para o agente do Bloco 3.

## 3. Roteamento barato ou caro

Um Choice decide qual modelo redige a resposta. O script mostra a conta de geração com e sem roteador. O custo de geração usa uma **premissa explícita** de tokens por resposta, declarada no topo do arquivo. Mostra também o número que importa: quantos casos difíceis foram parar no modelo barato.

## 4. Pelo LangChain

- **Parte A:** o `TypeSafeClassifier` é um `Runnable`. O `batch` paraleliza e, com `LANGSMITH_TRACING=true`, cada chamada vira um trace com tokens.
- **Parte B:** o `ModelRouterMiddleware` (experimental, extra `[experimental]`) faz o roteamento do item 3 dentro de um `create_agent`. A resposta completa, com probabilidades, fica em `state["model_route"]`.

Em replay, o classificador é o de verdade: só o transporte HTTP responde a partir das fixtures.

## 5. Dois níveis

Fila (4 opções), depois categoria dentro da fila (4 opções), contra um Choice plano de 16 opções. A hierarquia faz duas chamadas e o erro do primeiro nível se propaga. Quando o primeiro nível erra, a categoria certa nem está entre as opções.

---

## 🏋️ Exercício

Troque o tool-calling do agente do Bloco 3 (`03-ai-agents/03-langgraph-orchestration`) por um **node Choice** no LangGraph:

1. Escreva a `DecisionSpec` com as tools do agente como `criteria`.
2. Rotule 30 entradas reais com a tool certa (o formato está no módulo 05, script 01).
3. Registre acerto e latência antes e depois, com o harness do módulo 05.
4. Abaixo de qual confiança o node deve devolver a decisão ao LLM? Justifique com a curva do módulo 05.

## ⏭️ Próximo Passo
Choice escolhe entre opções exclusivas. Para afirmações independentes, use Nouls: **[Módulo 3: Noul, detecção e verificação](../03-noul-detection-verification)**.

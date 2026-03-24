# 🤖 Módulo 7: Trabalhando com Multi-Agentes

> **Goal:** Dividir para Conquistar.  
> **Status:** A Fronteira atual da IA Generativa (State of the Art).

Agentes individuais (single-agents) sofrem do problema do "Generalista": Se você fornecer a eles 30 ferramentas, 5 prompts gigantes e dezenas de restrições de formatação, a LLM colapsará, dividindo sua atenção ("Attention Mechanism") por todos esses tópicos, o que gera alucinações severas e quebra de regras.

Neste módulo prático, demonstramos as três melhores abordagens homologadas pela LangChain em `create_agent` para fragmentar cérebros gigantes em cérebros atômicos perfeitos.

---

## 📚 Índice de Scripts Práticos

Todos os códigos rodam nativamente (Console/Terminal). Para executá-los, acesse a pasta `python/` e garanta possuir o `.env` gerado nos módulos passados.

1. **[Mestre & Trabalhadores (Subagents pattern)](#1-mestre-e-trabalhadores-subagents-pattern)** -> `python/01_subagents.py`
2. **[Roteadores Inteligentes (Router pattern)](#3-roteadores-inteligentes-router-pattern)** -> `python/02_router.py`

---

## 1. Mestre e Trabalhadores (Subagents Pattern)

A arquitetura mais robusta e complexa no LangGraph. Ideal para tarefas multifacetadas (como um *Wedding Planner* que tem que cuidar de Voos, Buffet e Músicas).

- **Supervisor**: Um agente inteligente (GPT-4) que não faz o trabalho braçal. Ele delega.
- **Worker Agents**: Agentes menores (GPT-3.5/Mini) com "prompts de túnel" e focados 100% num assunto, empacotados pelo decorator `@tool` para serem invocados pelo Supervisor.

No script `01_subagents.py`, você verá o supervisor repassar a coleta de informações aos subordinados através da abstração do `ToolRuntime`, alterando silenciosamente a `AgentState` no final usando `Command(update={...})`.

---

## 2. Roteadores Inteligentes (Router Pattern)

Usar LLM como "Manager" (vide Subagents) pra decidir quem deve responder uma pergunta é custoso em tempo e dinheiro. Por que não ter uma função leve separando a demanda inicial?

No script `03_router.py`, demonstramos o uso dos novos tipos do LangGraph:
- **`Command(goto='agente')`**: O nó avalia a palavra chave (Ex: 'erro'/'tech') e finaliza sua execução jogando o controle de forma estática para o Agente Certo (não passa por invocação de `tools` do Supervisor).
- **`Send('node', args)`**: Para inputs multi-respostas. O router cria N eixos paralelos independentes (Ex: Mandando atuar o agente de Suporte de Carga e o de Restituição Financeira SIMULTANEAMENTE).

---

## 🧠 Mental Model Combinado

Hoje, a escalabilidade máxima dos Agentes pede:
1. **Router** frontal e enxuto na beira da sua API que tria o pedido.
2. Encaminhamento via `goto` para o grupo de **Subagents** certos (Squads).

## ⏭️ Parabéns! Fim desta Trilha Core.
Sua base como Engenheiro de Ferramentas / Agents orchestration em Langgraph está sólida de ponta a ponta.

# 🤖 Módulo 7: Trabalhando com Multi-Agentes

> **Goal:** Dividir para Conquistar.  
> **Status:** A Fronteira atual da IA Generativa (State of the Art).

Agentes individuais (single-agents) sofrem do problema do "Generalista": Se você fornecer a eles 30 ferramentas, 5 prompts gigantes e dezenas de restrições de formatação, a LLM colapsará, dividindo sua atenção ("Attention Mechanism") por todos esses tópicos, o que gera alucinações severas e quebra de regras.

Neste módulo prático, demonstramos as três melhores abordagens homologadas pela LangChain em `create_agent` para fragmentar cérebros gigantes em cérebros atômicos perfeitos.

---

## 📚 Índice de Scripts Práticos

Todos os códigos rodam nativamente (Console/Terminal). Certifique-se de possuir a API Key do Tavily (TAVILY_API_KEY) e da LLM configuradas no seu arquivo `.env` na raiz do projeto.

1. **[Mestre e Trabalhadores (Subagents Pattern)](#1-mestre-e-trabalhadores-subagents-pattern)** -> `01_subagents.py`
2. **[Roteadores Inteligentes (Router Pattern)](#2-roteadores-inteligentes-router-pattern)** -> `02_router.py`

---

## 1. Mestre e Trabalhadores (Subagents Pattern)

Padrão arquitetural consolidado na documentação do LangChain ("Multi-agent Network" e "Supervisor"). Ideal para tarefas multifacetadas (ex: um *Wedding Planner* que precisa cuidar de Voos, Locais e Músicas simultaneamente).

- **Supervisor**: Um agente orquestrador avançado (Ex: GPT-4o) que não executa o trabalho braçal, apenas planeja e delega responsabilidades. Em sua essência, funciona invocando subagentes como se fossem `tools` tradicionais, extraindo os parâmetros necessários do estado/conversa e repassando-os de forma pura.
- **Worker Agents / Subagents**: Agentes menores (Ex: GPT-4o-mini) com "prompts de túnel" focados 100% em uma única especialidade. Cada um possui ferramentas próprias para atuar, como pesquisa web real (via API do **Tavily Search**).

No script `01_subagents.py`, moldado às melhores práticas do LangGraph, removemos o acoplamento do `ToolRuntime`. Os **Worker Agents** (envolvidos pelo decorator `@tool`) recebem inputs primitivos como `origin` e `destination` puramente repassados pelo **Supervisor**, resultando em um design altamente interoperável e modular. O controle da memória e finalização segue com um update centralizado através do objeto `Command(update={...})` e resolvido via `InjectedToolCallId`.

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

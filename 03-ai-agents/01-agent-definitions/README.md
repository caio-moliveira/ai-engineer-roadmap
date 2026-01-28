# 🤖 Módulo 1: O que são Agentes de IA (Definição Real)

> **Goal:** Desmistificar o hype.  
> **Status:** Fundamental.

## 1. O que é um Agente?
Esqueça a ficção científica. Em Engenharia de Software, um Agente é:
**Um sistema que usa um LLM como motor de raciocínio para determinar o fluxo de controle da aplicação.**

### Agente vs. Workflow (RAG)
- **Workflow (RAG):** O caminho é **Hardcoded**.
  - `Input -> Retriever -> LLM -> Output`.
  - O desenvolvedor definiu os passos.
- **Agente:** O caminho é **Decidido pelo Modelo**.
  - `Input -> LLM Decide (Pesquisar? Responder? Pedir ajuda?) -> Tool -> LLM Decide...`
  - O sistema tem autonomia para escolher os passos.

## 2. O Spectrum de Autonomia
Nem tudo precisa ser autônomo.
1.  **Router:** Escolhe entre Caminho A ou B. (Baixo Risco).
2.  **State Machine (LangGraph):** Segue um grafo, mas decide loops. (Médio Risco).
3.  **Fully Autonomous:** Decide tudo. (Alto Risco, propenso a loops infinitos).

**Regra de Ouro:** Dê o **mínimo** de autonomia necessária para resolver o problema. Autonomia custa caro (tokens) e é imprevisível.

## 3. Por que Agentes falham?
A maioria das demos que você vê no Twitter falha em produção por 3 motivos:
1.  **Loops Infinitos:** O agente fica tentando a mesma ação errada para sempre.
2.  **Tools Ruins:** O agente tenta chamar uma API, mas a API retorna erro 500 ou formato errado.
3.  **Falta de Memória:** O agente esquece o que fez no passo anterior.

## 🧠 Mental Model: "O Estagiário Inteligente"
Trate seu Agente como um estagiário muito inteligente, mas sem experiência de vida.
- Se você disser "Resolva isso", ele vai fazer besteira.
- Se você der um Manual de Instruções (Prompt) e Ferramentas Claras (Tools), ele vai brilhar.

## ⏭️ Próximo Passo
Como desenhar esses estagiários?
Vá para **[Módulo 2: Arquiteturas de Agentes](../02-agent-architectures)**.

# 🛡️ Módulo 7: Deep Agents (Segurança e Guardrails)

> **Goal:** Evitar que o estagiário delete o banco de dados.  
> **Status:** Obrigatório em Produção.

## 1. Riscos de Agentes
Diferente de Chatbots (que só falam), Agentes **Agem**.
- **Loop Infinito:** Gastar $1000 em 1 hora tentando consertar um erro.
- **Tool Abuse:** Chamar `delete_user` com ID errado.
- **Data Leakage:** Enviar dados sensíveis para uma API externa.

## 2. Guardrails (NeMo / LlamaGuard)
São filtros que rodam *antes* e *depois* da chamada do LLM.
- **Input Rail:** "O usuário está tentando Injection?"
- **Output Rail:** "O agente está tentando vazar PII?"
- **Execution Rail:** "Essa tool pode ser chamada com esses argumentos?"

## 3. Timeouts e Limites
Nunca rode um `while` loop sem limite.
Todo grafo LangGraph deve ter `recursion_limit` (padrão 25).
Configure um orçamento máximo de tokens por execução.

## 4. Avaliação de Agentes
É mais difícil que avaliar RAG.
Você precisa avaliar a **Trajetória** (Trajectory).
- O agente escolheu as tools certas na ordem certa?
- Ele recuperou o erro ou desistiu?
- Use frameworks como **AgentBench**.

## 🧠 Mental Model: "A Cerca Elétrica"
O LLM é criativo e caótico. Os Guardrails são as paredes de concreto que definem onde ele pode brincar.
Se o agente tentar sair da cerca, o sistema corta a energia (interrompe a execução).

## ⏭️ Próximo Passo
E se precisarmos de um humano?
Vá para **[Módulo 8: Human-in-the-Loop](../08-human-in-the-loop)**.

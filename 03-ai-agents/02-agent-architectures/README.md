# 🏗️ Módulo 2: Arquiteturas de Agentes (2025+)

> **Goal:** Padrões de Design para Raciocínio.  
> **Status:** Não reinvente a roda.

## 1. ReAct (Reason + Act)
O padrão clássico (2023).
- **Loop:**
  1. **Thought:** "O usuário pediu o clima em SP."
  2. **Action:** `get_weather("Sao Paulo")`
  3. **Observation:** "25 graus, encoberto."
  4. **Thought:** "Tenho a resposta."
  5. **Answer:** "Está 25 graus."

- **Problema:** Simples demais. Se falhar, tendencia a alucinar.

## 2. Plan-and-Solve (Planner)
Para tarefas complexas ("Crie um app React").
- **Passo 1 (Planner):** O agente quebra o problema em steps.
  - 1. Criar arquivos.
  - 2. Instalar deps.
  - 3. Escrever código.
- **Passo 2 (Executor):** Outro agente executa cada passo da lista.
- **Vantagem:** Menos perda de contexto. Foco em uma tarefa por vez.

## 3. Reflection (Self-Correction)
O segredo da alta performance.
- O agente gera um output.
- O agente **Critica** o próprio output ("Isso está correto? Falta algo?").
- O agente **Refina** a resposta.

> **Dica de Produção:** Adicionar um passo de Reflexão melhora a precisão em ~30%, mas dobra o custo.

## 4. Tool-Augmented RAG
A arquitetura mais comum em empresas.
- O Agente tem acesso a uma Tool de `Retriever`.
- Ele decide *quando* pesquisar no Vector DB.
- Diferente do RAG tradicional, ele pode pesquisar múltiplas vezes ou refinar a busca.

## 🧠 Mental Model: "System 1 vs System 2"
- **LLM Padrão (Chat):** System 1 (Rápido, Intuitivo, Propenso a Erro).
- **Agente com Reflexão:** System 2 (Lento, Deliberativo, Preciso).

Use arquiteturas complexas apenas quando System 1 não for suficiente.

## ⏭️ Próximo Passo
Como codar isso?
Vá para **[Módulo 3: LangChain v1 para Agentes](../03-langchain-agents)**.

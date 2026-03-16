# 🧶 Módulo 3: LangGraph (O Coração da Orquestração)

> **Goal:** Controle total sobre o loop e construção de fluxos de agentes complexos.  
> **Status:** A ferramenta de orquestração de agentes mais importante e versátil de 2025.

O **LangGraph** organiza fluxos de trabalho de IA como **grafos** direcionados. Agentes vivem em loops, e enquanto *Chains* (Cadeias) tradicionais são lineares, o LangGraph permite criar arquiteturas cíclicas, com persistência de estado e rotas dinâmicas.

---

## 📚 Índice Prático e Documentação

Neste módulo, traduzimos a teoria para cenários do mundo real. Abaixo, você encontra os links para a documentação oficial do LangGraph e os scripts correspondentes:

1.  **[Nós e Estado (State)](#1-nós-nodes-e-estado-state)**
    *   Docs: [Conceptual Guide - Nodes](https://langchain-ai.github.io/langgraph/concepts/high_level/#nodes) | [How-to: State](https://langchain-ai.github.io/langgraph/how-tos/state-model/)
    *   Exemplo: `01_nodes_and_state.py` (Pipeline de Feedback de Cliente)
2.  **[Execução Paralela (Fan-out / Fan-in)](#2-execução-paralela-fan-out--fan-in)**
    *   Docs: [How-to: Parallel Execution](https://langchain-ai.github.io/langgraph/how-tos/map-reduce/)
    *   Exemplo: `02_parallel_execution.py` (Análise Multi-dimensional de Feedback)
3.  **[Arestas Condicionais (Conditional Edges)](#3-arestas-condicionais-conditional-edges)**
    *   Docs: [How-to: Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/conditional-edges/)
    *   Exemplo: `03_conditional_edges.py` (Roteamento para Especialistas)
4.  **[Memória e Persistência (Memory)](#4-memória-e-persistência-memory)**
    *   Docs: [Conceptual Guide - Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/) | [How-to: Persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
    *   Exemplo: `04_memory.py` (Chat Interativo com Histórico)
5.  **[Human-in-the-Loop (HITL)](#5-human-in-the-loop-hitl---o-fator-humano)**
    *   Docs: [Conceptual Guide - HITL](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/) | [How-to: HITL](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)
    *   Exemplo: `05_human_in_the_loop.py` (Aprovação de Transferência Bancária)

---

## 1. Nós (Nodes) e Estado (State)

O estado é o objeto que transita entre os nós. Em um cenário real, usamos `Annotated` com redutores para acumular logs e dados transformados.

**Cenário:** Pipeline que recebe feedback, limpa o texto e gera um relatório estruturado.

```python
# Exemplo Senior: Redutores e logs acumulados
class State(TypedDict):
    feedback_bruto: str
    feedback_limpo: str
    logs: Annotated[list[str], operator.add]
```

---

## 2. Execução Paralela (Fan-out / Fan-in)

Utilize paralelismo para tarefas que não dependem uma da outra, como analisar sentimento e categoria simultaneamente.

**Cenário:** Um único feedback é enviado para 3 LLMs diferentes em paralelo (Sentimento, Categoria e Urgência) e os resultados são consolidados em um nó agregador.

---

## 3. Arestas Condicionais (Conditional Edges)

Faça o grafo "decidir" o caminho. O uso moderno de `Command(goto="...")` dentro do nó é o padrão recomendado para fluxos dinâmicos.

**Cenário:** Se o feedback for um "Bug", o grafo roteia para o Especialista. Se for um "Elogio", vai para o Marketing.

---

## 4. Memória e Persistência (Memory)

O LangGraph mantém a consistência da conversa através de **Checkpointers**. O `thread_id` isola cada sessão, permitindo que o LLM lembre do contexto anterior.

**Feature Senior:** O redutor `add_messages` gerencia o histórico de chat automaticamente, fazendo o "append" inteligente de novas interações.

---

## 5. Human-in-the-Loop (HITL) - O Fator Humano

O método `interrupt()` pausa a execução térmica do grafo e aguarda uma intervenção manual. Essencial para processos críticos (Aprovação Financeira, Moderação de Conteúdo).

**Cenário:** Transferências bancárias > R$ 5.000 são pausadas para aprovação do gerente via terminal.

---

## 6. Capstone: Workflow do Agente de E-mail

Ao juntar tudo - execução paralela, persistência, roteamento condicional inteligente e moderação humana - chegamos ao estado da arte de agentes corporativos.

No nosso script `06_email_agent.py`, arquitetamos um fluxo complexo:
1. Receber Email (`read_email`).
2. Uma LLM avalia a Intenção via Strict JSON (`classify_intent`).
3. O fluxo faz **fan-out** executando RAG e Abertura de Tickets simultaneamente.
4. Ocorre um **fan-in** no nó redator.
5. **Roteamento Condicional**: Se for queixa crítica, vai para moderação humana via **HITL** (`interrupt`).

---

## ⏭️ Próximo Passo
O agente agora orquestra fluxos e lembra de coisas entre os ciclos. Mas o que acontece se o volume de memória explodir?
Vá para **[Módulo 5: Sistemas de Memória](../05-memory-systems)**.

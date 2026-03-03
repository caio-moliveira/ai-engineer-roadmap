# 🧶 Módulo 4: LangGraph (O Coração da Orquestração)

> **Goal:** Controle total sobre o loop e construção de fluxos de agentes complexos.  
> **Status:** A ferramenta de orquestração de agentes mais importante e versátil de 2025.

O **LangGraph** organiza fluxos de trabalho de IA como **grafos** direcionados. Agentes vivem em loops, e enquanto *Chains* (Cadeias) tradicionais são lineares, o LangGraph permite criar arquiteturas cíclicas, com persistência de estado e rotas dinâmicas.

Se você consegue desenhar o processo no papel como um fluxograma, você consegue codar no LangGraph.

---

## 📚 Índice prático do Módulo

Neste módulo, traduzimos a teoria para a prática usando scripts na pasta `/python`. Você pode executar cada um deles para ver o LangGraph em ação.

1. **[Nós e Estado (State)](#1-nós-nodes-e-estado-state)** -> `python/01_nodes_and_state.py`
2. **[Execução Paralela (Fan-out / Fan-in)](#2-execução-paralela-fan-out--fan-in)** -> `python/02_parallel_execution.py`
3. **[Arestas Condicionais (Conditional Edges)](#3-arestas-condicionais-conditional-edges)** -> `python/03_conditional_edges.py`
4. **[Memória e Persistência](#4-memória-e-persistência-memory)** -> `python/04_memory.py`
5. **[Human-in-the-Loop (HITL)](#5-human-in-the-loop-hitl---o-fator-humano)** -> `python/05_human_in_the_loop.py`
6. **[Capstone: Agente de E-mail](#6-capstone-workflow-do-agente-de-e-mail)** -> `python/06_email_agent.py`

---

## 1. Nós (Nodes) e Estado (State)

No centro do LangGraph, existem apenas três conceitos principais:
- **Estado (State):** A memória compartilhada de curto prazo do agente. Tudo que precisa persistir entre passos.
- **Nós (Nodes):** Funções Python puras que recebem o Estado, realizam trabalho e retornam atualizações para esse Estado.
- **Arestas (Edges):** Direcionamentos que definem qual nó executa em seguida.

### Definindo o Estado e Construindo Nós

O estado pode ser um `TypedDict`, `dataclass` ou modelo `Pydantic`.

```python
from typing import List, TypedDict
from langgraph.graph import END, START, StateGraph

# 1. Definimos o Schema do Estado
class State(TypedDict):
    nlist: List[str]

# 2. Criamos o Nó (Função Python)
def node_a(state: State) -> State:
    # Acessa o estado, processa algo e retorna ATUALIZAÇÕES
    return State(nlist=["Olá Mundo!"])

# 3. Construímos e Compilamos o Grafo
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_edge(START, "a") # Início do Grafo
builder.add_edge("a", END)   # Fim da Execução

graph = builder.compile()

# Executando
resultado = graph.invoke({"nlist": ["Início"]})
```

---

## 2. Execução Paralela (Fan-out / Fan-in)

O LangGraph permite execução paralela real. Quando um nó aponta para múltiplos nós, eles são executados simultaneamente (**Fan-out**). Para que as saídas desses nós não se sobresscrevam no Estado, usamos **Reducers**.

### O poder dos Reducers
Usamos `Annotated` do Python junto a uma função redutora (ex: `operator.add`). Em vez de sobrescrever a chave do estado, o LangGraph saberá que deve combinar/somar os resultados.

```python
import operator
from typing import Annotated

# Reducer garante que ramificações paralelas não apaguem dados umas das outras
class State(TypedDict):
    nlist: Annotated[list[str], operator.add]

# Configurando arestas paralelas no Builder
# FAN-OUT: O Node 'A' desenboca em 'B' e 'C' ao mesmo tempo
builder.add_edge("a", "b")
builder.add_edge("a", "c")

# FAN-IN: 'B' e 'C' se reencontram e aguardam em 'D'
builder.add_edge("b", "d")
builder.add_edge("c", "d")
```

---

## 3. Arestas Condicionais (Conditional Edges)

Para arquiteturas reais de agentes, o fluxo raramente é estático. Você precisará que o agente "decida" qual o próximo passo. Roteamento dinâmico no LangGraph é feito via `Command` ou via funções de aresta.

### Roteamento Seguro com `Command`
Nós de agentes modernos recomendam o uso do objeto `Command[Literal[...]]`. O próprio nó processa sua lógica e "comanda" o LangGraph para qual aresta pular usando `goto`.

```python
from langgraph.types import Command
from typing import Literal

def node_a(state: State) -> Command[Literal["b", "c", END]]:
    # Lógica de roteamento dinâmico baseada no estado
    if state["nlist"][-1] == "ir_para_b":
        proximo = "b"
    else:
        proximo = END

    # Retorna tanto a atualização do state quanto o destino
    return Command(
        update=State(nlist=["Atalho"]),
        goto=proximo
    )
```

---

## 4. Memória e Persistência (Memory)

Até o momento, cada chamada `.invoke()` recria o estado inteiro. Se quisermos criar agentes de chat ou fluxos assíncronos que retomam processos passados, adicionamos um **Checkpointer**.

Dessa forma, o estado inteiro do grafo é particionado e atrelado a um `thread_id`.

```python
from langgraph.checkpoint.memory import InMemorySaver

# 1. Alocamos a Memória
memory = InMemorySaver()

# 2. Compilamos passando o checkpointer
graph = builder.compile(checkpointer=memory)

# 3. Obrigatório: Invocamos passando um Config com o "Chat ID"
config = {"configurable": {"thread_id": "sessao-do-usuario-123"}}

result1 = graph.invoke({"nlist": ["a"]}, config)
result2 = graph.invoke({"nlist": ["b"]}, config)
# O result2 reterá ["a", "b"], mostrando que a memória foi acumulada!
```

---

## 5. Human-in-the-Loop (HITL) - O Fator Humano

O método `interrupt()` "congela" a execução térmica do grafo, salva o estado vigente no *checkpointer*, e encerra o processo até que você forneça um sinal manual. Vital para aprovação de transferências financeiras ou liberação de e-mails escritos por IAs.

*(Um `checkpointer` ativado é pré-requisito obrigatório).*

```python
from langgraph.types import interrupt

def node_critico(state: State) -> Command[...]:
    # O CÓDIGO DORME AQUI. O administrador receberá esse payload no frontend/terminal
    decisao_admin = interrupt({"pergunta": "O usuário enviou algo malicioso. Banir?"})
    
    # O código acordará apenas horas depois, direto nessa linha abaixo
    if decisao_admin == "sim":
       return Command(update={}, goto="ban_node")
```

### Como despertar/retomar um Grafo fora do código:
```python
# O invoke regular irá retornar um status de que foi interrompido...
result = graph.invoke(input, config)

if '__interrupt__' in result:
    # Retomamos despachando um Command(resume=)
    retomada = Command(resume="sim")
    graph.invoke(retomada, config)
```

---

## 6. Capstone: Workflow do Agente de E-mail

Ao juntar tudo - execução paralela, persistência, roteamento condicional inteligente e moderação humana - chegamos ao estado da arte de agentes corporativos.

No nosso script `06_email_agent.py`, arquitetamos um fluxo complexo:
1. Receber Email (`read_email`).
2. Uma LLM avalia a Intenção via Strict JSON (`classify_intent`).
3. O fluxo faz **fan-out** executando RAG (`search_documentation`) e Abertura de Tickets no Jira (`bug_tracking`) perfeitamente ao mesmo tempo.
4. Ocorre um **fan-in** no nó redator (`write_response`).
5. A LLM avalia: o e-mail aborda queixas críticas? Se sim, **Roteamento Condicional** pra moderação. Senão, vai direto.
6. O nó de moderação realiza o **HITL** (`interrupt`). O Humano revisa a minuta, aceita ou refaz.

> **Mental Model:** O LangGraph permite enjaular LLMs (imprevisíveis) dentro de funis puramente programáticos e confiáveis. Você só permite a LLM atuar ("chutar a bola") na etapa desenhada para ela atuar.

---

## ⏭️ Próximo Passo
O agente agora orquestra fluxos e lembra de coisas entre os ciclos. Mas o que acontece se o volume de memória explodir?
Vá para **[Módulo 5: Sistemas de Memória](../05-memory-systems)**.

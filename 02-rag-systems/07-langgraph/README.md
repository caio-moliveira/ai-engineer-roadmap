# 🧶 Módulo 7: LangGraph

> **Goal:** De Chains (DAGs) para Agentes (Loops).  
> **Status:** O futuro da orquestração RAG.

## 1. Por que LangGraph?
Pipelines LangChain são **Directed Acyclic Graphs (DAGs)**. Input -> Passo 1 -> Passo 2 -> Output.
A vida real é **Cíclica**.
- "Retrieval retornou 0 resultados. Tentar buscar sinônimos?" (Loop).
- "Resposta ambígua. Pedir clarificação ao usuário." (Loop).

LangGraph introduz **State Machines** (Máquinas de Estado) para IA.

## 2. Conceitos Core
- **State:** Um dicionário compartilhado (TypedDict) que persiste entre os passos.
- **Nodes:** Funções que modificam o estado.
- **Edges:** Lógica que decide para onde ir a seguir (Condicional).

## 3. A Arquitetura
```python
from langgraph.graph import StateGraph, END

# 1. Definir Estado
class AgentState(TypedDict):
    question: str
    documents: List[str]
    answer: str

# 2. Definir Nodes
def retrieve(state):
    docs = vector_db.search(state['question'])
    return {"documents": docs}

def generate(state):
    # Lógica para checar se docs são bons...
    return {"answer": llm.invoke(...)}

# 3. Construir Grafo
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()
```

## 4. Corrective RAG (CRAG)
Um dos melhores patterns para RAG lógico.
- **Node 1:** Retrieve.
- **Node 2:** Grade Documents (LLM checa se docs são relevantes).
- **Edge:**
    - Se Relevante -> Generate.
    - Se Irrelevante -> **Web Search** (Fallback).

## 🧠 Mental Model: "Máquina de Estados"
Não pense em "Chains". Pense em um Fluxograma.
- Início -> Busca -> Achamos?
    - Sim -> Resposta.
    - Não -> Re-frasear -> Buscar de novo.

## ⏭️ Próximo Passo
Existe alternativa ao LangChain?
Vá para **[Módulo 8: LlamaIndex](../08-llamaindex)**.

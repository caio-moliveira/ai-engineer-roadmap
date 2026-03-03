import operator
from typing import Annotated, List, TypedDict
from langgraph.graph import END, START, StateGraph

# 1. State modificado com Reducer (operator.add)
class State(TypedDict):
    nlist: Annotated[List[str], operator.add]

# 2. Definindo Múltiplos Nós (Nodes)
def node_a(state: State) -> State:
    print(f"Adicionando 'A' a {state['nlist']}")
    return State(nlist=["A"])

def node_b(state: State) -> State:
    print(f"Adicionando 'B' a {state['nlist']}")
    return State(nlist=["B"])

def node_c(state: State) -> State:
    print(f"Adicionando 'C' a {state['nlist']}")
    return State(nlist=["C"])

def node_bb(state: State) -> State:
    print(f"Adicionando 'BB' a {state['nlist']}")
    return State(nlist=["BB"])

def node_cc(state: State) -> State:
    print(f"Adicionando 'CC' a {state['nlist']}")
    return State(nlist=["CC"])

def node_d(state: State) -> State:
    print(f"Adicionando 'D' a {state['nlist']}")
    return State(nlist=["D"])

# 3. Construindo o Grafo (Graph)
builder = StateGraph(State)

builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_node("bb", node_bb)
builder.add_node("cc", node_cc)
builder.add_node("d", node_d)

builder.add_edge(START, "a")

# FAN-OUT: A vai para B e para C ao mesmo tempo!
builder.add_edge("a", "b")
builder.add_edge("a", "c")

# Cada branch prossegue isolada
builder.add_edge("b", "bb")
builder.add_edge("c", "cc")

# FAN-IN: Ambas branches se encontram e esperam-se no D
builder.add_edge("bb", "d")
builder.add_edge("cc", "d")

builder.add_edge("d", END)

graph = builder.compile()

# 4. Execução Paralela
if __name__ == "__main__":
    initial_state = State(
        nlist=["Valor Original Inicial:"]
    )
    
    print("--- Executando Grafo Paralelo ---")
    resultado = graph.invoke(initial_state)
    print("\n--- Resultado Final ---")
    print(resultado)

from typing import List, TypedDict
from langgraph.graph import END, START, StateGraph

# 1. Definindo o Estado (State)
class State(TypedDict):
    nlist: List[str]

# 2. Criando Nós (Nodes)
def node_a(state: State) -> State:
    print(f"O nó A está recebendo: {state['nlist']}")
    
    note = "Olá Mundo vindo do Nó A!"
    
    return State(nlist=[note])

# 3. Construindo o Grafo (Graph)
builder = StateGraph(State)

builder.add_node("a", node_a)
builder.add_edge(START, "a")
builder.add_edge("a", END)

graph = builder.compile()

# 4. Executando (Invoke)
if __name__ == "__main__":
    initial_state = State(
        nlist=["Olá Nó A, como vai você?"]
    )
    
    print("--- Iniciando o Grafo ---")
    resultado = graph.invoke(initial_state)
    print("\n--- Resultado Final ---")
    print(resultado)

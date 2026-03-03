import operator
from typing import Annotated, List, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

class State(TypedDict):
    nlist: Annotated[List[str], operator.add]

# Abordagem 1: Nodes guiando a Rota (Command)
def node_a(state: State) -> Command[Literal["b", "c", END]]:
    select = state["nlist"][-1]
    
    if select == "b":
        next_node = "b"
    elif select == "c":
        next_node = "c"
    elif select == "q":
        next_node = END
    else:
        next_node = END

    return Command(
        update=State(nlist=[select]),
        goto=next_node
    )

def node_b(state: State) -> State:
    return State(nlist=["B"])

def node_c(state: State) -> State:
    return State(nlist=["C"])

# Abordagem 2: Função Condicional (Comentada no flow, mas disponível)
def cond_edge(state: State) -> Literal["b", "c", END]:
    select = state["nlist"][-1]
    if select == "b":
        return "b"
    elif select == "c":
        return "c"
    else:
        return END

# Construindo o Grafo
builder = StateGraph(State)

builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

builder.add_edge(START, "a")
# Na abordagem Command, nenhuma aresta extra partindo de `a` precisa ser definida.
# Se fossemos usar add_conditional_edges, seria assim:
# builder.add_conditional_edges("a", cond_edge)

builder.add_edge("b", END)
builder.add_edge("c", END)

graph = builder.compile()

# Loop Interativo
if __name__ == "__main__":
    print("--- Arestas Condicionais ---")
    print("O nó 'a' vai decidir pra onde rotear com base no seu input!")
    
    while True:
        user = input('\nDigite "b", "c", ou "q" para sair: ')
        
        input_state = State(nlist=[user])
        result = graph.invoke(input_state)
        
        print(f"Estado final: {result}")
        
        if result['nlist'][-1] == "q" or user.lower() == "q":
            print("Encerrando!")
            break

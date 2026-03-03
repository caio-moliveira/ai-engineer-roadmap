import operator
from typing import Annotated, List, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
# 1. Puxando e inicializando a Memoria Simples
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    nlist: Annotated[List[str], operator.add]

def node_a(state: State) -> Command[Literal["b", "c", END]]:
    select = state["nlist"][-1]
    if select == "b": next_node = "b"
    elif select == "c": next_node = "c"
    else: next_node = END

    return Command(
        update=State(nlist=[select]),
        goto=next_node
    )

def node_b(state: State) -> State: return State(nlist=["B"])
def node_c(state: State) -> State: return State(nlist=["C"])

# Builder normal
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)

# 2. Compilando com checkpointer para Memória
memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)

# 3. Loop com config (Injetando thread_id)
if __name__ == "__main__":
    # Configuração que atrela os históricos a um ID exclusivo
    config = {"configurable": {"thread_id": "thread-1"}}
    
    print("--- Memória Ativa ---")
    print("Sempre que você rodar esse loop, ele lembrará das iterações passadas.\n")
    
    while True:
        user = input('\nDigite "b", "c", ou "q" para sair: ')
        input_state = State(nlist=[user])
        
        # Obrigatório passar `config` quando o checkpointer está instanciado no `compile()`
        result = graph.invoke(input_state, config)
        
        print(f"Estado final ACUMULADO:\n{result['nlist']}")
        
        if result['nlist'][-1] == "q" or user.lower() == "q":
            print("Encerrando!")
            break

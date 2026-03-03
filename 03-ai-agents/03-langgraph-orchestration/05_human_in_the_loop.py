import operator
from typing import Annotated, List, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    nlist: Annotated[List[str], operator.add]

def node_a(state: State) -> Command[Literal["b", "c", END]]:
    print("-> Entrando no nó 'a'")
    select = state["nlist"][-1]
    
    # Condições Seguras
    if select == "b": next_node = "b"
    elif select == "c": next_node = "c"
    elif select == "q": next_node = END
    
    # Sinal de Alerta! HITL Necessário
    else:
        # AQUI O GRAFO PAUSA!
        admin_response = interrupt(f"Input Inesperado! Recebi a letra: '{select}'. Como prosseguir?")
        
        print(f"-> [O admin respondeu com a ordem: {admin_response} ]")
        
        if admin_response == "continue":
            next_node = "b"
        else:
            next_node = END
            select = "q"
            
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

# Checkpoint OBRIGATÓRIO p/ a pausa!
memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread-2"}}
    print("--- Human in the Loop ---")
    print("Trilhas Seguras: 'b', 'c', e 'q'")
    print("Qualquer outra letra chamará a MODERAÇÃO!")
    
    while True:
        user = input('\nDigite uma letra: ')
        input_state = State(nlist=[user])
        
        # 1. Primeira Execução do Input
        result = graph.invoke(input_state, config)
        
        # 2. Descobrindo Se Pausou via Interrupt (A Letra Misteriosa Ativou a flag)
        if '__interrupt__' in result:
            print(f"\n[!] SISTEMA INTERROMPIDO [!]")
            msg_da_funcao = result['__interrupt__'][-1].value
            print(f"Motivo: {msg_da_funcao}")
            
            # 3. Interação do Admin Visual!
            decisao_humana = input(f"\nAtenção Admin => Digite 'continue' ou 'rejeitar': ")

            # 4. Desbloqueando a função "node_a"
            human_response = Command(resume=decisao_humana)
            result = graph.invoke(human_response, config) # Invocando Pela Segunda Vez
            
        print(f"Estado Final Atualizado: {result['nlist']}")
        
        if result['nlist'][-1] == "q":
            print("-> Encerrando!")
            break

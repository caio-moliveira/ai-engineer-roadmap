import operator
from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

# 1. Configuração Inicial
load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Definindo o Estado (Somente Mensagens)
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# 3. Criando o Nó do Agente
def chatbot(state: State) -> dict:
    """Nó simples que envia o histórico completo para o LLM."""

    resposta = llm.invoke(state["messages"])
    return {"messages": [resposta]}

# 4. Construindo o Grafo com Persistência
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# O MemorySaver() é o checkpointer em memória
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# 5. Loop de Conversa Interativa no Terminal
if __name__ == "__main__":
    print("="*60)
    print("        CHAT SIMPLES COM MEMÓRIA (LANGGRAPH)")
    print("="*60)
    print("O histórico será salvo automaticamente entre as perguntas.")
    print("Digite 'sair' para encerrar.\n")

    # O thread_id identifica unicamente esta conversa no banco de memória
    config = {"configurable": {"thread_id": "conversa-1"}}

    while True:
        user_input = input("Você: ")
        
        if user_input.lower() in ["sair", "exit", "quit"]:
            # Antes de sair, buscamos o estado final para imprimir o histórico
            estado_atual = graph.get_state(config)
            historico = estado_atual.values.get("messages", [])
            
            print("\n" + "="*60)
            print("        HISTÓRICO COMPLETO DA CONVERSA (ESTRUTURADO)")
            print("="*60)
            for msg in historico:
                classe_nome = msg.__class__.__name__
                print(f"[{classe_nome}]: {msg.content}")
            
            print("\n" + "="*60)
            print("        HISTÓRICO BRUTO (OBJETOS REAIS)")
            print("="*60)
            for msg in historico:
                print(msg)
            
            print("="*60)
            print("Até logo!")
            break

        # Ao invocar, o LangGraph busca as mensagens anteriores do 'conversa-1'
        # e as concatena com a nova HumanMessage.
        resultado = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]}, 
            config
        )
        
        # A resposta final será a última mensagem do histórico atualizado
        print(f"Assistente: {resultado['messages'][-1].content}\n")

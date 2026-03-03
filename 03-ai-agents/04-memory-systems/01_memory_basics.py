import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

# Carrega variáveis de ambiente (ex: OPENAI_API_KEY)
load_dotenv()

    # Criando um agente sem ferramentas e sem memória
    agent = create_agent(model="gpt-4o-mini", tools=[])
    
    # 1. Primeira Interação
    question1 = HumanMessage(content="Hello my name is Seán and my favourite colour is green")
    print(f"\n[Usuário]: {question1.content}")
    
    response1 = agent.invoke({"messages": [question1]})
    print(f"[Agente]: {response1['messages'][-1].content}")
    
    # 2. Segunda Interação (O agente não vai lembrar)
    question2 = HumanMessage(content="What's my favourite colour?")
    print(f"\n[Usuário]: {question2.content}")
    
    response2 = agent.invoke({"messages": [question2]})
    print(f"[Agente]: {response2['messages'][-1].content}")
    print("\n-> Ccomo você pode ver, o agente SEM memória não lembra da interação anterior.")


def test_with_memory():
    print("\n\n" + "="*50)
    print(" PARTE 2: AGENTE COM MEMÓRIA (InMemorySaver)")
    print("="*50)
    
    # Adicionando o checkpointer via InMemorySaver
    memory = InMemorySaver()
    agent = create_agent(
        model="gpt-4o-mini",
        tools=[],
        checkpointer=memory,
    )
    
    # Precisamos de uma configuração atrelando as mensagens a uma Thread (Sessão)
    config = {"configurable": {"thread_id": "thread_sean_01"}}
    
    # 1. Primeira Interação
    question1 = HumanMessage(content="Hello my name is Seán and my favourite colour is green")
    print(f"\n[Usuário]: {question1.content}")
    
    response1 = agent.invoke(
        {"messages": [question1]},
        config
    )
    print(f"[Agente]: {response1['messages'][-1].content}")
    
    # 2. Segunda Interação (O agente VAI lembrar porque estamos passando o mesmo `config`)
    question2 = HumanMessage(content="What's my favourite colour?")
    print(f"\n[Usuário]: {question2.content}")
    
    response2 = agent.invoke(
        {"messages": [question2]},
        config
    )
    print(f"[Agente]: {response2['messages'][-1].content}")
    print("\n-> Usando o `checkpointer` com um `thread_id`, o agente manteve o contexto da conversa!")

if __name__ == "__main__":
    print("Iniciando demonstração de Sistemas de Memória...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada. O script pode falhar.")
        
    test_no_memory()
    test_with_memory()

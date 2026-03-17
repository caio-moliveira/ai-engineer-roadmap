import os
import asyncio
import operator
from typing import Annotated, List, TypedDict

from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# 1. Definição do Estado
class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# 2. Nó do Chatbot
async def chatbot_node(state: State):
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

async def main():
    print("--- 🚀 Chat Interativo com Memória Redis ---")
    
    # Configuração da conexão Redis
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # 3. Montagem do Grafo
    workflow = StateGraph(State)
    workflow.add_node("agent", chatbot_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)

    try:
        # Conforme a documentação oficial, usamos AsyncRedisSaver dentro de um context manager assíncrono
        async with AsyncRedisSaver.from_conn_string(url) as saver:
            # Opcional: await saver.asetup() se necessário para inicializar o DB
            
            graph = workflow.compile(checkpointer=saver)
            
            # 4. Identificação do Usuário
            user_id = input("\n👤 Digite seu User ID (ex: caio): ").strip() or "default_user"
            config = {"configurable": {"thread_id": user_id}}
            
            # 5. Recuperação de Histórico Prévio
            state = await graph.aget_state(config)
            history = state.values.get("messages", [])
            
            if history:
                print(f"\n📜 Histórico recuperado de Redis ({len(history)} mensagens):")
                for msg in history:
                    pfx = "Usuário" if isinstance(msg, HumanMessage) else "Bot"
                    name = "Eu" if isinstance(msg, HumanMessage) else "Bot"
                    print(f"  {name}: {msg.content}")
            else:
                print("\n✨ Nenhuma conversa anterior encontrada para este ID.")

            # 6. Loop de Conversa
            print(f"\n💬 Chat Iniciado! Digite 'sair' para encerrar.")
            while True:
                user_input = input("\nVocê: ").strip()
                if user_input.lower() in ["sair", "exit", "quit"]:
                    print(f"👋 Até logo, {user_id}!")
                    break
                
                if not user_input:
                    continue

                input_data = {"messages": [HumanMessage(content=user_input)]}
                
                # Execução com persistência automática no Redis via thread_id
                async for event in graph.astream(input_data, config, stream_mode="values"):
                    # No modo "values", pegamos a última mensagem do estado atualizado
                    if "messages" in event:
                        last_msg = event["messages"][-1]
                        if isinstance(last_msg, AIMessage):
                            print(f"Bot: {last_msg.content}")

    except Exception as e:
        import traceback
        print(f"\n❌ Erro na conexão: {e}")
        traceback.print_exc()
        print("\nDica: Certifique-se de que o Redis está rodando: docker run -p 6379:6379 -d redis")

if __name__ == "__main__":
    asyncio.run(main())

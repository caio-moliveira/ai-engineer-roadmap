import asyncio
import os
from typing import Any, Dict, List, Annotated
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

# 1. Definição do Estado do Agente
class State(Dict):
    # O Annotated com operator.add faz com que novas mensagens sejam anexadas ao histórico existente
    messages: Annotated[List[BaseMessage], operator.add]

# 2. Definição do Nó do Chatbot
async def chatbot_node(state: State):
    """Nó que interage com o LLM usando o histórico de mensagens."""
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

class ShortTermMemoryManager:
    """
    Utilitários para gerenciar memória de curto prazo (short-term) no LangGraph.
    Focado em persistência por thread.
    """

    def __init__(self, checkpointer: BaseCheckpointSaver):
        self.checkpointer = checkpointer

    def get_config(self, thread_id: str) -> Dict[str, Any]:
        return {"configurable": {"thread_id": thread_id}}

    async def get_history(self, thread_id: str, graph: Any) -> List[BaseMessage]:
        config = self.get_config(thread_id)
        state = await graph.aget_state(config)
        return state.values.get("messages", [])

async def main():
    """
    Exemplo prático de execução individual com memória em chat.
    """
    print("--- Demo: Memória de Curto Prazo (Short-Term) ---")
    
    # Configuração do Grafo
    workflow = StateGraph(State)
    workflow.add_node("agent", chatbot_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    
    # Uso de MemorySaver para persistência local (em memória)
    # Para Postgres, trocaria por PostgresSaver
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    # Identificador do usuário para a thread
    thread_id = input("\n👤 Digite seu Thread ID (ex: caio): ").strip() or "default_user"
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n💬 Chat Iniciado (Thread: {thread_id})! Digite 'sair' para encerrar.")
    
    while True:
        user_input = input("\nVocê: ").strip()
        if user_input.lower() in ["sair", "exit", "quit"]:
            print(f"👋 Até logo!")
            break
        
        if not user_input:
            continue

        input_data = {"messages": [HumanMessage(content=user_input)]}
        
        async for event in graph.astream(input_data, config):
            for node, values in event.items():
                if "messages" in values:
                    # Pegamos a última mensagem (que deve ser do AI)
                    last_msg = values["messages"][-1]
                    if isinstance(last_msg, AIMessage):
                        print(f"Bot: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(main())

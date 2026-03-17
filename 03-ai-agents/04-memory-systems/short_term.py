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
    
    # Identificador único da conversa
    thread_id = "usuario_exemplo_1"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Primeira interação
    print(f"\n[Thread: {thread_id}] Usuário: Oi, meu nome é Caio.")
    input1 = {"messages": [HumanMessage(content="Oi, meu nome é Caio.")]}
    async for event in graph.astream(input1, config):
        for node, values in event.items():
            if "messages" in values:
                print(f"Bot: {values['messages'][-1].content}")

    # Segunda interação (O bot deve lembrar o nome devido à memória de thread)
    print(f"\n[Thread: {thread_id}] Usuário: Qual é o meu nome?")
    input2 = {"messages": [HumanMessage(content="Qual é o meu nome?")]}
    async for event in graph.astream(input2, config):
        for node, values in event.items():
            if "messages" in values:
                print(f"Bot: {values['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())

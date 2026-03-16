from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph

# O Short-Term Memory no LangGraph é baseado em Threads.
# Cada thread_id representa uma "conversa" ou sessão de curto prazo única.

class ShortTermMemoryManager:
    """
    Utilitários para gerenciar memória de curto prazo (short-term) no LangGraph.
    """

    def __init__(self, checkpointer: BaseCheckpointSaver):
        """
        Inicializa com um checkpointer (ex: PostgresSaver ou MemorySaver).
        """
        self.checkpointer = checkpointer

    def get_config(self, thread_id: str) -> Dict[str, Any]:
        """
        Retorna a configuração de execução necessária para o checkpoint.
        """
        return {"configurable": {"thread_id": thread_id}}

    async def get_current_state(self, thread_id: str, graph: StateGraph) -> Dict[str, Any]:
        """
        Recupera o estado atual de uma thread específica.
        """
        config = self.get_config(thread_id)
        return await graph.aget_state(config)

    async def get_history(self, thread_id: str, graph: StateGraph) -> List[BaseMessage]:
        """
        Extrai o histórico de mensagens do estado atual de uma thread.
        """
        state = await self.get_current_state(thread_id, graph)
        # Assume que o estado do grafo tem uma chave 'messages'
        return state.values.get("messages", [])

def explain_short_term():
    """
    Explicação didática sobre Short-Term Memory.
    """
    return (
        "Short-term memory no LangGraph é 'Thread-bound'.\n"
        "1. Ela persiste o estado completo do grafo (mensagens, variáveis, etc.).\n"
        "2. É acessada via `thread_id`.\n"
        "3. Permite 'Time Travel' (voltar a estados anteriores).\n"
        "4. É automática quando um checkpointer está configurado no compile()."
    )

# Exemplo de uso conceitual:
# graph = workflow.compile(checkpointer=postgres_saver)
# await graph.ainvoke(input_data, config={"configurable": {"thread_id": "user_123"}})

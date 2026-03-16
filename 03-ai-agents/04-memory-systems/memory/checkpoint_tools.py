from typing import Any, Dict, List, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph

# Checkpoints são o "coração" da persistência no LangGraph.
# Eles salvam o snapshot do estado do grafo em cada passo.
# Útil para: Debugging, Human-in-the-loop e Time Travel.

class CheckpointInspector:
    """
    Ferramentas para inspecionar e gerenciar checkpoints de threads.
    """

    def __init__(self, checkpointer: BaseCheckpointSaver):
        self.checkpointer = checkpointer

    async def list_thread_history(
        self, 
        thread_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Lista o histórico de checkpoints (versões) de uma thread.
        Permite ver como o estado evoluiu.
        """
        config = {"configurable": {"thread_id": thread_id}}
        history = []
        async for state in self.checkpointer.alist(config, limit=limit):
            history.append({
                "checkpoint_id": state.config["configurable"].get("checkpoint_id"),
                "ts": state.metadata.get("ts") if state.metadata else None,
                "values": state.values
            })
        return history

    async def get_latest_checkpoint(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera o estado mais recente de uma thread.
        """
        config = {"configurable": {"thread_id": thread_id}}
        state = await self.checkpointer.aget(config)
        return state.values if state else None

    async def reset_thread(self, thread_id: str):
        """
        Explicação sobre 'Reset':
        No LangGraph, checkpoints são imutáveis por padrão. 
        Para 'resetar', costuma-se criar uma nova thread_id ou 
        injetar um estado vazio na thread atual via `update_state`.
        """
        print(f"Dica: Para resetar a thread {thread_id}, envie um estado vazio ou novo via update_state.")

def checkpoint_vs_store():
    """
    Diferenciação clara para o desenvolvedor.
    """
    return {
        "Checkpoint": "CURTO PRAZO. Específico da thread. Snapshot automático. Permite retroceder.",
        "Store": "LONGO PRAZO. Global/Por usuário. Persiste entre threads. Busca semântica."
    }

# Exemplo de Observabilidade:
# inspector = CheckpointInspector(postgres_saver)
# history = await inspector.list_thread_history("session_456")
# print(f"A thread possui {len(history)} versões de estado.")

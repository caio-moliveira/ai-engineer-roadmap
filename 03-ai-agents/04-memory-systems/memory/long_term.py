from typing import Any, Dict, List, Optional, Tuple

from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig

# Long-Term Memory (LTM) no LangGraph utiliza o conceito de 'Store'.
# Ao contrário do checkpoint, o Store é compartilhado entre threads.
# Geralmente organizado por namespaces, ex: ("memories", user_id).

class LongTermMemoryManager:
    """
    Gerenciador de Memória de Longo Prazo (LTM) usando o Store do LangGraph.
    """

    def __init__(self, store: BaseStore):
        self.store = store

    def get_user_namespace(self, user_id: str) -> Tuple[str, ...]:
        """
        Cria um namespace padrão para o usuário.
        """
        return ("memories", user_id)

    async def save_memory(self, user_id: str, key: str, value: Dict[str, Any]):
        """
        Salva uma informação persistente para o usuário (ex: preferências, fatos).
        """
        namespace = self.get_user_namespace(user_id)
        await self.store.aput(namespace, key, value)

    async def get_memory(self, user_id: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera uma memória específica pelo namespace e chave.
        """
        namespace = self.get_user_namespace(user_id)
        item = await self.store.aget(namespace, key)
        return item.value if item else None

    async def search_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Busca memórias no namespace do usuário.
        Nota: Se o store suportar busca semântica, ele usará a query para tal.
        """
        namespace = self.get_user_namespace(user_id)
        items = await self.store.asearch(namespace, query=query)
        return [item.value for item in items]

def get_ltm_from_node(config: RunnableConfig) -> BaseStore:
    """
    Demonstra como acessar o Store de dentro de um Node do LangGraph.
    
    O Store é injetado no 'config' durante a execução se estiver configurado.
    """
    store = config.get("store")
    if not store:
        raise ValueError("Store não configurado no Grafo.")
    return store

# Dica didática:
# Use Short-Term (Checkpoint) para o 'fluxo atual' da conversa.
# Use Long-Term (Store) para 'fatos que o bot deve lembrar para sempre' sobre o usuário.

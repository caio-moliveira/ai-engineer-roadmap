import asyncio
from typing import Any, Dict, List, Optional, Tuple

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Long-Term Memory (LTM) no LangGraph utiliza o conceito de 'Store'.
# Ao contrário do checkpoint, o Store é compartilhado entre threads.

class LongTermMemoryManager:
    """
    Gerenciador de Memória de Longo Prazo (LTM) usando o Store do LangGraph.
    """

    def __init__(self, store: BaseStore):
        self.store = store

    def get_user_namespace(self, user_id: str) -> Tuple[str, ...]:
        return ("memories", user_id)

    async def save_memory(self, user_id: str, key: str, value: Dict[str, Any]):
        namespace = self.get_user_namespace(user_id)
        await self.store.aput(namespace, key, value)

    async def get_memories_as_string(self, user_id: str) -> str:
        """Busca todas as memórias do usuário e retorna uma string formatada."""
        namespace = self.get_user_namespace(user_id)
        items = await self.store.asearch(namespace)
        if not items:
            return "Sem memórias prévias."
        return "\n".join([f"- {item.key}: {item.value['content']}" for item in items])

async def main():
    print("--- Demo: Memória de Longo Prazo (Long-Term Store) ---")
    
    # 1. Setup do Store
    store = InMemoryStore()
    manager = LongTermMemoryManager(store)
    user_id = "caio_123"
    
    # 2. Salvando uma preferência de longo prazo
    print(f"\n[Sistema] Salvando preferência para o usuário {user_id}...")
    await manager.save_memory(user_id, "preferencia_cafe", {"content": "Gosto de café sem açúcar e muito forte."})
    
    # 3. Recuperando memórias para injetar no Contexto
    memorias = await manager.get_memories_as_string(user_id)
    print(f"\n[Store] Memórias encontradas:\n{memorias}")
    
    # 4. Uso com LLM
    llm = ChatOpenAI(model="gpt-4o-mini")
    pergunta = "Com base no que você sabe sobre minhas preferências, como devo preparar meu café?"
    
    print(f"\nUsuário: {pergunta}")
    
    prompt = f"Você é um assistente pessoal. Aqui estão fatos que você sabe sobre o usuário:\n{memorias}\n\nUsuário pergunta: {pergunta}"
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    print(f"Bot: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())

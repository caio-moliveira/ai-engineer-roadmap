import asyncio
from typing import List, Optional

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class SemanticMemoryManager:
    """
    Gerenciador para busca semântica em memórias persistentes.
    """

    def __init__(self, store: BaseStore):
        self.store = store

    async def search_relevant_context(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5
    ) -> str:
        namespace = ("memories", user_id)
        
        # Busca semântica (asearch)
        results = await self.store.asearch(
            namespace,
            query=query,
            limit=limit
        )
        
        if not results:
            return "Nenhuma memória relevante encontrada."
            
        context_parts = [f"- {item.key}: {item.value['content']}" for item in results]
        return "\n".join(context_parts)

async def main():
    print("--- Demo: Memória Semântica (Semantic Search) ---")
    
    # 1. Setup (Para o InMemoryStore, a 'busca semântica' do LangGraph 
    # simula relevância ou usa busca por regex/prefixo se não houver indexador vetorial real.
    # Em produção, usaria-se PostgresStore ou similar com search habilitado.)
    store = InMemoryStore()
    manager = SemanticMemoryManager(store)
    user_id = "pedro_dev"
    
    # 2. Populando o store com fatos variados
    print(f"\n[Sistema] Guardando conhecimentos sobre {user_id}...")
    await store.aput(("memories", user_id), "ia", {"content": "Pedro trabalha com Deep Learning e PyTorch."})
    await store.aput(("memories", user_id), "hobby", {"content": "Pedro gosta de surfar nos fins de semana."})
    await store.aput(("memories", user_id), "clima", {"content": "Pedro prefere o frio ao calor."})
    
    # 3. Realizando busca semântica
    # A query 'tecnologia' deve trazer o item sobre 'Deep Learning'
    query = "Com o que o Pedro trabalha?"
    print(f"\n[Busca] Procurando por: '{query}'")
    contexto = await manager.search_relevant_context(user_id, query)
    print(f"Resultado:\n{contexto}")
    
    # 4. LLM integrando o conhecimento
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = f"Aqui está o que sabemos: {contexto}\n\nPergunta: {query}"
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    print(f"\nBot: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())

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
    print("--- 🧠 Demo: Memória de Longo Prazo Interativa (LTM) ---")
    
    # 1. Setup do Store (Em memória para o demo)
    store = InMemoryStore()
    manager = LongTermMemoryManager(store)
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    # Identificação do Usuário
    user_id = input("\n👤 Digite seu User ID (ex: caio): ").strip() or "caio_default"
    
    # 2. Pré-seed: Simulando informações que o bot já "conhece"
    print(f"\n[Sistema] Carregando conhecimentos prévios sobre {user_id}...")
    await manager.save_memory(user_id, "perfil_base", {
        "content": "Caio é Engenheiro de IA, tem 23 anos e adora café forte sem açúcar."
    })
    await manager.save_memory(user_id, "localizacao", {
        "content": "Mora em Montes Claros, Minas Gerais, Brasil."
    })
    
    print(f"✅ Memória de longo prazo inicializada!")
    print(f"💬 Chat Iniciado! Digite 'sair' para encerrar ou 'memoria' para ver o que eu sei.")

    # 3. Loop de Conversa Interativa
    while True:
        user_input = input("\nVocê: ").strip()
        
        if user_input.lower() in ["sair", "exit", "quit"]:
            print(f"👋 Até logo, {user_id}!")
            break
            
        if user_input.lower() == "memoria":
            memorias = await manager.get_memories_as_string(user_id)
            print(f"\n[Store] O que eu sei sobre você:\n{memorias}")
            continue

        if not user_input:
            continue

        # Recuperar memórias atuais para dar contexto ao LLM
        contexto_memorias = await manager.get_memories_as_string(user_id)
        
        # O prompt instrui o LLM a responder E identificar se há novos fatos para salvar
        prompt_template = f"""
        Você é um assistente pessoal inteligente com memória de longo prazo.
        
        CONTEXTO ATUAL (O que você já sabe sobre o usuário):
        {contexto_memorias}
        
        INSTRUÇÕES:
        1. Responda à pergunta do usuário de forma natural.
        2. Se o usuário mencionar um NOVO fato importante sobre ele (ex: hobbies, preferências, trabalho, família), 
           termine sua resposta com uma linha especial: "NOVO_FATO: [descrição curta do fato]".
        
        PERGUNTA DO USUÁRIO: {user_input}
        """
        
        response = await llm.ainvoke([HumanMessage(content=prompt_template)])
        content = response.content

        # Processar a resposta e extrair novos fatos, se existirem
        if "NOVO_FATO:" in content:
            partes = content.split("NOVO_FATO:")
            resposta_limpa = partes[0].strip()
            novo_fato = partes[1].strip()
            
            # Gerar uma chave simples baseada no conteúdo (simplificado para o demo)
            key = f"fato_{asyncio.get_event_loop().time()}"
            await manager.save_memory(user_id, key, {"content": novo_fato})
            
            print(f"Bot: {resposta_limpa}")
            print(f"✨ [Memória Atualizada]: {novo_fato}")
        else:
            print(f"Bot: {content}")

if __name__ == "__main__":
    asyncio.run(main())

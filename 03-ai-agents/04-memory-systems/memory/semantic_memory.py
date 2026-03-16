from typing import List, Optional

from langchain_core.embeddings import Embeddings
from langgraph.store.base import BaseStore

# A memória semântica permite recuperar informações por relevância de significado,
# não apenas por palavras-chave exatas. No LangGraph Store, isso é feito
# via a função `search` se o Store estiver configurado com um motor de busca vetorial.

class SemanticMemoryManager:
    """
    Gerenciador para busca semântica em memórias persistentes.
    """

    def __init__(self, store: BaseStore, embeddings: Optional[Embeddings] = None):
        """
        Inicializa com o Store e opcionalmente um modelo de Embeddings.
        
        Nota: Muitos Stores modernos gerenciam os embeddings internamente 
        ou via configuração do provedor de busca.
        """
        self.store = store
        self.embeddings = embeddings

    async def search_relevant_context(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5
    ) -> str:
        """
        Busca memórias semânticas e as formata como contexto para o LLM.
        """
        namespace = ("memories", user_id)
        
        # O LangGraph Store suporta busca semântica se configurado adequadamente
        results = await self.store.asearch(
            namespace,
            query=query,
            limit=limit
        )
        
        if not results:
            return "Nenhuma memória relevante encontrada."
            
        context_parts = [f"- {item.value}" for item in results]
        return "\n".join(context_parts)

    def get_semantic_tips(self):
        """
        Dicas sobre custo e performance.
        """
        return {
            "custo": "Buscas semânticas exigem geração de embeddings (chamada de API).",
            "limitacao": "A qualidade depende do modelo de embedding (ex: text-embedding-3-small).",
            "reuso": "Ideal para 'RAG de memórias' (Memory-RAG)."
        }

# Exemplo didático: 
# Se o usuário diz "Adoro café amargo", salvamos no Store.
# Quando ele pergunta "O que eu gosto de beber?", a busca semântica por "beber" 
# deve retornar a entrada de "café amargo" por proximidade vetorial.

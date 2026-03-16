import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from langgraph.checkpoint.redis import RedisSaver
# NOTA: Até a versão atual do LangGraph, o suporte para 'Store' (long-term) em Redis 
# pode variar ou exigir implementações customizadas se não houver um RedisStore oficial.
# Para fins didáticos e compatibilidade, focaremos no RedisSaver para checkpointer.

class RedisMemoryManager:
    """
    Gerenciador de memória utilizando Redis para LangGraph.
    
    Ideal para cenários de alta performance e memória de curto prazo (checkpoints).
    Para memória de longo prazo persistente de forma durável, o PostgresStore 
    costuma ser o padrão recomendado, mas o Redis também pode ser usado como cache.
    """
    
    def __init__(self, redis_url: str):
        """
        Inicializa o gerenciador com a URL do Redis.
        
        Args:
            redis_url: URI de conexão (ex: redis://localhost:6379)
        """
        self.redis_url = redis_url

    @asynccontextmanager
    async def get_checkpointer(self) -> AsyncGenerator[RedisSaver, None]:
        """
        Factory para o checkpointer de curto prazo (RedisSaver).
        
        Permite persistência de estado de threads em Redis.
        """
        # RedisSaver.from_conn_string é o método comum de inicialização
        saver = RedisSaver.from_conn_string(self.redis_url)
        try:
            yield saver
        finally:
            # O RedisSaver gerencia sua própria conexão no pool
            pass

    def get_long_term_info(self):
        """
        Documentação de suporte:
        Como o LangGraph foca em 'Stores' para long-term memory e o suporte nativo 
        de PostgresStore é mais maduro, para Redis recomenda-se usar o Redis 
        como um Vector Store via LangChain para buscas semânticas (semantic_memory.py).
        """
        return "Para Long-Term em Redis, prefira integração via VectorStore."

def get_redis_url() -> str:
    """
    Recupera a URL do Redis de variáveis de ambiente.
    """
    return os.getenv("REDIS_URL", "redis://localhost:6379")

# Observação sobre versões:
# Certifique-se de ter `langgraph-checkpoint-redis` instalado.

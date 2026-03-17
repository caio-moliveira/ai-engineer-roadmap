import os
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from langgraph.checkpoint.redis import RedisSaver

class RedisMemoryManager:
    """
    Gerenciador de memória utilizando Redis para LangGraph.
    """
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url

    @asynccontextmanager
    async def get_checkpointer(self) -> AsyncGenerator[RedisSaver, None]:
        saver = RedisSaver.from_conn_string(self.redis_url)
        try:
            yield saver
        finally:
            pass

async def main():
    print("--- Demo: Persistência em Redis ---")
    
    # IMPORTANTE: Requer um servidor Redis rodando.
    # Ex: docker run --name some-redis -p 6379:6379 -d redis
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    manager = RedisMemoryManager(url)
    
    try:
        print(f"\n[Sistema] Tentando conectar em: {url}...")
        async with manager.get_checkpointer() as saver:
            print("✓ RedisSaver (Short-Term) conectado com sucesso!")
            
    except Exception as e:
        print(f"\n[ERRO] Não foi possível conectar ao Redis: {e}")
        print("Certifique-se de que o Redis está rodando e a URL está correta.")

if __name__ == "__main__":
    asyncio.run(main())

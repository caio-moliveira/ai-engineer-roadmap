import os
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from langgraph.checkpoint.postgres import PostgresSaver as LangGraphPostgresSaver
from langgraph.store.postgres import PostgresStore

class PostgresMemoryManager:
    """
    Gerenciador de memória utilizando PostgreSQL para LangGraph.
    """
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    @asynccontextmanager
    async def get_checkpointer(self) -> AsyncGenerator[LangGraphPostgresSaver, None]:
        async with await LangGraphPostgresSaver.connect(self.connection_string) as saver:
            await saver.setup()
            yield saver

    @asynccontextmanager
    async def get_store(self) -> AsyncGenerator[PostgresStore, None]:
        async with await PostgresStore.connect(self.connection_string) as store:
            await store.setup()
            yield store

async def main():
    print("--- Demo: Persistência em PostgreSQL ---")
    
    # IMPORTANTE: Requer um banco Postgres rodando.
    # Ex: docker run --name some-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
    uri = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    manager = PostgresMemoryManager(uri)
    
    try:
        print(f"\n[Sistema] Tentando conectar em: {uri}...")
        async with manager.get_checkpointer() as saver:
            print("✓ Checkpointer (Short-Term) conectado com sucesso!")
            
        async with manager.get_store() as store:
            print("✓ Store (Long-Term) conectado com sucesso!")
            
    except Exception as e:
        print(f"\n[ERRO] Não foi possível conectar ao Postgres: {e}")
        print("Certifique-se de que o Postgres está rodando e a URL está correta.")

if __name__ == "__main__":
    asyncio.run(main())

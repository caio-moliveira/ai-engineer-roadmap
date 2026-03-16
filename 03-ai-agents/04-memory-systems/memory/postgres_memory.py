import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from langchain_postgres import PostgresSaver
from langgraph.checkpoint.postgres import PostgresSaver as LangGraphPostgresSaver
from langgraph.store.postgres import PostgresStore

# NOTA: LangGraph utiliza checkpointers para memória de curto prazo (thread-bound)
# e Stores para memória de longo prazo (persistente entre sessões).

class PostgresMemoryManager:
    """
    Gerenciador de memória utilizando PostgreSQL para LangGraph.
    
    Esta classe encapsula a configuração de checkpointers (short-term) 
    e stores (long-term) persistentes.
    """
    
    def __init__(self, connection_string: str):
        """
        Inicializa o gerenciador com a string de conexão do Postgres.
        
        Args:
            connection_string: URI de conexão (ex: postgresql://user:pass@localhost:5432/db)
        """
        self.connection_string = connection_string
        self._checkpointer: Optional[LangGraphPostgresSaver] = None
        self._store: Optional[PostgresStore] = None

    @asynccontextmanager
    async def get_checkpointer(self) -> AsyncGenerator[LangGraphPostgresSaver, None]:
        """
        Factory para o checkpointer de curto prazo (PostgresSaver).
        
        O PostgresSaver permite que o LangGraph salve o estado de cada thread
        diretamente no banco de dados, permitindo retomar conversas.
        """
        async with await LangGraphPostgresSaver.connect(self.connection_string) as saver:
            # Cria as tabelas necessárias se não existirem
            await saver.setup()
            yield saver

    @asynccontextmanager
    async def get_store(self) -> AsyncGenerator[PostgresStore, None]:
        """
        Factory para o store de longo prazo (PostgresStore).
        
        O Store é usado para salvar informações que transcendem uma única thread,
        como preferências do usuário ou memórias semânticas aprendidas.
        """
        async with await PostgresStore.connect(self.connection_string) as store:
            # Cria as tabelas para o Store
            await store.setup()
            yield store

def get_postgres_uri() -> str:
    """
    Recupera a URI do Postgres de variáveis de ambiente ou usa um default seguro para desenvolvimento.
    """
    return os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

# Observação sobre versões: 
# No LangChain/LangGraph >= 0.2.x, o uso de `langgraph.checkpoint.postgres` 
# é a forma recomendada para persistência oficial.

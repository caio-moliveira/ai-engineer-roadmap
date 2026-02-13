import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import FunctionAgent
import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
import asyncio

load_dotenv()

async def main():
    print("--- 04. Agente RAG com Qdrant (LlamaIndex) ---\n")
    
    # 1. Configurações Globais (LLM e Embedding)
    # Definimos o modelo de LLM e de Embedding que serão usados pelo LlamaIndex
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    
    # 2. Conectar ao Qdrant (Localhost)
    # Inicializa o cliente Qdrant e define a collection
    collection_name = "climate_change_collection"
    client = qdrant_client.QdrantClient(host="localhost", port=6333)
    
    print(f"Conectando ao Qdrant na coleção '{collection_name}'...")
    
    # Verificar se a coleção existe e se tem dados
    try:
        count_result = client.count(collection_name=collection_name)
        doc_count = count_result.count
    except Exception:
        doc_count = 0
        print("Coleção não encontrada ou erro ao conectar. Uma nova será criada se necessário.")

    # Inicializar o Vector Store do LlamaIndex com o cliente Qdrant
    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = None
    
    # Se a coleção estiver vazia, carregamos e indexamos os documentos
    if doc_count == 0:
        print("A coleção está vazia. Carregando documentos locais...")
        data_path = os.path.join(os.path.dirname(__file__), "data")
        
        if os.path.exists(data_path):
            documents = SimpleDirectoryReader(data_path).load_data()
            print(f"Carregados {len(documents)} documentos. Indexando no Qdrant...")
            
            # Cria o índice e persiste no Qdrant
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                show_progress=True
            )
            print("Indexação concluída.")
        else:
            print(f"Erro: Diretório de dados '{data_path}' não encontrado. Não é possível popular o índice.")
            return
    else:
        print(f"A coleção '{collection_name}' já contém {doc_count} vetores. Carregando o índice existente...")
        # Carrega o índice existente do Vector Store
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )

    if not index:
        print("Não foi possível inicializar o índice.")
        return

    # 3. Criar Ferramenta de Busca (Query Engine Tool)
    # Transformamos nosso índice em uma ferramenta que o agente pode usar
    query_engine = index.as_query_engine(similarity_top_k=5)
    
    rag_tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name="knowledge_base_mudancas_climaticas",
        description=(
            "Uma ferramenta útil para buscar informações detalhadas e fatos sobre mudanças climáticas, "
            "seus efeitos, causas e dados científicos contidos na base de conhecimento."
        ),
    )

    # 4. Criar o Agente (FunctionAgent)
    # O agente decide quando usar a ferramenta de busca ou responder diretamente (se souber, mas aqui forçamos o uso pelo prompt ou necessidade)
    agent = FunctionAgent(
        tools=[rag_tool],
        llm=Settings.llm,
        verbose=True,
        system_prompt="Você é um assistente especialista em clima. Use a ferramenta de busca para responder perguntas baseadas em dados científicos sempre que possível."
    )

    # 5. Loop de Interação    
    query="Qual é a principal causa da mudança climática?"
    response = await agent.run(query)
    print(f"\nResposta do Agente:\n{response}\n")
            
if __name__ == "__main__":
    asyncio.run(main())

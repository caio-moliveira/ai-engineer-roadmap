from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import VectorParams, Distance, SparseVectorParams

def main():
    # 1. Conexão com o Qdrant
    # Para testes e aprendizado, podemos usar ":memory:", que cria uma instância temporária na memória RAM.
    # Para produção ou persistência local, usaríamos path="path/to/db" ou url="http://localhost:6333" (se rodando via Docker).
    print("Conectando ao Qdrant...")
    # client = QdrantClient(":memory:")  
    client = QdrantClient(host="localhost", port=6333)
    
    # Nome da nossa coleção (similar a uma tabela em bancos relacionais)
    collection_name = "minha_primeira_colecao"

    # 2. Configuração dos Vetores
    # O passo mais importante é definir o `vectors_config`.
    # size: A dimensão dos vetores que serão armazenados. Deve corresponder ao modelo de embeddings usado (ex: OpenAI text-embedding-3-small é 1536).
    # distance: A métrica de distância usada para comparar os vetores.
    #   - Cosine: Comumente usado para similaridade semântica (textos, NLP). Normaliza os vetores.
    #   - Dot: Produto escalar. Bom para vetores já normalizados ou quando a magnitude importa.
    #   - Euclidean: Distância Euclidiana. Bom para dados espaciais ou imagens em certos contextos.
    vector_size = 1536  # Exemplo comum para modelos da OpenAI
    distance_metric = Distance.COSINE

    print(f"Configurando coleção '{collection_name}' com size={vector_size} e distance={distance_metric}...")

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config={"texto-denso": VectorParams(
                size=vector_size,
                distance=distance_metric
            )},
            sparse_vectors_config={'texto-sparse': SparseVectorParams(index=models.SparseIndexParams())}, # Híbrido
        )

    print(f"Coleção '{collection_name}' criada com sucesso!")

    # 4. Verificação
    # Confirmando que a coleção foi criada e verificando seus parâmetros
    collection_info = client.get_collection(collection_name)
    print(f"Info da coleção: {collection_info}")

if __name__ == "__main__":
    main()

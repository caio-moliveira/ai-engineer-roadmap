from qdrant_client import QdrantClient, models

def main():
    client = QdrantClient(host="localhost", port=6333)

    collection_name = "indexing_demo"
    
    if not client.collection_exists(collection_name):  
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE)
        )
    
    # Adicionar muitos pontos para fazer sentido ter index
    # (Em demo pequena não faz diferença de performance, mas o conceito é o que importa)
    points = []
    for i in range(100):
        points.append(
            models.PointStruct(
                id=i,
                vector=[0.1, 0.1], # Vetor dummy
                # Payload com campos que serão filtrados frequentemente
                payload={"categoria": "livros" if i % 2 == 0 else "eletronicos", "rank": i}
            )
        )
        
    client.upsert(collection_name=collection_name, points=points)
    
    print("\n--- 1. Criando Indexes ---")
    
    # Por padrão, o Qdrant já cria índice para os vetores (HNSW).
    # Mas para o Payload (metadados), a busca é "scan" (lenta) a menos que criemos um índice.
    
    # Criando índice para o campo 'categoria'
    # FieldType.KEYWORD: Para textos exatos (strings, categorias, IDs)
    print("Criando indice para 'categoria' (Keyword)...")
    client.create_payload_index(
        collection_name=collection_name,
        field_name="categoria",
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    
    # Criando índice para o campo 'rank'
    # FieldType.INTEGER: Para números (permite range filters rápidos)
    print("Criando indice para 'rank' (Integer)...")
    client.create_payload_index(
        collection_name=collection_name,
        field_name="rank",
        field_schema=models.PayloadSchemaType.INTEGER
    )
    
    # Agora filtros nesses campos serão muito mais rápidos em escala
    
    print("Indices criados com sucesso! O Qdrant agora usa essas estruturas para acelerar filtros.")

if __name__ == "__main__":
    main()

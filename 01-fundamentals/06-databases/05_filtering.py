from qdrant_client import QdrantClient, models


def main():
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "filter_demo"
    
    # Setup - Idempotência
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE)
    )
    
    # Criando dados com payload rico para filtrar
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(id=1, vector=[1.0, 0.0], payload={"cidade": "SP", "preco": 100, "status": "ativo"}),
            models.PointStruct(id=2, vector=[0.9, 0.1], payload={"cidade": "RJ", "preco": 150, "status": "ativo"}),
            models.PointStruct(id=3, vector=[0.0, 1.0], payload={"cidade": "SP", "preco": 200, "status": "inativo"}),
            models.PointStruct(id=4, vector=[0.1, 0.9], payload={"cidade": "MG", "preco": 50,  "status": "ativo"}),
        ]
    )

    query_vector = [1.0, 0.0] # Busca
    
    # 1. Filtro Simples (Must)
    # "Must" = AND (Obrigatório)
    # Quero resultados parecidos com o vetor [1, 0] MAS APENAS de "SP".
    
    print("\n--- 1. Filtro: Cidade = SP (Must) ---")
    my_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="cidade",
                match=models.MatchValue(value="SP")
            )
        ]
    )
    
    # Usando query_points (substituindo client.search)
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        query_filter=my_filter,
        limit=5
    ).points
    
    for hit in results:
        print(f"ID: {hit.id}, Cidade: {hit.payload['cidade']}, Score: {hit.score:.4f}")

    # 2. Filtro Composto (Must + Should + Must Not)
    # Must: Status = ativo
    # Must Not: Cidade = RJ (Excluir RJ)
    # Range: Preço < 200
    
    print("\n--- 2. Filtro Composto ---")
    
    correct_filter = models.Filter(
        must=[
            models.FieldCondition(key="status", match=models.MatchValue(value="ativo")),
            models.FieldCondition(key="preco", range=models.Range(lt=200))
        ],
        must_not=[
            models.FieldCondition(key="cidade", match=models.MatchValue(value="RJ"))
        ]
    )
    
    print("Buscando: Ativos, < 200, Nao RJ")
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        query_filter=correct_filter,
        limit=5
    ).points
    
    for hit in results:
        print(f"ID: {hit.id}, Payload: {hit.payload}")

if __name__ == "__main__":
    main()

from qdrant_client import QdrantClient, models


def main():
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "text_search_demo"
    
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE)
    )
    
    # Dados com texto longo
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(id=1, vector=[0.9, 0.1], payload={"descricao": "Um celular smartphone moderno com camera 4k"}),
            models.PointStruct(id=2, vector=[0.1, 0.9], payload={"descricao": "Uma capa de chuva amarela resistente"}),
            models.PointStruct(id=3, vector=[0.5, 0.5], payload={"descricao": "Livro sobre desenvolvimento de software moderno"}),
        ]
    )

    # 1. Full-Text Search no Payload
    # Para buscar palavras dentro de um texto no payload, precisamos de um Indice de Texto.
    
    print("\n--- 7. Text Search & Híbrido ---")
    print("Criando índice de TEXTO no campo 'descricao'...")
    
    client.create_payload_index(
        collection_name=collection_name,
        field_name="descricao",
        field_schema=models.TextIndexParams(
            type="text",
            tokenizer=models.TokenizerType.WORD, # Quebra por palavras
            min_token_len=2,
            lowercase=True
        )
    )

    # 2. Busca Híbrida (Vetor + Keyword Text Match)
    # Procuramos vectors próximos de [0.9, 0.1] (Tech/Celular)
    # MAS que contenham a palavra "moderno" na descrição.
    
    query_vector = [0.9, 0.1]
    palavra_chave = "moderno"
    
    print(f"Buscando vetor {query_vector} COM a palavra '{palavra_chave}'...")
    
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="descricao",
                    match=models.MatchText(text=palavra_chave) # Busca Full-Text
                )
            ]
        ),
        limit=5
    ).points
    
    for hit in results:
        print(f"ID: {hit.id}, Desc: {hit.payload['descricao']}, Score: {hit.score:.4f}")
        
    print("\nNote que 'Livro' e 'Celular' têm 'moderno', mas o Score vetorial define a ordem.")
    print("Note que 'Capa de chuva' NÃO aparece, pois não tem 'moderno'.")

if __name__ == "__main__":
    main()

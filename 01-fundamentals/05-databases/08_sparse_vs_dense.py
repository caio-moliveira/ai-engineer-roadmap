from qdrant_client import QdrantClient, models

def main():
    client = QdrantClient(host="localhost", port=6333)
    
    print("--- 8. Dense Vectors vs Hybrid (Sparse + Dense) ---")
    
    # ==========================================
    # CENÁRIO A: APENAS DENSE VECTORS
    # ==========================================
    # É o padrão para "busca semântica".
    # Vantagem: Entende o significado (ex: "cachorro" ~= "cão").
    # Desvantagem: Pode falhar em matches exatos de keywords específicas ou códigos (ex: "Erro 404").
    
    collection_dense = "demo_dense_only"
    if client.collection_exists(collection_dense):
        client.delete_collection(collection_dense)
        
    print(f"\nCriando '{collection_dense}' (Apenas Denso)...")
    client.create_collection(
        collection_name=collection_dense,
        # Configuração para um único vetor (unnamed)
        vectors_config=models.VectorParams(
            size=3, # Simplificado para demo
            distance=models.Distance.COSINE
        )
    )
    
    # Inserindo dados: Documentos sobre "Python"
    # Vetor [0.9, 0.1, 0.1] significa "Conteúdo sobre Programação"
    print("Inserindo documentos na coleção Densa...")
    client.upsert(
        collection_name=collection_dense,
        points=[
            models.PointStruct(
                id=1, 
                vector=[0.9, 0.1, 0.1], 
                payload={"text": "Tutorial de Python para Iniciantes (Erro 404 na instalação)"}
            ),
            models.PointStruct(
                id=2, 
                vector=[0.1, 0.9, 0.1], 
                payload={"text": "Receita de Bolo de Cenoura"}
            )
        ]
    )
    
    # Busca Densa: Procurando por "Programação" ([1.0, 0.0, 0.0])
    print(f"Busca Densa: Query=[1.0, 0.0, 0.0] (Conceito de Programação)")
    dense_results = client.query_points(
        collection_name=collection_dense,
        query=[1.0, 0.0, 0.0],
        limit=1
    ).points
    
    for hit in dense_results:
        print(f" -> Encontrou: '{hit.payload['text']}' (Score: {hit.score:.4f})")


    # ==========================================
    # CENÁRIO B: HÍBRIDO (DENSE + SPARSE)
    # ==========================================
    # Combina o melhor dos dois mundos.
    # Dense: Significado.
    # Sparse: Keywords exatas (similar ao BM25/TF-IDF do ElasticSearch/Lucene).
    
    collection_hybrid = "demo_hybrid_setup"
    if client.collection_exists(collection_hybrid):
        client.delete_collection(collection_hybrid)
        
    print(f"\nCriando '{collection_hybrid}' (Híbrido - Denso + Esparso)...")
    client.create_collection(
        collection_name=collection_hybrid,
        
        # 1. Named Vectors (Vetores com nome)
        # Necessário dar nomes quando usamos múltiplos vetores.
        vectors_config={
            "texto-denso": models.VectorParams(
                size=3,
                distance=models.Distance.COSINE
            )
        },
        
        # 2. Sparse Vectors
        # Criamos um índice esparso chamado "texto-sparse"
        sparse_vectors_config={
            "texto-sparse": models.SparseVectorParams(
                index=models.SparseIndexParams(
                    on_disk=False, 
                )
            )
        }
    )
    
    # Inserindo dados Híbridos
    # Para o Sparse Vector, imagine que mapeamos palavras para IDs:
    # "Erro" = ID 10, "404" = ID 11.
    print("Inserindo documentos na coleção Híbrida...")
    client.upsert(
        collection_name=collection_hybrid,
        points=[
            models.PointStruct(
                id=1,
                # Dense Vector: Igual ao anterior (contexto "Programação")
                # Sparse Vector: Marcando fortemente as palavras "Erro" (ID 10) e "404" (ID 11)
                vector={
                    "texto-denso": [0.9, 0.1, 0.1],
                    "texto-sparse": models.SparseVector(
                        indices=[10, 11], 
                        values=[1.0, 1.0]
                    )
                },
                payload={"text": "Tutorial de Python para Iniciantes (Erro 404 na instalação)"}
            )
        ]
    )
    
    # Busca Híbrida: Procurando especificamente pelo código de erro "404"
    # Se usássemos apenas o vetor denso de "Programação", outros tutoriais viriam.
    # Mas aqui queremos o vetor esparso da palavra "404" (ID 11).
    
    print(f"Busca Híbrida: Query no Sparse Vector (ID 11='404')")
    
    # No Qdrant moderno, Hybrid Search é feito via 'prefetch' ou Fusion.
    # Mas podemos consultar apenas o Sparse Vector diretamente também.
    
    hybrid_results = client.query_points(
        collection_name=collection_hybrid,
        # Querying the SPECIFIC named vector "texto-sparse"
        using="texto-sparse",
        query=models.SparseVector(
            indices=[11], # ID da palavra "404"
            values=[1.0]
        ),
        limit=1
    ).points
    
    for hit in hybrid_results:
        print(f" -> Encontrou via Sparse: '{hit.payload['text']}' (Score: {hit.score:.4f})")
    
    print("\nRESUMO DA DIFERENÇA:")
    print("1. 'Dense Only': Encontrou pelo contexto geral 'Programação'.")
    print("2. 'Hybrid/Sparse': Permitiu buscar EXATAMENTE pelo token '404' (simulado pelo ID 11).") 
    print("   Em produção, modelos como SPLADE geram esses índices/valores automaticamente.")

if __name__ == "__main__":
    main()

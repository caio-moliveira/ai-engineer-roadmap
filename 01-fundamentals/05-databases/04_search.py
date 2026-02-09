from qdrant_client import QdrantClient, models


def main():
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "search_demo"
    
    # Setup - Idempotência
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
        
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=3, distance=models.Distance.COSINE)
    )
    
    # 1. Inserindo dados com Payload mais rico (descritivo)
    print("--- 1. Inserindo dados ---")
    points = [
        models.PointStruct(
            id=1, 
            vector=[0.9, 0.1, 0.5], 
            payload={
                "nome": "Dev Backend Senior", 
                "bio": "Especialista em APIs, Rust e Python. Gosta de K8s.",
                "senioridade": "Senior"
            }
        ),
        models.PointStruct(
            id=2, 
            vector=[0.1, 0.9, 0.5], 
            payload={
                "nome": "Gerente de Projetos", 
                "bio": "Certificado PMP, ama Scrum e planilhas.",
                "senioridade": "Pleno"
            }
        ),
        models.PointStruct(
            id=3, 
            vector=[0.5, 0.5, 0.9], 
            payload={
                "nome": "Tech Lead", 
                "bio": "Lidera times técnicos, arquiteta soluções escaláveis.",
                "senioridade": "Staff"
            }
        ),
    ]
    client.upsert(collection_name=collection_name, points=points)
    
    query_vector = [0.95, 0.1, 0.4] # Perfil Técnico (Backend)
    
    # 2. Busca Rápida (Apenas IDs e Scores)
    # Cenário: Você quer recuperar milhares de IDs rapidinho para processar depois,
    # OU você já tem os dados em outro banco (ex: SQL) e só quer o ranking vetorial.
    # Usamos `with_payload=False`.
    
    print("\n--- 2. Busca SUPER RÁPIDA (with_payload=False) ---")
    print("Objetivo: Pegar apenas IDs e Scores (economiza banda e processamento).")
    
    results_fast = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=2,
        with_payload=False # NÃO traz os metadados
    ).points
    
    for hit in results_fast:
        print(f"ID: {hit.id} | Score: {hit.score:.4f} | Payload: {hit.payload}")
        
    print("(Note que o Payload veio vazio/None)")

    # 3. Busca Completa (Trazendo Metadados)
    # Cenário: Você vai mostrar o resultado direto pro usuário (ex: Nome, Bio).
    # Usamos `with_payload=True` (ou especificamos quais campos queremos).
    
    print("\n--- 3. Busca COMPLETA (with_payload=True) ---")
    print("Objetivo: Pegar o 'Bio' e 'Nome' para exibir na tela.")
    
    results_full = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=2,
        with_payload=True # Traz TODO o payload
    ).points

    for point in results_full:
        print(f"ID: {point.id} | Score: {point.score:.4f}")
        print(f" -> Nome: {point.payload['nome']}")
        print(f" -> Bio:  {point.payload['bio']}")

if __name__ == "__main__":
    main()

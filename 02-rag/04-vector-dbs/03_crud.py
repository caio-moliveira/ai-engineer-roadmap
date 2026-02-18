from qdrant_client import QdrantClient, models
import uuid


def main():
    # Setup inicial (igual ao passo 02)
    # Para testes repetidos, vamos conectar
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "crud_demo"
    
    # IMPORTANTE: Em scripts de exemplo, checamos se existe para recriar do zero.
    # Isso garante que o script sempre rode limpo (sem erro de "já existe").
    if not client.collection_exists(collection_name):  
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=3, distance=models.Distance.COSINE)
        )
    
    print(f"--- Coleção '{collection_name}' criada ---")

    # 1. CREATE / UPSERT (Inserir ou Atualizar Pontos)
    # Estrutura de Payload mais rica: { "content": "texto...", "metadata": { ... } }
    
    print("--- 1. Inserindo 3 pontos com metadados ricos ---")
    # points_to_upsert = [
    #     models.PointStruct(
    #         id=1,
    #         vector=[0.1, 0.9, 0.0],
    #         payload={
    #             "content": "Introdução à Inteligência Artificial",
    #             "metadata": {
    #                 "author": "Alice",
    #                 "year": 2023,
    #                 "tags": ["AI", "Tech"]
    #             }
    #         }
    #     ),
    #     models.PointStruct(
    #         id=2,
    #         vector=[0.2, 0.8, 0.1],
    #         payload={
    #             "content": "Machine Learning para Iniciantes",
    #             "metadata": {
    #                 "author": "Bob",
    #                 "year": 2022,
    #                 "tags": ["ML", "Data Science"]
    #             }
    #         }
    #     ),
    #     models.PointStruct(
    #         id=3,
    #         vector=[0.9, 0.1, 0.5],
    #         payload={
    #             "content": "História dos Bancos de Dados",
    #             "metadata": {
    #                 "author": "Charlie",
    #                 "year": 2020,
    #                 "tags": ["DB", "SQL"]
    #             }
    #         }
    #     )
    # ]
    
    # operation_info = client.upsert(
    #     collection_name=collection_name,
    #     points=points_to_upsert
    # )
    # print(f"Status do Upsert: {operation_info.status}")

    # 2. READ (Ler Pontos por ID)
    # print(f"\n--- 2. Leitura de Pontos (Retrieve ID 1 e 3) ---")
    # retrieved_points = client.retrieve(
    #     collection_name=collection_name,
    #     ids=[1, 3],
    #     with_payload=True,
    #     with_vectors=True 
    # )
    
    # for p in retrieved_points:
    #     print(f"ID: {p.id}")
    #     print(f"  Content: {p.payload['content']}")
    #     print(f"  Metadata: {p.payload['metadata']}")
    #     print(f"  Vector: {p.vector}")

    # # 3. UPDATE PAYLOAD (Atualizar apenas metadados)
    # # Vamos adicionar uma visualização ao post do 'Bob' (ID 2) dentro do objeto 'metadata'
    # # Nota: set_payload faz merge no nível superior. Para atualizar nested fields, você substitui o objeto pai ou usa set_payload com cuidado.
    # # Aqui vamos adicionar um campo novo no nível raiz para simplificar o exemplo de "Update".
    
    # print(f"\n--- 3. Atualizando Payload do ID 2 ---")
    # client.set_payload(
    #     collection_name=collection_name,
    #     payload={
    #         "views": 1500,  # Campo novo
    #         "status": "reviewed"
    #     },
    #     points=[2] 
    # )
    
    # updated_point = client.retrieve(collection_name=collection_name, ids=[2])[0]
    # print(f"Payload atualizado (ID 2): {updated_point.payload}")

    # # 4. DELETE (Deletar Pontos)
    print(f"\n--- 4. Deletando o ID 3 ---")
    client.delete(
        collection_name=collection_name,
        points_selector=models.PointIdsList(
            points=[3]
        )
    )
    
    remaining = client.count(collection_name=collection_name)
    print(f"Total de pontos restantes: {remaining.count}")

if __name__ == "__main__":
    main()

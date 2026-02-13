from qdrant_client import models

def main():
    """
    01 - Conceitos Fundamentais do Qdrant
    
    Este script não conecta ao banco de dados, mas demonstra as estruturas de dados
    que representam os conceitos principais: Collection, Point, Vector e Payload.
    """
    
    # 1. Collection (Coleção)
    # Uma coleção é um conjunto de pontos nomeados (similar a uma tabela SQL).
    # Ela tem uma configuração obrigatória de vetores.
    vector_config = models.VectorParams(
        size=1536,                      # Dimensão do vetor (ex: OpenAI)
        distance=models.Distance.COSINE # Métrica de distância (Cosine, Euclid, Dot)
    )
    print(f"--- 1. Configuração de Coleção ---\n{vector_config}\n")

    # 2. Point (Ponto)
    # É a unidade básica de dados. Contém:
    # - id: Identificador único (int ou UUID)
    # - vector: A lista de floats (o embedding em si)
    # - payload: Um dicionário de metadados (JSON)
    
    point_example = models.PointStruct(
        id=1,
        vector=[0.1, 0.9, 0.5, ...],  # Vetor simplificado para visualização
        payload={
            "titulo": "Tutorial Qdrant",
            "tags": ["banco vetorial", "python"],
            "vies": 0.99
        }
    )
    
    print("--- 2. Estrutura de um Ponto (PointStruct) ---")
    print(f"ID: {point_example.id}")
    print(f"Payload: {point_example.payload}")
    print("Vector: [0.1, 0.9, ...]") # Representação visual
    
    # 3. Payload (Carga útil)
    # Dados anexados ao vetor. Permitem filtragem e busca híbrida.
    # No Qdrant, o payload é schemaless (como no MongoDB).
    payload_exemplo = {
        "cidade": "São Paulo",
        "contagem": 10,
        "ativo": True
    }
    print(f"\n--- 3. Payload ---\nExemplo de metadados: {payload_exemplo}\n")
    
    print("Resumo:")
    print("O Qdrant armazena Points dentro de Collections.")
    print("Cada Point tem um ID, um Vector (para busca semântica) e um Payload (para filtros).")

if __name__ == "__main__":
    main()

import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(v1, v2):
    # Fórmula: (A . B) / (||A|| * ||B||)
    prod_escalar = np.dot(v1, v2)
    norma_v1 = np.linalg.norm(v1)
    norma_v2 = np.linalg.norm(v2)
    return prod_escalar / (norma_v1 * norma_v2)

def main():
    print("=== A Mágica do RAG: Busca Semântica ===\n")
    
    # 1. Carregar Modelo
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 2. Base de Conhecimento (Simulada)
    # Imagine que isso são pedaços (chunks) de documentos do PDF da aula.
    documentos = [
        "A fotossíntese é o processo usado por plantas para converter luz em energia.", # Bio
        "O PIB do Brasil cresceu 2% no último trimestre.",                             # Econ
        "A receita de bolo de cenoura leva 3 ovos e farinha.",                         # Culinária
        "O Python é uma linguagem de programação muito popular para IA.",              # Tech
        "O React é uma biblioteca JavaScript para criar interfaces de usuário."        # Tech
    ]
    
    # 3. Gerar Embeddings para a Base Inteira (Indexação)
    print("Indexando documentos (gerando vetores)...")
    doc_embeddings = model.encode(documentos)
    
    # 4. A Pergunta do Usuário (Query)
    pergunta = "Como aprender a programar inteligência artificial?"
    print(f"\nPergunta: '{pergunta}'")
    
    # 5. Transformar Pergunta em Vetor
    query_embedding = model.encode([pergunta])[0]
    
    # 6. Calcular Similaridade (Busca)
    scores = []
    for i, doc_vec in enumerate(doc_embeddings):
        sim = cosine_similarity(query_embedding, doc_vec)
        scores.append((sim, documentos[i]))
    
    # 7. Ordenar por Similaridade (Ranking)
    scores.sort(key=lambda x: x[0], reverse=True)
    
    # 8. Exibir Resultados (Top 3)
    print("\n--- Resultados da Busca ---")
    for score, texto in scores[:3]:
        print(f"[Score: {score:.4f}] {texto}")
        
    # Observação:
    # A pergunta "aprender a programar IA" trouxe o documento sobre Python como #1.
    # Mesmo sem a palavra "aprender" estar explícita no documento.
    # Isso é busca SEMÂNTICA. O "meaning" (significado) bateu.
    
    pergunta_culinaria = "ingredientes para sobremesa"
    print(f"\nPergunta: '{pergunta_culinaria}'")
    query_culinaria_emb = model.encode([pergunta_culinaria])[0]
    
    scores_culinaria = []
    for i, doc_vec in enumerate(doc_embeddings):
        sim = cosine_similarity(query_culinaria_emb, doc_vec)
        scores_culinaria.append((sim, documentos[i]))
        
    scores_culinaria.sort(key=lambda x: x[0], reverse=True)
    
    print("\n--- Resultados da Busca (Culinária) ---")
    for score, texto in scores_culinaria[:3]:
        print(f"[Score: {score:.4f}] {texto}")

if __name__ == "__main__":
    main()

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import time

def explanation_step(title, content):
    print(f"\n\n=== {title} ===")
    print(content)
    # time.sleep(1)

def main():
    print("Bem-vindo à Aula: Embeddings Reais (Simplificados)")
    print("--------------------------------------------------")
    
    explanation_step("1. O Conceito", 
        "Em vez de inventar números, vamos usar uma IA REAL para gerar os vetores.\n"
        "O modelo 'all-MiniLM-L6-v2' gera vetores de 384 dimensões.\n"
        "Como não dá para ler 384 números, vamos usar um algoritmo matemático (PCA)\n"
        "para 'espremer' essa informação em apenas 3 números (Dimensões) para facilitar a leitura.")

    # 1. Carregar Modelo Real
    print("\n[Carregando modelo de IA...]")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 2. Definir Conceitos para Comparar
    palavras = [
        "Cachorro", "Lobo", "Husky",  # Grupo Caninos
        "Gato", "Tigre",              # Grupo Felinos
        "Banana", "Maçã",             # Grupo Frutas
        "Brasil", "França"            # Grupo Países
    ]
    
    # 3. Gerar Embeddings (384 dimensões)
    embeddings_reais = model.encode(palavras)
    
    # 4. Reduzir para 3 Dimensões (para visualização didática)
    # random_state fixo para garantir que os números sejam sempre os mesmos na aula
    pca = PCA(n_components=3, random_state=42) 
    embeddings_3d = pca.fit_transform(embeddings_reais)
    
    explanation_step("2. Os Vetores Gerados (3 Dimensões Principais)",
        "Olhe como a IA agrupou os significados matematicamente:")
    
    # Dicionário para facilitar acesso
    vetores_dict = {}
    
    print(f"\n{'PALAVRA':<10} | {'VETOR 3D (Simplificado)':<30}")
    print("-" * 45)
    
    for i, palavra in enumerate(palavras):
        vec = embeddings_3d[i]
        vetores_dict[palavra] = vec
        # Formatar vetor bonitinho
        vec_str = f"[{vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f}]"
        print(f"{palavra:<10} | {vec_str}")

    explanation_step("3. Comparando Similaridade (Cosine Similarity) **DIREÇÃO**",
        "Desta vez usaremos a métrica OFICIAL de IA: Cosine Similarity.\n"
        "- 1.0  = Significado IGUAL\n"
        "- 0.0  = Nada a ver\n"
        "- -1.0 = Significado OPOSTO")
        
    def calcular_cosine_similarity(p1, p2):
        v1 = vetores_dict[p1]
        v2 = vetores_dict[p2]
        # Similarity = (A . B) / (||A|| * ||B||)
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        return dot_product / (norm_v1 * norm_v2)

    # Comparações
    pares = [
        ("Cachorro", "Lobo"),      
        ("Cachorro", "Gato"),     
        ("Cachorro", "Banana"),   
        ("Brasil", "França"),      
        ("Brasil", "Banana")       
    ]
    
    print(f"\n{'COMPARAÇÃO':<25} | {'SIMILARIDADE':<12} | {'CONCLUSÃO'}")
    print("-" * 60)
    
    for p1, p2 in pares:
        sim = calcular_cosine_similarity(p1, p2)
        
        conclusao = "Diferente"
        if sim > 0.8: conclusao = "MUITO PARECIDO"
        elif sim > 0.5: conclusao = "Relacionado"
            
        print(f"{p1} <-> {p2:<10} | {sim:.4f}       | {conclusao}")

    # 5. Explicação Detalhada do Cálculo
    explanation_step("4. DESVENDANDO A MÁGICA (Cálculo Passo-a-Passo)",
        "Como o computador sabe que Brasil e França são parecidos?\n"
        "Usando a fórmula do COSSENO: (A . B) / (||A|| * ||B||)")
    
    v_bra = vetores_dict["Brasil"]
    v_fra = vetores_dict["França"]
    
    print(f"Vetor Brasil (A): [{v_bra[0]:.3f}, {v_bra[1]:.3f}, {v_bra[2]:.3f}]")
    print(f"Vetor França (B): [{v_fra[0]:.3f}, {v_fra[1]:.3f}, {v_fra[2]:.3f}]")
    
    # print("\nPASSO 1: Dot Product (Produto Escalar)")
    # print("Multiplica cada posição e soma tudo: (x1*x2) + (y1*y2) + (z1*z2)")
    
    # dot_prod = (v_bra[0] * v_fra[0]) + (v_bra[1] * v_fra[1]) + (v_bra[2] * v_fra[2])
    
    # print(f"({v_bra[0]:.2f}*{v_fra[0]:.2f}) + ({v_bra[1]:.2f}*{v_fra[1]:.2f}) + ({v_bra[2]:.2f}*{v_fra[2]:.2f})")
    # print(f"Resultado Dot Product = {dot_prod:.4f}")
    
    # print("\nPASSO 2: Magnitude (Tamanho da seta)")
    # print("Raiz da soma dos quadrados: sqrt(x²+y²+z²)")
    
    # norm_bra = np.linalg.norm(v_bra)
    # norm_fra = np.linalg.norm(v_fra)
    
    # print(f"Magnitude Brasil = {norm_bra:.4f}")
    # print(f"Magnitude França = {norm_fra:.4f}")
    
    # print("\nPASSO 3: Divisão Final")
    # print("Dot Product / (MagA * MagB)")
    
    # similarity = dot_prod / (norm_bra * norm_fra)
    
    # print(f"{dot_prod:.4f} / ({norm_bra:.4f} * {norm_fra:.4f})")
    # print(f"Resultado Final = {similarity:.4f}")
    
    # print("\nMatemática Pura! O ângulo entre as setas nos diz o quão similar são as palavras.")

    print("\nMatemática Pura! O ângulo entre as setas nos diz o quão similar são as palavras.")

def exemplo_frases_reais():
    explanation_step("5. Exemplo Prático: Frases e Perguntas (RAG)", 
        "Palavras soltas são fáceis. Mas e frases inteiras?\n"
        "O embedding captura o SENTIDO da frase, independente das palavras usadas.")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    base_de_conhecimento = [
        "A empresa teve lucro de 10 milhões esse ano.",   # Finanças
        "O cachorro correu feliz pelo parque.",           # Animais
        "A receita de bolo precisa de farinha e ovos.",   # Culinária
        "O mercado de ações fechou em alta.",             # Finanças
        "Os felinos são animais muito independentes."     # Animais
    ]
    
    pergunta = "Investimentos e economia"
    
    print(f"\nPergunta: '{pergunta}'")
    print("\nCalculando similaridade com a base...")
    print("-" * 60)
    print(f"{'FRASE':<50} | {'SIMILARIDADE'}")
    print("-" * 60)
    
    # Gerar embeddings
    emb_pergunta = model.encode(pergunta)
    emb_base = model.encode(base_de_conhecimento)
    
    # Calcular similaridade para cada frase
    for i, frase in enumerate(base_de_conhecimento):
        emb_frase = emb_base[i]
        
        # Cosseno na mão (usando numpy para ser rápido)
        sim = np.dot(emb_pergunta, emb_frase) / (np.linalg.norm(emb_pergunta) * np.linalg.norm(emb_frase))
        
        print(f"{frase:<50} | {sim:.4f}")
        
    print("-" * 60)
    print("CONCLUSÃO:")
    print("A frase 'O mercado de ações fechou em alta' tem alta similaridade,")
    print("mesmo NÃO tendo a palavra 'economia' ou 'investimentos'.")
    print("Isso é Busca Semântica!")

if __name__ == "__main__":
    main()
    exemplo_frases_reais()

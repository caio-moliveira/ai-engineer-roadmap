import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def main():
    print("=== Visualizando Embeddings (Redução de Dimensionalidade) ===\n")
    
    # 1. Dados: Vamos criar grupos distintos
    grupos = {
        "Frutas": ["Maçã", "Banana", "Laranja", "Uva", "Manga"],
        "Animais": ["Cachorro", "Gato", "Leão", "Tigre", "Elefante"],
        "Cidades": ["Nova York", "Londres", "Tóquio", "Paris", "São Paulo"],
        "Carros": ["Fusca", "Ferrari", "BMW", "Toyota", "Ford"]
    }
    
    # Preparar listas planas
    textos = []
    labels_cores = []
    cores = ['red', 'blue', 'green', 'black']
    
    cor_map = {}
    
    idx = 0
    for categoria, lista_itens in grupos.items():
        cor_map[categoria] = cores[idx]
        for item in lista_itens:
            textos.append(item)
            labels_cores.append(cores[idx])
        idx += 1
            
    # 2. Gerar Embeddings (Alta Dimensão: 384 dims)
    print("Gerando embeddings...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(textos)
    
    # 3. Redução para 2D (PCA ou t-SNE)
    # PCA busca eixos de maior variância (mais rápido, linear)
    # t-SNE busca preservar vizinhança local (melhor p/ visualização, não-linear)
    
    print("Reduzindo para 2D com PCA...")
    pca = PCA(n_components=2)
    coords_2d = pca.fit_transform(embeddings)
    
    # 4. Plotagem
    print("Gerando gráfico...")
    plt.figure(figsize=(10, 8))
    
    # Scatter plot
    for categoria, cor in cor_map.items():
        # Filtra pontos desta categoria para criar legenda correta
        indices = [i for i, c in enumerate(labels_cores) if c == cor]
        pontos_x = coords_2d[indices, 0]
        pontos_y = coords_2d[indices, 1]
        plt.scatter(pontos_x, pontos_y, c=cor, label=categoria, s=100)
        
    # Anotar cada ponto com o texto
    for i, texto in enumerate(textos):
        plt.annotate(texto, (coords_2d[i, 0], coords_2d[i, 1]), xytext=(5, 5), textcoords='offset points')
        
    plt.title("Visualização de Embeddings (PCA)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Salvar em vez de mostrar (para evitar travar em ambientes headless)
    output_file = "embeddings_visualization.png"
    plt.savefig(output_file)
    print(f"Gráfico salvo como '{output_file}'. Abra para ver!")
    
    # plt.show() # Descomente se rodar em ambiente com GUI

if __name__ == "__main__":
    main()

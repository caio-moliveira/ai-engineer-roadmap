# 🔢 Módulo 3: Embeddings

> **Goal:** Transformar texto em números (Coordenadas Semânticas).  
> **Status:** A fundação da Busca Semântica.

## 1. O que é um Embedding?
É uma lista de números (um vetor) que representa o "Significado" de um texto.
`[0.12, -0.98, 0.44, ...]`

- **Mágica:** Nesse espaço de 1536 dimensões, "Rei" - "Homem" + "Mulher" ≈ "Rainha".
- **Semântica:** "Cachorro" está mais perto de "Filhote" do que de "Gato", e mais perto de "Gato" do que de "Carro".

## 2. Escolha do Modelo (2025)
Não use apenas a OpenAI cegamente.

| Modelo | Provedor | Dims | Pros | Contras |
|:---|:---|:---|:---|:---|
| **text-embedding-3-small** | OpenAI | 1536 | Barato, rápido, padrão. | Privacidade, Custo em escala. |
| **text-embedding-3-large** | OpenAI | 3072 | Maior acurácia. | 2x custo, 2x tamanho de storage. |
| **bge-m3 / multilingual-e5** | Open Source | 1024 | Grátis, roda local, bate a OpenAI. | Você precisa hospedar (GPU necessária). |
| **Cohere Embed v3** | Cohere | 1024 | Especializado em RAG. | Custo de API. |

## 3. A "Maldição da Dimensionalidade"
- **Mais Dimensões** = Mais Nuance = Mais Custo de Storage ($$$) + Busca mais Lenta.
- O `text-3` da OpenAI permite **Encurtar Embeddings**. Você pode cortar o vetor de 1536 para 512 e perder apenas ~2% de acurácia.

## 4. Métricas de Distância
Como medimos a "proximidade"?
1.  **Cosine Similarity:** O padrão. Mede o ângulo. (1.0 = Igual, 0 = Ortogonal, -1 = Oposto).
2.  **Dot Product:** Apenas para vetores normalizados. Mais rápido.
3.  **Euclidean (L2):** Mede a distância em linha reta. Raramente usado para texto.

## 🧠 Mental Model: "O Mapa da Biblioteca"
Embeddings são coordenadas de GPS para os livros na biblioteca.
- Livros de "Culinária" estão na Latitude 40.
- Livros de "História" estão na Latitude 80.
- Uma pergunta "Melhor receita de massa" cai na Latitude 40.01.
Nós apenas olhamos os livros mais próximos.

## ⚠️ Erros Comuns
- **Misturar Modelos:** Você NÃO PODE buscar um vetor `bge-m3` contra um vetor `openai`. Você deve re-indexar tudo se trocar de modelo.
- **Ignorar Multilingual:** OpenAI é decente, mas `multilingual-e5` é muito melhor para Português/Espanhol.

## ⏭️ Próximo Passo
Onde guardamos esses milhões de vetores?
Vá para **[Módulo 4: Vector Databases](../04-vector-dbs)**.

# 🗄️ Módulo 4: Vector Databases

> **Goal:** Busca em Alta Velocidade.  
> **Status:** O Postgres da IA.

## 1. O que ele faz?
DBs Padrão (SQL) são bons em match exato (`id = 5`).
Vector DBs são bons em match aproximado (`significado ≈ "redes neurais"`).

Ele usa algoritmos **ANN (Approximate Nearest Neighbor)** como **HNSW** para encontrar vetores próximos em milissegundos, mesmo com 100M de registros.

## 2. Cenário de Mercado (2025)

### Dedicated Vector DBs
- **Qdrant:** Baseado em Rust. Rápido. Design focado em filtros. Melhor Developer Experience (DX).
- **Weaviate:** Baseado em Go. Módulos de embedding embutidos. Bom para dados não estruturados.
- **Pinecone:** Totalmente gerenciado (SaaS). Fácil de começar. Caro em escala.

### Integrados (O Stack "Bom o Suficiente")
- **pgvector (Postgres):** Apenas uma extensão. Perfeito se você já tem Postgres e <1M vetores.
- **Elasticsearch:** O motor de busca clássico. Aprendeu a fazer KNN decente.

### 🏆 Recomendação
- **Comece com:** `pgvector` (Mantenha o stack simples).
- **Escale para:** `Qdrant` (Quando precisar de performance/filtragem pesada).

## 3. Filtragem de Metadados (A armadilha do "pós-filtro")
**Cenário:** Achar "Emails sobre impostos" do "Usuário A".

- **Post-Filter (Ruim):** Acha 100 emails de impostos (de qualquer pessoa), depois filtra pelo Usuário A. Resultado: 0 emails encontrados.
- **Pre-Filter (Bom):** Filtra pelo Usuário A primeiro, *depois* faz a busca vetorial.
- **Qdrant/Pinecone** lidam com isso automaticamente.

## 4. Indexação (HNSW Explicado)
HNSW (Hierarchical Navigable Small World) é um "Mapa com Zoom".
- **Camada 0:** Todos os pontos (Street View).
- **Camada 1:** Conecta bairros (Visão da Cidade).
- **Camada 2:** Conecta cidades (Visão do País).
A busca começa no topo e vai dando zoom.

## 5. Escalabilidade
- **Vetores são pesados.** 1M de vetores OpenAI = ~3GB RAM.
- **Disco vs RAM:**
    - **In-Memory:** Mais rápido. Caro.
    - **On-Disk (Mmap):** Mais lento, mas permite datasets maiores que a RAM. Qdrant brilha aqui.

## 🧠 Mental Model: "Por que não NumPy?"
Você *pode* achar vizinhos próximos com `np.dot(query, all_vectors)`.
Mas isso é complexidade **O(N)**.
Vector DBs são **O(log N)**.
Se tiver 10k itens, use NumPy.
Se tiver 10M itens, use um Vector DB.

### 2. 

## ⏭️ Próximo Passo
Temos o DB. Como fazemos perguntas boas?
Vá para **[Módulo 5: Estratégias de Retrieval](../05-retrieval-strategies)**.

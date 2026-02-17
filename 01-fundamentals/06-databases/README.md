# 🗄️ Módulo 6: Vector Databases e Bancos de Dados Relacionais

> **Goal:** Entender a diferença entre Bancos Relacionais, NoSQL e Vetoriais, e aplicar na prática com Qdrant.  
> **Status:** O "Cérebro" da Memória de Longo Prazo da IA.

## 1. Relacional (SQL) vs. Vetorial (Vector DB)

A principal diferença reside na **natureza dos dados** e **como a busca é feita**.

### 🏦 Banco de Dados Relacional (SQL)
*   **Estrutura:** Tabelas rígidas (linhas e colunas). Schema definido (`CREATE TABLE users...`).
*   **Busca:** Exata e determinística.
    *   `SELECT * FROM users WHERE email = 'john@example.com'` -> Retorna exatamente o registro ou nada.
    *   `LIKE '%termo%'` -> Busca substring exata, sem contexto semântico.
*   **Uso:** Sistemas transacionais (ERP, CRM, E-commerce), dados financeiros, cadastros.
*   **Exemplos:** [PostgreSQL](https://www.postgresql.org/), MySQL, SQL Server.

### 🧭 Banco de Dados Vetorial (Vector DB)
*   **Estrutura:** Armazena **Vetores (Embeddings)** e metadados JSON (payload). Não exige schema rígido para os dados, mas sim para a configuração da coleção (dimensão do vetor).
*   **Busca:** Aproximada e Semântica (Similaridade).
    *   "Encontre documentos que falem sobre *inteligência artificial*" -> Retorna textos sobre "Machine Learning", "Neural Networks", mesmo sem a palavra exata "inteligência artificial".
*   **Mecanismo:** Transforma dados não estruturados (Texto, Imagem, Áudio) em vetores numéricos e calcula a distância entre eles num espaço multidimensional.
*   **Uso:** RAG (Retrieval-Augmented Generation), Recomendação, Busca Semântica, Detecção de Anomalias.

---

## 2. NoSQL vs. Vector Databases

É comum confundir porque ambos lidam bem com dados não estruturados (JSON, Documents), mas o **propósito** é diferente.

*   **NoSQL (ex: MongoDB, DynamoDB):**
    *   Focado em armazenar e recuperar documentos JSON inteiros ou fazer queries em campos específicos do JSON.
    *   Excelente para alta vazão de escrita/leitura de objetos.
    *   *Limitação:* Não é nativamente otimizado para cálculos matemáticos complexos de distância entre vetores em alta velocidade (embora alguns estejam adicionando funcionalidades vetoriais agora).

*   **Vector Database (ex: Qdrant, Pinecone):**
    *   Focado em **indexar vetores** para busca de similaridade (ANN - Approximate Nearest Neighbor).
    *   O "Documento" (payload) é secundário; o protagonista é o **Vetor**.
    *   Ele armazena os vetores gerados a partir dos seus documentos não estruturados.

> **Resumo:** Use NoSQL para guardar o objeto. Use Vector DB para *encontrar* o objeto pelo seu significado.

---

## 3. Características e Parâmetros Importantes

Ao configurar um Vector DB, você encontrará estes termos cruciais:

1.  **Dimensão (Dimension):** O tamanho do vetor. Deve ser **idêntico** ao modelo de embedding usado.
    *   Ex: `OpenAI text-embedding-3-small` gera vetores de **1536** dimensões. Sua coleção no Qdrant *precisa* ser criada com `size: 1536`.
2.  **Métrica de Distância (Distance Metric):** Como calcular a similaridade.
    *   **Cosine Similarity (Cosseno):** Mais comum para NLP (texto). Mede o ângulo entre vetores. (Recomendado para OpenAI).
    *   **Dot Product:** Para sistemas de recomendação.
    *   **Euclidean:** Distância física direta.
3.  **HNSW (Hierarchical Navigable Small World):** O algoritmo de indexação padrão da indústria. Pense nele como um "mapa de ruas" eficiente para navegar no espaço vetorial sem precisar comparar com *todos* os pontos (o que seria lento).

---

## 4. 🏆 Recomendação: Qdrant

Para este roadmap e para aplicações reais, recomendamos fortemente o **[Qdrant](https://qdrant.tech/)**.

### Por que Qdrant?
1.  **Performance:** Escrito em **Rust**. Extremamente rápido e eficiente em memória.
2.  **Flexibilidade:** Funciona bem para uma simples POC (Proof of Concept) rodando na memória do seu laptop e escala para cluster de produção com terabytes de dados.
3.  **Filtragem Híbrida:** O "matador de features". Ele permite filtrar por metadados *enquanto* busca vetores (ex: "Busque documentos sobre 'gatos' (vetor) mas APENAS do ano 2024 (filtro)"). Outros DBs sofrem com "post-filtering" (filtram depois da busca, perdendo precisão).
4.  **Developer Experience:** API Python excelente e documentação clara.

### POC vs. Produção
*   **POC:** Use o modo "Local" (em memória ou disco local). Zero setup de infra.
*   **Produção:** Use **Docker** ou **Qdrant Cloud**.

---

## 5. Mão na Massa: Como Usar o Qdrant

### Instalação
```bash
pip install qdrant-client
```

### 🐍 Opção 1: Qdrant Local (Python puro)
Perfeito para testes rápidos. O banco roda *dentro* do seu script Python.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Init: Armazena em RAM (volátil)
# client = QdrantClient(":memory:") 

# Init: Armazena em disco local (persistente)
client = QdrantClient(path="./qdrant_db") 

# Criar Coleção
client.create_collection(
    collection_name="my_books",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

print("Qdrant Local iniciado com sucesso!")
```

### 🐳 Opção 2: Qdrant via Docker (Recomendado para Dev/Prod)
Roda como um serviço separado (como um Postgres). Isso é o mais próximo de um ambiente real.

1.  **Rodar Container:**
    ```bash
    docker run -p 6333:6333 -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant
    ```

2.  **Conectar via Python:**
    ```python
    # Conecta no serviço rodando no Docker
    client = QdrantClient(url="http://localhost:6333")
    
    # O resto do código (criar coleção, upsert, search) é IDÊNTICO.
    ```

## ⏭️ Próximo Passo
Agora que temos onde guardar nossos vetores, precisamos entender como *trazer* a informação certa de volta.
Vá para **[Módulo 5: Estratégias de Retrieval](../05-retrieval-strategies)** (ou continue explorando a ingestão de dados).

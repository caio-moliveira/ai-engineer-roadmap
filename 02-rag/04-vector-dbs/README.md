# 🗄️ Módulo 04: Bancos de Dados (Relacional + Vetorial)

> **Goal:** Onde a memória e o contexto semântico vivem.
> **Ferramentas:** `Vector DBs` [Qdrant](https://qdrant.tech/documentation/concepts/collections/), `LangChain`.

---

## 🚀 O Novo Stack de Dados: Exato vs Semântico

Aplicações de IA modernas combinam dois "cérebros":

1.  **Exato (SQL)** — Consultas precisas e estruturas rígidas (ex: "Quantos produtos vendeu no mês X?"). Ideal para **fatos**.
2.  **Semântico (Vector DB)** — Consultas por **significado e contexto** (ex: "Quais documentos falam sobre cláusulas abusivas?"). Ideal para **conhecimento**.

Combinar esses dois é o que chamamos de **SQL + RAG (Retrieval-Augmented Generation)**.

---

## � O que é um Vector Database?

Um banco vetorial armazena dados como **Vectors (Embeddings)** em vez de (apenas) linhas e colunas.

*   **Embedding**: Uma lista de números (`[0.1, 0.9, -0.5...]`) que representa o significado de um texto, imagem ou áudio.
*   **Busca Semântica**: Ao invés de `WHERE title = 'Java'`, fazemos "Encontre os vetores mais próximos (matematicamente) da pergunta do usuário".
*   **Métrica de Distância**: Como calculamos "proximidade"? (Cosine Similarity é o padrão para textos).

---

## 🎓 Curso Prático: Qdrant Fundamentals

Criamos uma série de scripts Python (`01` a `08`) para você aprender na prática, do zero ao avançado.

### 📂 Estrutura do Curso

| Arquivo | Tópico | O que você aprende |
| :--- | :--- | :--- |
| **[01_concepts.py](./01_concepts.py)** | **Conceitos** | O que é `Collection`, `Point`, `Vector` e `Payload` sem conectar no banco. |
| **[02_setup_qdrant.py](./02_setup_qdrant.py)** | **Setup** | Conectar (`:memory:` vs Docker) e criar coleções definindo `VectorParams`. |
| **[03_crud.py](./03_crud.py)** | **CRUD** | **Create** (Upsert), **Read** (Retrieve ID), **Update** (Payload), **Delete**. |
| **[04_search.py](./04_search.py)** | **Busca** | A diferença entre pegar só IDs (`payload=False`) vs Objetos Completos. |
| **[05_filtering.py](./05_filtering.py)** | **Filtros** | Cláusulas `Must`, `Should`, `MustNot` (a lógica booleana vetorial). |
| **[06_indexing.py](./06_indexing.py)** | **Performance** | Criar `Payload Index` para acelerar filtros em metadados (Text, Int, Keyword). |
| **[07_hybrid_search.py](./07_hybrid_search.py)** | **Híbrido (V1)** | Vetor + Keyword Match no Payload (ex: achar "celular" que tenha a palavra "X"). |
| **[08_sparse_vs_dense.py](./08_sparse_vs_dense.py)** | **Híbrido (V2)** | **Dense** (Significado) vs **Sparse** (Keywords exatas/SPLADE). O estado da arte. |

---

## 🛠️ Deep Dive: Classes e Parâmetros do Qdrant

Aqui explicamos o "porquê" de cada linha de código usada nos exemplos.

### 1. `QdrantClient`
O ponto de entrada.
*   `QdrantClient(":memory:")`: Cria um banco temporário na RAM. Ótimo para testes unitários ou estudar.
*   `QdrantClient(host="localhost", port=6333)`: Conecta em um container Docker real (produção).
*   `QdrantClient(url="...", api_key="...")`: Conecta no Qdrant Cloud (seguro/gerenciado).

### 2. `models.VectorParams` vs `SparseVectorParams`
Definem a "física" do seu universo vetorial.
*   `size`: **CRÍTICO**. Deve ser igual ao modelo de embedding (ex: OpenAI `text-embedding-3-small` = **1536**). Se errar, o banco rejeita inserções.
*   `distance`:
    *   `Distance.COSINE`: Padrão para NLP/Textos. Mede o ângulo (direção).
    *   `Distance.DOT`: Produto escalar. Se os vetores forem normalizados, é igual ao Cosine mas mais rápido.
    *   `Distance.EUCLID`: Distância "física" em linha reta. Raro para textos, comum para imagens/geo.

### 3. `models.PointStruct`
A unidade atômica de dado (como uma "linha" no SQL).
*   `id`: Pode ser Inteiro (`1, 2`) ou UUID (`"a1b2..."`). **É chave primária**. Se repetir, **sobrescreve**.
*   `vector`: A lista de floats ou dicionário de vetores (para hybrid search).
*   `payload`: JSON arbitrário (`dict`). Schemaless!
    *   *Dica:* Use nomes consistentes (`snake_case`) para facilitar filtros depois.

### 4. `models.Filter`
A engine de query booleana.
*   `must` (**AND**): A condição PRECISA ser verdadeira. Ex: `status="active"`.
*   `must_not` (**NOT**): A condição NÃO pode ser verdadeira. Ex: `deleted=true`.
*   `should` (**OR / Boost**):
    *   Em **Filtros** (`query_filter`): Funciona como OR ("pelo menos um deve dar match").
    *   Em **Score** (search params): Funciona como "Boost" (se tiver, aumenta o score, mas não é obrigatório).

### 5. `client.query_points(...)`
A API moderna ("Universal Query") que substitui `search()` e `recommend()`.
*   `query`: O vetor de busca.
*   `query_filter`: Onde você passa o objeto `models.Filter`.
*   `limit`: Top K (quantos vizinhos retornar).
*   `with_payload`:
    *   `True`: Retorna o JSON completo (mais lento/pesado).
    *   `False`: Retorna só ID e Score (super rápido).
    *   `['campo1', 'campo2']`: Projection (retorna só campos específicos).

---

## 🚦 Como Rodar

1.  **Instale o cliente:**
    ```bash
    pip install qdrant-client
    ```

2.  **Rode (exemplo):**
    ```bash
    python 01-fundamentals/05-databases/04_search.py
    ```
    *(Todos os scripts conectam em `:memory:` ou `localhost` e são auto-contidos).*

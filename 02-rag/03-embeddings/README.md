# 🔢 Módulo 3: Embeddings

> **Objetivo:** Transformar texto em números (Coordenadas Semânticas).  
> **Status:** A fundação da Busca Semântica e do RAG.

## 📚 Conteúdo Prático (Scripts)

Nesta pasta, criamos 5 scripts para você entender embeddings do zero:

| Arquivo                             | O que você vai aprender?                                  |
|:------------------------------------|:----------------------------------------------------------|
| **`01_concept_vectors.py`**         | A matemática básica. O que é um vetor? Como calcular distâncias? |
| **`02_openai_embeddings.py`**       | Como gerar vetores usando a API da OpenAI (padrão de mercado). |
| **`03_local_embeddings.py`**        | Como gerar vetores **de graça** e localmente com Open Source.   |
| **`04_semantic_search_demo.py`**    | **A Mágica do RAG!** Criando um mini-buscador semântico.       |
---

## 🚀 Como Executar

### 1. Instalar Dependências
Certifique-se de que você tem o Python instalado e rode:
```bash
pip install -r requirements.txt
```

### 2. Configurar OpenAI (Opcional para scripts locais)
Para rodar o script `02`, você precisa de uma chave API da OpenAI no arquivo `.env`:
```env
OPENAI_API_KEY=sk-...
```

### 3. Rodar os Scripts
Basta executar com python:
```bash
python 01_concept_vectors.py
python 04_semantic_search_demo.py
# etc...
```

---

## 🧠 Teoria Resumida (O que você precisa saber)

### 1. O Problema: Computadores são Ruíns com Texto
Computadores não entendem palavras, apenas números.
- Antigamente, usávamos IDs (Cachorro=1, Lobo=2, Banana=3).
- **O defeito:** Matematicamente, 2 (Lobo) não é "mais próximo" de 1 (Cachorro) do que 3 (Banana). Perdemos o significado.

### 2. A Solução: Vetores de Características (Embeddings)
Em vez de um número, usamos uma **lista de números**. Cada número representa uma característica (ou **Dimensão**).
Imagine um gráfico "Fofura vs Tamanho":
- 🐶 Cachorro: `[0.9, 0.4]` (Muito fofo, pequeno)
- 🐺 Lobo:     `[0.1, 0.5]` (Pouco fofo, médio)
- 🍌 Banana:   `[0.0, 0.1]` (Nada fofo, pequeno)

Agora, matematicamente, o Lobo está perto do Cachorro!

### 3. O que são Dimensões?
Nos exemplos didáticos, usamos 2 ou 3 dimensões.
Na vida real, modelos como o da OpenAI usam **1536 dimensões**.
- Cada dimensão captura uma nuance sutil da linguagem (gênero, pluralidade, sentimento, contexto, etc).
- **Mais Dimensões** = Mais inteligência e nuance.
- **Menos Dimensões** = Mais rápido e barato.

### 4. Como eles são calculados?
Ninguém escreve esses números à mão. Eles são **Treinados** por Redes Neurais.
A IA lê a internet inteira tentando adivinhar a próxima palavra.
- *"O gato subiu no..."* (Telhado? Árvore? Batata?)
- Se ela acerta, ela ajusta os números.
- No final, palavras usadas em contextos parecidos acabam tendo números parecidos.

---

### 5. Escolha do Modelo (Guia Rápido 2025)

| Modelo | Provedor | Dims | Pros | Contras |
|:---|:---|:---|:---|:---|
| **text-embedding-3-small** | OpenAI | 1536 | Barato, rápido, padrão. | Privacidade, Custo em escala. |
| **text-embedding-3-large** | OpenAI | 3072 | Maior acurácia. | 2x custo, 2x tamanho de storage. |
| **bge-m3 / multilingual-e5** | Open Source | 1024 | Grátis, roda local, bate a OpenAI. | Você precisa hospedar (GPU necessária). |

---

## ⏭️ Próximo Passo
Agora que você entendeu que embeddings são apenas **coordenadas de significado instruídas por leitura massiva**, onde guardamos esses milhões de vetores?

Vá para **[Módulo 4: Vector Databases](../04-vector-dbs)**.

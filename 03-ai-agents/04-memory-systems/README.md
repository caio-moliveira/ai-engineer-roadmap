# 🧠 Módulo 4: Sistemas de Memória (LangGraph)

Este módulo é um guia técnico e prático sobre como implementar sistemas de memória avançados utilizando o ecossistema **LangGraph** e **LangChain**.

Diferente de sistemas básicos de chat, aqui exploramos a separação entre memória de curto prazo (conversacional) e memória de longo prazo (conhecimento persistente do usuário).

---

## 📂 Visão Geral dos Scripts

Os arquivos abaixo foram desenvolvidos de forma modular e didática. Cada um pode ser executado individualmente para demonstrar um conceito específico.

### 1. Memória de Curto Prazo (`short_term.py`)
Focada em **Checkpoints** e **Threads**. É a memória que permite ao agente lembrar o que foi dito na interação anterior dentro da mesma conversa.
- **Conceito Chave**: `thread_id`.
- **Implementação**: Usa `MemorySaver` para persistência em memória durante o desenvolvimento.
- **Como rodar**: `uv run short_term.py`

### 2. Memória de Longo Prazo (`long_term.py`)
Demonstra o uso de **Stores** do LangGraph para persistir informações que transcendem uma única "sessão" ou "thread".
- **Conceito Chave**: `Store`, namespaces (ex: `("memories", user_id)`).
- **Uso**: Salvar preferências, fatos aprendidos e perfil do usuário.
- **Como rodar**: `uv run long_term.py`

### 3. Persistência com PostgreSQL (`postgres_memory.py`)
Guia de configuração para levar a memória de curto e longo prazo para produção usando um banco de dados relacional.
- **Componentes**: `PostgresSaver` (Checkpoints) e `PostgresStore` (Long-term).
- **Setup**: Requer uma instância de Postgres (ex: via Docker).
- **Como rodar**: `uv run postgres_memory.py`

### 4. Persistência com Redis (`redis_memory.py`)
Focado em alta performance para checkpoints de curto prazo.
- **Componente**: `RedisSaver`.
- **Vantagem**: Baixíssima latência para recuperação de estado em sistemas de alta escala.
- **Como rodar**: `uv run redis_memory.py`

### 5. Busca Semântica em Memória (`semantic_memory.py`)
Implementa o conceito de **Memory-RAG**. Em vez de buscar por palavras exatas, o agente busca memórias por relevância semântica (vetorial).
- **Funcionamento**: Utiliza o método `asearch` do Store com suporte a embeddings.
- **Como rodar**: `uv run semantic_memory.py`

---

## 🛠️ Requisitos Técnicos

- **Python 3.11+**
- **Variáveis de Ambiente**:
  - `OPENAI_API_KEY`: Necessária para os demos com LLM.
  - `POSTGRES_URL` (opcional): Para rodar o demo de Postgres.
  - `REDIS_URL` (opcional): Para rodar o demo de Redis.

## 🎓 Conceitos Fundamentais

> [!IMPORTANT]
> **Checkpoints (Short-Term)**: São automáticos. O LangGraph salva o snapshot de todo o estado toda vez que o grafo avança. É vinculado a um `thread_id`.

> [!TIP]
> **Store (Long-Term)**: É manual e explícito. Você decide o que vale a pena "aprender" e salvar para o futuro do usuário, independente de qual thread ele está usando.

---

## ⏭️ Próximo Passo
Com memórias funcionais, seus agentes agora têm "passado". O próximo passo é dar a eles a capacidade de agir no mundo real.
Vá para **[Módulo 5: Tools & MCP](../05-tools-mcp)**.

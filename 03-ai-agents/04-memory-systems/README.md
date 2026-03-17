# 🧠 Módulo 4: Sistemas de Memória (LangGraph)

Este módulo explora a implementação de sistemas de memória avançados no **LangGraph**, dividindo-os em memória de curto prazo (thread-specific) e memória de longo prazo (conhecimento persistente).

---

## 📂 Visão Geral dos Scripts

O módulo foi simplificado para focar em três pilares fundamentais da memória:

### 1. Memória de Curto Prazo (`short_term.py`)
Focada em **Checkpoints** e **Threads**. Permite que o agente mantenha o contexto de uma conversa específica.
- **Conceito Chave**: `thread_id`.
- **Implementação**: Uso de `MemorySaver` para persistência efêmera em memória.

### 2. Memória de Longo Prazo (`long_term.py`)
Utiliza o conceito de **Store** do LangGraph para persistir informações que transcendem uma única sessão (ex: preferências do usuário).
- **Conceito Chave**: `Store`, namespaces.
- **Uso**: Salvar fatos aprendidos sobre o usuário.

### 3. Persistência Externa (`persisted_memory.py`)
Demonstra como conectar seu agente a bancos de dados robustos para produção, utilizando **Redis** e **PostgreSQL**.
- **Redis**: Ideal para alta performance em checkpoints de curto prazo.
- **PostgreSQL**: Excelente para persistência relacional de longo prazo e estados complexos.

---

## 🛠️ Infraestrutura e Setup

Para utilizar persistência externa, você precisará configurar os seguintes serviços:

### 🚀 Redis (Docker)
Recomendamos o uso do `redis-stack-server` para ter acesso completo às funcionalidades.
- **Imagem**: `redis/redis-stack-server:latest`
- **Porta Padrão**: `6379`
- **URL de Conexão**: `redis://localhost:6379`
- **Docker Command**:
  ```bash
  docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack-server:latest
  ```

### 🐘 PostgreSQL (Supabase)
Para o Postgres, utilizamos o **Supabase** como provedor Cloud.
1. Crie um projeto no [Supabase](https://supabase.com/).
2. Obtenha a **Connection String** nas configurações de Database.
3. Com a URL em mãos, o LangGraph consegue criar as tabelas necessárias automaticamente.

---

## 📦 Dependências e Imports

Para utilizar esses provedores, você deve instalar os pacotes específicos via **uv**:

```bash
# Para Redis
uv add langgraph-checkpoint-redis

# Para PostgreSQL
uv add langgraph-checkpoint-postgres
```

### Imports Necessários
No seu código Python, utilize os seguintes imports para os Savers:

```python
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.postgres import PostgresSaver
```

---

## 🔗 Documentação Útil

- [LangGraph Persistence Documentation](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [Redis Stack Image - Docker Hub](https://hub.docker.com/r/redis/redis-stack-server)
- [Supabase Database Docs](https://supabase.com/docs/guides/database)
- [LangGraph Redis Saver Guide](https://langchain-ai.github.io/langgraph/how-tos/persistence_redis/)

---

## 🎓 Conceitos Fundamentais

> [!IMPORTANT]
> **Checkpoints (Short-Term)**: São automáticos e vinculados a um `thread_id`. Capturam o estado completo do grafo.
> **Store (Long-Term)**: É uma escrita explícita (`store.put`) para persistir conhecimentos gerais do usuário entre diferentes threads.

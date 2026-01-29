# 🚢 Módulo 09: Deploy, Infra e Produção

> **Goal:** Ensinar como colocar uma API de IA em produção de forma profissional, previsível e sustentável.
>
> Este módulo é escrito no formato de **documentação técnica**, não como checklist conceitual.
> O foco é **deploy de backend de IA** — APIs que executam agentes, RAGs e workflows com LLMs.

---

## 🧠 Introdução — O que significa "deploy" em sistemas de IA

Em aplicações tradicionais, deploy significa:

* subir um backend
* expor endpoints
* escalar requisições

Em sistemas de IA, deploy significa algo muito mais complexo:

* garantir reprodutibilidade do ambiente
* controlar dependências pesadas
* proteger chaves sensíveis
* evitar custo descontrolado
* garantir comportamento consistente

Uma API de IA não pode:

* inicializar coisas no meio da request
* depender de estado local
* carregar modelos de forma preguiçosa

Tudo deve estar **deterministicamente pronto no startup do container**.

---

## 📦 Arquitetura base de uma API de IA

Antes de falar de Docker, é importante entender o que estamos empacotando.

Uma API de IA típica possui:

```
app/
 ├── main.py            # FastAPI entrypoint
 ├── api/               # rotas HTTP
 ├── core/              # configurações e settings
 ├── llm/               # clients de modelos
 ├── rag/               # pipelines de retrieval
 ├── agents/            # fluxos agentic
 ├── observability/     # tracing, logs
 └── services/          # regras de negócio
```

O Docker não resolve arquitetura ruim.
Ele apenas empacota.

---

# 1️⃣ Docker — por que ele é obrigatório em IA

Docker garante que:

* o mesmo código rode igual em qualquer ambiente
* as mesmas versões de libs sejam usadas
* o runtime do modelo seja previsível

Sem Docker, o comportamento do LLM pode variar apenas por diferença de dependências.

---

## 1.1 Diferença prática: Web API vs API de IA

| Aspecto      | Web comum  | IA         |
| ------------ | ---------- | ---------- |
| Dependências | leves      | pesadas    |
| Startup      | rápido     | mais lento |
| Memória      | baixa      | alta       |
| Custo        | previsível | variável   |

Isso muda completamente o Dockerfile.

---

# 2️⃣ Dockerfile explicado linha por linha

A seguir está um **Dockerfile realista para uma API FastAPI de IA**.

```dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copiar apenas dependências primeiro
COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv pip install --system

# agora copia o código
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Por que essa ordem importa?

Docker cria camadas.

Se você copiar o código antes das dependências:

* qualquer alteração invalida o cache
* tudo é reinstalado

Separando dependências:

* mudanças de código não reinstalam libs
* build fica muito mais rápido

---

# 3️⃣ Multistage build (quando necessário)

Em projetos de IA mais pesados (torch, sentence-transformers, vLLM), usamos multistage build.

Exemplo conceitual:

```dockerfile
FROM python:3.11 AS builder
WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv pip install --system

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

O estágio final fica muito menor.

---

# 4️⃣ Variáveis de ambiente (configuração correta)

Nada sensível pode existir no código.

Nunca:

```python
OPENAI_API_KEY = "sk-xxxx"
```

Tudo deve vir do ambiente.

---

## 4.1 Pydantic Settings (fail fast)

Exemplo real:

```python
class Settings(BaseSettings):
    openai_api_key: str
    environment: str

    class Config:
        env_file = ".env"
```

Se a variável não existir:

* a aplicação falha no startup
* o container não sobe

Isso evita falhas silenciosas.

---

# 5️⃣ Startup lifecycle da API

Uma API de IA deve inicializar tudo no startup:

```python
@app.on_event("startup")
async def startup():
    load_llm_clients()
    connect_vector_db()
    warmup_embeddings()
```

Nada crítico deve ser criado durante uma request.

Requests devem apenas:

* executar lógica
* usar recursos já prontos

---

# 6️⃣ Streaming de resposta (SSE)

LLMs são lentos.

Se você esperar o modelo terminar para responder:

* o usuário acha que travou

Com streaming:

```python
return EventSourceResponse(generator())
```

O usuário começa a ver tokens imediatamente.

Isso melhora drasticamente a experiência.

---

# 7️⃣ Proteção de custo

Sem proteção, uma única rota pode gerar milhares de tokens.

Boas práticas:

* limitar tamanho do prompt
* limitar histórico
* timeout por request
* rate limiting

Isso não é otimização.
É sobrevivência financeira.

---

# 8️⃣ Deploy mental model

Deploy não é o final.

É o início da vida do sistema.

Depois do deploy vêm:

* métricas
* tracing
* avaliação
* otimização

Por isso este módulo se conecta diretamente com observabilidade.

---

# 🏁 Conclusão

Colocar IA em produção exige:

* disciplina de engenharia
* arquitetura limpa
* containers bem construídos
* controle de ambiente

Não existe sistema de IA confiável sem deploy profissional.

---

⏭️ **Próxima Etapa:** Construir um sistema RAG real, do zero.
Nos vemos no **Bloco 2: Sistemas RAG**.

# ⚡ FastAPI para Engenheiros de IA: O Backbone da Produção

> **Mantra:** "O modelo é apenas uma função. A API é o produto."
> **Docs Oficiais:** [FastAPI](https://fastapi.tiangolo.com/) | [Pydantic](https://docs.pydantic.dev/)

Este módulo explica como transformar scripts de IA (que rodam no seu computador) em serviços de API robustos que aguentam tráfego real. Não vamos ensinar como criar um "Hello World", mas sim como arquitetar sistemas de IA.

---

## 1. Arquitetura Async: O Fim do Bloqueio
Em aplicações web normais, uma query de banco leva 10ms. Em IA, uma geração de texto pode levar 30 segundos.
Se você usar frameworks síncronos (Flask, Django padrão), **uma** requisição bloqueia o servidor inteiro.

### O Padrão AsyncIO
FastAPI permite que enquanto o servidor espera a resposta da OpenAI (I/O Bound), ele processe outras 10.000 requisições.

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.post("/generate")
async def generate_text(prompt: str):
    # O 'await' libera o processador para fazer outras coisas
    # enquanto a resposta não chega.
    response = await openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"content": response.choices[0].message.content}
```

---

## 2. Streaming de Tokens (Server-Sent Events)
Ninguém quer esperar 20 segundos para ver o texto aparecer de uma vez. A UX moderna de IA exige que o texto apareça "digitado" em tempo real.
Usamos **SSE (Server-Sent Events)** para isso.

> **Conceito:** O servidor mantém a conexão aberta e "empurra" pedaços (chunks) de texto assim que eles são gerados pelo LLM.

```python
from fastapi.responses import StreamingResponse

async def stream_generator(prompt: str):
    stream = await openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True  # Importante!
    )
    for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        yield token  # Yield "entrega" o pedaço imediatamente

@app.post("/chat/stream")
async def stream_chat(prompt: str):
    return StreamingResponse(stream_generator(prompt), media_type="text/event-stream")
```
*Docs:* [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

---

## 3. Background Tasks & Workflows
RAG Ingestion (ler 100 PDFs e vetorizar) é lento. O usuário não pode ficar esperando o loading girar por 5 minutos.
Para processos longos, devolvemos um "202 Accepted" imediatamente e rodamos o processo em background.

### Abordagem Simples (BackgroundTasks)
Para tarefas leves que podem ser perdidas se o servidor reiniciar.

```python
from fastapi import BackgroundTasks

def index_document(doc_id: str):
    # Lógica pesada: Ler PDF -> Chunk -> Embed -> Salvar no VectorDB
    vector_db.upsert(doc_id)

@app.post("/ingest/{doc_id}")
async def start_ingestion(doc_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(index_document, doc_id)
    return {"status": "Processing started", "doc_id": doc_id}
```
*Docs:* [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

## 4. Injeção de Dependências (O Coração da Engenharia)
Sistemas de IA têm muitos "clientes": Cliente OpenAI, Cliente VectorDB, Cliente Logger.
Não instancie eles globalmente. Use `Depends`. Isso permite trocar o VectorDB real por um Mock durante os testes.

```python
from fastapi import Depends
from qdrant_client import QdrantClient

# Dependency Provider
def get_vector_db():
    client = QdrantClient(url="http://localhost:6333")
    try:
        yield client
    finally:
        client.close()

@app.post("/search")
async def search_docs(query: str, db: QdrantClient = Depends(get_vector_db)):
    # db é injetado automaticamente e fechado no final
    results = db.search(collection_name="docs", query_vector=...)
    return results
```
*Docs:* [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

## 5. Lifespan Events (Startup & Shutdown)
Onde você carrega modelos pesados ou ML em memória. Você não quer carregar um modelo de 5GB na memória a cada requisição. Você carrega **uma vez** na inicialização.

```python
from contextlib import asynccontextmanager

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load resources
    ml_models["bert"] = load_heavy_model()
    print("Modelo carregado!")
    yield
    # Clean up resources
    ml_models.clear()

app = FastAPI(lifespan=lifespan)
```
*Docs:* [FastAPI Lifespan](https://fastapi.tiangolo.com/advanced/events/)

---

## ⏭️ Próximo Passo
A API está pronta, mas o dado de entrada é seguro?
Vamos garantir contratos com **[Módulo 04: Modelagem e Contratos de Dados](../04-data-modeling)**.

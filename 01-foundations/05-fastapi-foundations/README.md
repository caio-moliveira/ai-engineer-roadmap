# ⚡ Module 5: FastAPI Foundations

> **Goal:** Build High-Performance AI APIs.  
> **Status:** The Industry Standard.

## 1. Why FastAPI?
It is the standard for AI/ML for a reason:
1.  **Async Native:** Built on `Starlette`. Handles high concurrency for LLM apps.
2.  **Pydantic Native:** Validation is first-class, not an afterthought.
3.  **Auto-Docs:** Swagger UI (`/docs`) is generated automatically.

## 2. A Basic Skeleton (Production Style)
We don't do "single file APIs". We use Routers.

```python
# main.py
from fastapi import FastAPI
from app.routers import chat, ingestion

app = FastAPI(title="Pro AI Agent", version="1.0.0")

app.include_router(chat.router)
app.include_router(ingestion.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

## 3. Dependency Injection (The Secret Weapon)
Stop using global variables for your Database or OpenAI Client.
Use `Depends()`. This makes testing easy.

```python
from fastapi import Depends

def get_db():
    db = QdrantClient()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(msg: str, db = Depends(get_db)):
    # db is injected automatically
    return db.search(msg)
```

## 4. Background Tasks
Don't make the user wait for long operations (like updating vector indexes).

```python
from fastapi import BackgroundTasks

async def index_document(doc_id: str):
    # Takes 30 seconds
    ...

@app.post("/upload")
async def upload(file: UploadFile, bg_tasks: BackgroundTasks):
    # Create ID
    doc_id = "123"
    # Schedule task, run AFTER response is sent
    bg_tasks.add_task(index_document, doc_id)
    return {"status": "processing", "id": doc_id}
```

## 5. Streaming Responses (SSE)
The standard way to stream LLM tokens to a frontend (React/Next.js).

```python
from fastapi.responses import StreamingResponse

@app.post("/generate")
async def generate_stream():
    return StreamingResponse(
        content=stream_gpt_generator(), 
        media_type="text/event-stream"
    )
```

## 🧠 Mental Model: "Statelessness"
Your API should be **Stateless**.
- Don't save user conversation history in a global Python variable/list.
- If the server restarts, history is lost.
- **Solution:** Save state in Redis or Postgres. Pass a `session_id` to the API.

## ⚠️ Common Mistakes
- **Blocking the Event Loop:** Running CPU-heavy code (like image resizing or pandas crunching) inside an `async def`. It blocks the *entire* server.
    - **Fix:** Use `def` (FastAPI runs it in a threadpool) or use `Celery`/`Arq` workers.
- **No Lifespan:** Not closing DB connections on shutdown. Use `@asynccontextmanager`.

## ⏭️ Next Step
Let's learn how to validate data strictly.
Go to **[Module 6: Pydantic v2](../06-pydantic-v2)**.

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from database import init_db
from frontend import router as frontend_router
from router import router as receipts_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Receipt OCR API",
    description="Processa imagens de recibos via GLM-OCR + GPT-4.1-mini e persiste em SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(receipts_router)
app.include_router(frontend_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

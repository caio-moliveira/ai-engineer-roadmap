from fastapi import FastAPI
from router import router

app = FastAPI(
    title="AI API - Fundamentals",
    description="API demonstrando integração com OpenAI e LangChain"
)

app.include_router(router)
    
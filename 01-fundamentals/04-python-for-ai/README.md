# 🐍 Módulo 4: Python para Engenheiros de IA

> **Goal:** Escrever código que não trava quando a OpenAI demora 30s para responder.  
> **Status:** O fim do código bloqueante.

## 1. Async/Await (Obrigatório)
LLMs são I/O Bound. Eles demoram.
Se você usar `requests.post()` em um endpoint do FastAPI, você trava o servidor inteiro para todos os usuários.
**Use `httpx` e `asyncio`.**

```python
# Errado (Bloqueante)
import requests
def chat():
    return requests.post("...") # Servidor parado por 10s

# Certo (Assíncrono)
import httpx
async def chat():
    async with httpx.AsyncClient() as client:
        return await client.post("...") # Servidor livre para outros requests
```

## 2. Generators & Streaming
Ninguém gosta de esperar. Streaming reduz a latência percebida a zero.
Aprenda a usar `yield` para retornar tokens assim que eles chegam.

```python
async def stream_tokens():
    async for chunk in client.stream(...):
        yield chunk
```

## 3. Decorators para Resiliência (`tenacity`)
APIs falham. Rate limits acontecem.
Não escreva loops `while True` manuais. Use decoradores.

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, max=60), stop=stop_after_attempt(5))
async def call_openai():
    ...
```

## 🧠 Mental Model: "Sistemas Reativos"
Seu código Python não é mais um script linear. É um orquestrador de eventos que reage a inputs externos (usuário, APIs, Banco) de forma não-bloqueante.

## ⏭️ Próximo Passo
Onde rodamos esse Python?
Vá para **[Módulo 5: FastAPI Foundations](../05-fastapi)**.

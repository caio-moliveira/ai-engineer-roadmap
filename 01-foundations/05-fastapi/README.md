# ⚡ Módulo 5: FastAPI Foundations

> **Goal:** Construir a interface do seu cérebro de IA.  
> **Status:** O framework padrão do mercado.

## 1. Por que FastAPI?
Flask e Django são ótimos, mas FastAPI foi desenhado para a era moderna:
- **Async Nativo:** Perfeito para LLMs.
- **Pydantic Integrado:** Validação de dados automática (essencial para JSONs de LLMs).
- **Swagger Auto-gerado:** Documentação instantânea.

## 2. Dependency Injection (DI)
O "pulo do gato" do FastAPI.
Não crie conexões globais com o Banco ou OpenAI. Injete-as.
Isso facilita testes (mocking) e gerenciamento de recursos.

```python
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(msg: str, db: Session = Depends(get_db)):
    ...
```

## 3. Background Tasks
O usuário não precisa esperar você salvar o chat no banco.
Retorne a resposta do LLM e salve no banco em background.

```python
@app.post("/chat")
async def chat(msg: str, background_tasks: BackgroundTasks):
    response = await llm.generate(msg)
    background_tasks.add_task(save_to_db, msg, response)
    return response
```

## 🧠 Mental Model: "O Porteiro Eficiente"
O FastAPI é o porteiro do seu prédio. Ele recebe o pacote, valida se é pra você, te entrega e já atende o próximo. Ele não entra no elevador com você (bloqueio).

## ⏭️ Próximo Passo
Como garantimos que os dados estão certos?
Vá para **[Módulo 6: Pydantic v2](../06-pydantic-v2)**.

# FastAPI para Aplicações de IA

## O que é FastAPI?

[FastAPI](https://fastapi.tiangolo.com/) é um framework web moderno e de alto desempenho para construir APIs com Python. Para aplicativos de IA, ele serve como a interface entre seus modelos de IA e o mundo exterior, permitindo que sistemas externos enviem dados para seus modelos e recebam previsões ou resultados de processamento. O que torna o FastAPI particularmente atraente é sua simplicidade e elegância - ele fornece tudo o que você precisa sem complexidade desnecessária.



### Por que FastAPI para Engenharia de IA?

1. **Desempenho**: Construído sobre Starlette e Pydantic, o FastAPI é rápido e simplesmente funciona.
2. **Documentação Automática**: O FastAPI gera automaticamente documentação interativa da API (via Swagger UI e ReDoc) a partir do seu código e anotações de tipo, facilitando a colaboração entre equipes.
3. **Segurança de Tipos**: Aproveitando o Pydantic, o FastAPI fornece validação automática de requisições e mensagens de erro claras, reduzindo a probabilidade de erros em tempo de execução.
4. **Suporte Assíncrono**: O suporte nativo para padrões async/await permite que sua API lide com múltiplas requisições de forma eficiente enquanto espera pelas respostas do modelo de IA.
5. **Suporte a WebSocket**: Para respostas de IA em streaming ou construção de aplicações em tempo real, o FastAPI oferece suporte de primeira classe a WebSocket.

## Saiba Mais

Além deste README, [este tutorial](https://fastapi.tiangolo.com/tutorial/) mostra como usar o FastAPI com a maioria de seus recursos, passo a passo.

## Início Rápido

1.  **Instale as dependências**:
    ```bash
    uv sync
    ```

2.  **Execute a aplicação**:
    Execute o seguinte comando na raiz do repositório:
    ```bash
    uv run uvicorn main:app --app-dir 01-fundamentals/03-fastapi --reload
    ```

3.  **Acesse sua API**:
    -   Endpoints da API: http://localhost:8000/docs
    -   Docs Interativos: http://localhost:8000/docs

### Sobre o Uvicorn

O Uvicorn é um servidor ASGI que realmente executa sua aplicação FastAPI. Enquanto o FastAPI define a estrutura e a lógica da sua API, o Uvicorn é o servidor que lida com conexões HTTP e serve sua aplicação.

Pense no FastAPI como a planta da sua API, e no Uvicorn como o motor que a impulsiona.

O comando `uvicorn main:app --app-dir 01-fundamentals/03-fastapi --reload` significa:
-   `main`: Use o arquivo chamado `main.py`
-   `:app`: Procure por uma variável chamada `app` dentro desse arquivo
-   `--app-dir 01-fundamentals/03-fastapi`: Diz ao Uvicorn onde procurar o arquivo da aplicação, permitindo que ele lide com importações corretamente a partir da raiz.
-   `--reload`: Reinicia automaticamente o servidor quando você altera seu código (útil durante o desenvolvimento)

### Porta Padrão

Por padrão, o Uvicorn roda na porta 8000. Isso significa:
-   Sua API estará acessível em `http://localhost:8000`
-   `localhost` refere-se ao seu próprio computador
-   `8000` é a "porta" ou número da porta pela qual as requisições podem acessar sua API

Você pode alterar isso com a flag `--port` se necessário:
```bash
uvicorn main:app --app-dir 01-fundamentals/03-fastapi --port 5000
```

## Estrutura

Organizamos a aplicação em arquivos modulares:

-   `main.py`: Ponto de entrada da aplicação que cria o app FastAPI.
-   `router.py`: Roteia as requisições recebidas para os manipuladores de endpoint apropriados.
-   `endpoint.py`: Contém a lógica central para as integrações de IA (OpenAI, LangChain).
-   `models.py`: Define modelos de dados Pydantic para validação de requisições.

Essa abordagem modular mantém seu código organizado à medida que sua aplicação de IA cresce em complexidade.

> Para documentação completa, visite a [documentação oficial do FastAPI](https://fastapi.tiangolo.com/).

## Passo a Passo do Código

Vamos examinar como nossos arquivos funcionam juntos para criar uma API limpa para processamento de eventos de IA.

### 1. `main.py` - Ponto de Entrada da Aplicação

```python
from fastapi import FastAPI
from router import router

app = FastAPI(
    title="AI API - Fundamentals",
    description="API demonstrando integração com OpenAI e LangChain"
)

app.include_router(router)
```

Este arquivo:
-   Cria a instância principal da aplicação `FastAPI`.
-   Importa e inclui nosso `router` principal.
-   Serve como ponto de entrada para o Uvicorn.

### 2. `router.py` - Roteamento de Requisições

```python
from fastapi import APIRouter
from endpoint import generate_text_openai
from models import GenerateRequest

router = APIRouter()

@router.post("/openai")
async def endpoint_openai(request: GenerateRequest):
    # Chama a função de lógica
    result = await generate_text_openai(request.prompt)
    return {"response": result}
```

Este arquivo:
-   Cria um `APIRouter`.
-   Define endpoints (ex: `/openai`).
-   Conecta a requisição HTTP à lógica em `endpoint.py`.

### 3. `endpoint.py` - Lógica Central

```python
import os
from openai import AsyncOpenAI

async def generate_text_openai(prompt: str) -> str:
    """
    Integração direta com SDK da OpenAI (Async).
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # ... chama a API ...
    return response.choices[0].message.content
```

Este arquivo:
-   Contém a "lógica de negócios" ou "lógica de IA".
-   Interage diretamente com serviços externos como OpenAI.
-   Mantém o roteador limpo de detalhes de implementação.

### 4. `models.py` - Validação de Dados

```python
from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str
    topic: Optional[str] = None
```

Este arquivo:
-   Define a estrutura dos dados esperados usando Pydantic.
-   Garante que as requisições tenham os campos necessários (como `prompt`).

## Endpoints Síncronos vs. Assíncronos no FastAPI

O FastAPI suporta manipuladores de requisição síncronos e assíncronos.

### Endpoints Síncronos

Endpoints síncronos usam funções Python padrão e bloqueiam o servidor durante o processamento:

```python
@router.post("/sync")
def sync_endpoint(data: EventSchema):
    # Isso bloqueia o servidor até a conclusão
    result = process_data(data)
    return {"result": result}
```

**Quando usar:** Para operações rápidas que concluem rapidamente (menos de 1 segundo).

### Endpoints Assíncronos

Endpoints assíncronos usam a sintaxe `async`/`await` do Python e não bloqueiam o servidor:

```python
@router.post("/async")
async def async_endpoint(data: EventSchema):
    # Isso não bloqueia o servidor
    result = await async_process_data(data)
    return {"result": result}
```

**Quando usar:** Para operações que:
-   Envolvem operações de E/S (chamadas de API, consultas ao banco de dados)
-   Levam mais tempo para processar (inferência de IA complexa)
-   Precisam lidar com muitas requisições simultâneas

**Em nosso módulo:** Usamos definições `async` porque estamos chamando APIs externas (OpenAI) que são limitadas por E/S (I/O bound).

## Entendendo Métodos de API: GET vs POST

Se você é novo em APIs, pense na diferença entre GET e POST como similar à diferença entre ler e escrever.

-   **GET (Pedindo Informação)**: Usado para recuperar informações sem alterar nada (ex: verificar status).
-   **POST (Enviando Informação)**: Usado para enviar dados que precisam ser processados. No nosso caso, usamos **POST** para enviar um prompt para o modelo de IA.

## Protegendo seu Endpoint FastAPI com Tokens Bearer

**Nota:** A implementação atual neste módulo é simplificada e não inclui autenticação. No entanto, a segurança é crítica para APIs de IA em produção.

A autenticação com token Bearer é a abordagem recomendada para APIs modernas.

### Implementando Autenticação com Token Bearer (Conceitual)

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
API_TOKEN = "seu-token-secreto"

@router.post("/openai")
def handle_event(
    request: GenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")
    # Prosseguir...
```

Para aplicações em produção, considere usar tokens para controlar o acesso aos seus recursos de IA!

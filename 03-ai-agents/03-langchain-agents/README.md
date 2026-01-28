# 🦜🔗 Módulo 3: LangChain v1 para Agentes

> **Goal:** Tools e Function Calling.  
> **Status:** O mecanismo de interação.

## 1. Tool Calling (Function Calling)
Modelos modernos (GPT-4o, Claude 3.5) foram treinados para retornar JSON estruturado quando solicitados.
LangChain v1 padroniza isso.

### Definindo uma Tool (O jeito certo)
Use Pydantic. Sempre.

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="A query de busca otimizada para SEO")
    year: int = Field(description="O ano para filtrar resultados")

@tool("search_google", args_schema=SearchInput)
def search_google(query: str, year: int):
    """Realiza uma busca no Google."""
    return f"Resultados para {query} em {year}..."
```

## 2. Binding Tools
Você precisa "ensinar" o modelo sobre as ferramentas disponíveis.

```python
tools = [search_google]
llm_with_tools = llm.bind_tools(tools)
```

## 3. Invocação e Parsing
Quando o modelo decide usar uma tool, ele não executa. Ele retorna um **ToolCall**.
Seu código deve:
1. Detectar o `tool_call`.
2. Executar a função Python real.
3. Devolver o resultado para o modelo.

**LangGraph faz isso automaticamente com o `ToolNode`.**

## ⚠️ Erros Comuns
- **Docstrings Ruins:** O modelo lê a docstring da função para saber *quando* usá-la. Seja descritivo.
- **Tools demais:** Não dê 50 tools para o agente. Ele vai se confundir. Mantenha < 10 por agente.
- **Falta de Tipagem:** Se você não tipar os argumentos, o modelo vai alucinar parâmetros.

## 🧠 Mental Model: "A API do Modelo"
Pense no `bind_tools` como se estivesse definindo uma API REST que o modelo pode chamar. A qualidade da sua "Documentação de API" (Schemas e Docstrings) determina o sucesso do cliente (o Modelo).

## ⏭️ Próximo Passo
Como orquestrar esses chamados?
Vá para **[Módulo 4: LangGraph](../04-langgraph-orchestration)**.

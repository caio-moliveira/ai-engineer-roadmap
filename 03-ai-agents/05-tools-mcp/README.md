# 🛠️ Módulo 6: Tools & MCP (Model Context Protocol)

> **Goal:** Dar "Mãos" para seu Agente atuar no mundo externo.  
> **Status:** O padrão ouro (MCP) recém-lançado que substitui integrações dolorosas.

Se no módulo passado demos memórias aos agentes, neste nós os ensinaremos a agir. Agentes sem ferramentas são limitados a conversar; com ferramentas, eles podem formatar HDDs, consultar bancos SQL, navegar em viagens ou enviar e-mails.

Disponibilizamos scripts práticos consolidados na pasta `/python` simulando fluxos backend corporativos com o recém-lançado framework oficial `create_agent` pareado com `MultiServerMCPClient`.

---

## 📚 Índice de Scripts Práticos

Todos os scripts são construídos sobre o core do LangChain e formatados para execução nativa via console.

1. **[Ferramentas Nativas em Python (`@tool`)](#1-ferramentas-nativas-em-python)** -> `python/01_custom_tools.py`
2. **[Contexto de Execução Oculto (Runtime Context)](#2-injeção-de-contexto-no-runtime)** -> `python/02_runtime_context.py`
3. **[MCP: Servidor Local via Subprocessos](#3-mcp-servidor-local-via-stdio)** -> `python/03_mcp_local_server.py`
4. **[MCP: Servidores Globais e APIs REST](#4-mcp-servidores-remotos-e-online-api)** -> `python/04_mcp_remote.py`

---

## 1. Ferramentas Nativas em Python

Ferramentas (Tools) são pedaços de código convencionais com uma "casca" que permite que a LLM saiba exatamente para que servem e **quando chamá-las**. A casca é o decorator `@tool`. Não subestime a docstring (o texto dentro de `"""`), a inteligência do agente depende 100% da clareza dessa explicação.

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def calculadora(x: float, y: float) -> float:
    """Soma dois números. Útil para matemática."""
    return x + y

# Bind das ferramentas ao agente é absurdamente simples
agent = create_agent(model="gpt-4o", tools=[calculadora])
```

---

## 2. Injeção de Contexto no Runtime

Às vezes, uma feramenta precisa de algo "sigiloso" (ID do usuário no Backend, token de sessão, contexto relacional) que a IA nunca vai gerar e você não quer que ela tente deduzir.

Em nossa abstraction do *Langgraph*, nós englobamos parâmetros via `ToolRuntime` e injetamos o `context_schema` que foi montado no server no momento da `invoke()`.

```python
from langchain.tools import tool, ToolRuntime

# A LLM NUNCA precisa adivinhar essa propriedade 'runtime', e a Tool ascessará o contexto!
@tool
def resgatar_saldo(runtime: ToolRuntime) -> str:
    """Busca o saldo do usuário logado"""
    id_backend = runtime.context.user_id 
    # [Busca no SQL por esse ID...]
    return f"O saldo é R$ 1..."

# Agente blindado: Invocado passando a configuração local da sessão!
agent = create_agent(model="gpt-4", tools=[resgatar_saldo], context_schema=UserContext)
agent.invoke(..., context=UserContext(user_id="U-123"))
```

---

## 3. O Fim das Tools Nativas e Nascimento do MCP (Model Context Protocol)

Definir Tools Python manuais numa base monolítica é exaustivo (você precisa re-codar a API do Google Calendar toda vez).
O **MCP (Model Context Protocol)** - iniciativa pioneira open source desenvolvida pela Anthropic, converteu o pareamento de Tools para um conceito *Micro-serviços*.

Servidores MCP publicam Ferramentas, Prompts e Recursos numa linguagem universal. O Agente simplesmente se "conecta" e pergunta `get_tools()`.

### MCP: Servidor Local (via STDIO)
Abordado no script `03_mcp_local_server.py`. O Langchain executa um script Python vizinho como um binário isolado. Toda comunicação JSON bate como input e output standard (`stdio`). Suporta abstrações assíncronas de sub-processos.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

# O Server está atrelado a um binário do Python fora da memoria atual
client = MultiServerMCPClient({
    "database_server": {
        "transport": "stdio",
        "command": "python",
        "args": ["../servidor_sql.py"]
    }
})

tools = await client.get_tools()
```

### 4. MCP: Servidores Remotos e Online API
Abordado no script `04_mcp_remote.py`. 

Se sua VM/SO tiver a package `uvx` ou `npx` instaladas, você engabela as ferramentas oficiais da nuvem sem escrever **nenhuma** `@tool`. Você não programa a lógica da calculadora de voos, você APENAS ASSINA um Server Sent Events via `streamable_http`.

```python
client = MultiServerMCPClient({
    # Assinando serviços MCP remotos HTTPS Restful 
    "travel_server": {
        "transport": "streamable_http",
        "url": "https://mcp.kiwi.com"
    }
})

tools = await client.get_tools()
agent = create_agent(model="gpt-4o", tools=tools)

# O agente consultará a Kiwi remotamente, trará as passagens via MCP e devolverá no prompt!
await agent.ainvoke({"messages": [...]})
```

## 🧠 Mental Model Combinado

Hoje, os Agentes em Produção seguem o tríplice pilar:
1. **Controle e Loop de Atos**: `LangGraph` dita com quem o node fala, e o `interrupt()` provém o aval Humano.
2. **Histórico Vivo**: `checkpointer` (Memórias Sqlite/Postgres/MemorySaver) provêm retenção de diálogos.
3. **Sensores Livres**: Ferramentas empacotadas no padrão micro-serviços `MCP`, não poluindo código core.

## ⏭️ Próximo Passo
Dominados os Agentes Unitários e Ferramentais Atômicos, está na hora de subir na pirâmide da gestão corporativa. Pelo que você viu em `MultiServerMCPClient`, um agente lida com vários MCPs.
Mas o que acontece quando **Agentes** de dezenas de especialidades viram *Ferramentas* uns dos outros?
Vá para **[Módulo 7: Sistemas Multi-Agentes](../06-multi-agents)**.

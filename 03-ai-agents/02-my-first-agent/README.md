# 🦜🔗 Módulo 2: Criando seu primeiro Agente

> **Goal:** Construir seu primeiro Agente de IA com LangChain, focando na inicialização de modelos e chamadas de ferramentas (Tool Calling).  
> **Status:** O mecanismo de interação usando LangChain v0.2/v0.3.

## 1. O que precisamos para construir nosso primeiro AI Agent com LangChain?

LangChain tornou-se o framework padrão (e mais utilizado no mercado por Engenheiros de IA) para a orquestração de Agentes. No módulo de Fundamentos, vimos como criar integrações simples com provedores de API para Grandes Modelos de Linguagem (LLMs). 

Para escalarmos isso na elaboração de "Agentes de IA", a LangChain modernizou a forma de instanciar e dar autonomia para os modelos. Precisaremos essencialmente de dois elementos vitais na nossa arquitetura base:

### 1.1. Inicialização de Modelos com `init_chat_model`
No passado, precisávamos importar classes específicas atreladas a cada provedor (ex: `ChatOpenAI`, `ChatAnthropic`). Hoje, a LangChain permite instanciar qualquer modelo de bate-papo de maneira totalmente agnóstica via método utilitário `init_chat_model`. Isso nos garante flexibilidade arquitetural para trocar de LLM (OpenAI, Anthropic, Google Gemini, Ollama) com apenas uma linha de código, sem alterar as etapas posteriores.
- **Referência:** [LangChain Docs - Chat Models Basic Usage](https://docs.langchain.com/oss/python/langchain/models#basic-usage)

### 1.2. Construção de Agentes com `create_agent` (Agent Constructors)
Existem várias maneiras de construir o motor lógico de um Agente. Uma das formas mais tradicionais e seguras na LangChain é utilizar construtores da família `create_*_agent` (como o consolidado `create_tool_calling_agent`). Essa função encapsula internamente a união do raciocínio e das capacidades de uma forma otimizada. Ela unifica: 
- O **LLM** (instanciado anteriormente).
- O **Prompt** (instruções sistêmicas e contexto de como ele deve se comportar).
- As **Tools** (ferramentas, integrações e ações que fornecemos permissão de uso).
- **Referência:** [LangChain Docs - Agents](https://docs.langchain.com/oss/python/langchain/agents)

Vamos mostrar a aplicação prática desses dois conceitos (modelos dinâmicos e construtores de agentes) no decorrer deste módulo de Agentes de IA, pois são passos essenciais para começarmos a erguer nossas arquiteturas customizadas.

---

## 2. Tool Calling (Function Calling)
Modelos modernos (GPT-4o, Claude 3.5, Gemini 1.5) foram treinados para retornar JSON estruturado quando orientados a interagir e realizar alguma "ação" externa pela infraestrutura.
LangChain padroniza perfeitamente esse vaivém de informações.

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

## 3. Binding Tools
Você precisa "ensinar" o modelo sobre as ferramentas disponíveis, acoplando elas dinamicamente à instância dele.

```python
tools = [search_google]
llm_with_tools = llm.bind_tools(tools)
```

## 4. Invocação e Parsing
Quando o agente decide usar uma tool, ele não executa o código em si na sua máquina local. Ele retorna o comando de **ToolCall**.
Seu código deve cuidar da mecânica:
1. Detectar o `tool_call`.
2. Executar a função Python real.
3. Devolver o resultado retornado observando formato pro modelo continuar seu raciocínio.

**LangGraph faz isso automaticamente debaixo dos panos com o construtor `ToolNode`.**

## 5. Output Estruturado (Response Format)

Em muitos casos, você não quer que o agente responda apenas em texto livre, mas sim em um formato que seu sistema possa processar (como JSON ou um objeto Pydantic). A LangChain facilita isso através do parâmetro `response_format`.

### Exemplo: Agente com Schema Pydantic
Defina o seu contrato de dados e passe-o para o construtor do agente.

```python
from pydantic import BaseModel
from typing import List

class Recipe(BaseModel):
    nome: str
    ingredientes: List[str]
    instrucoes: str

agent = create_agent(
    model="gpt-5-nano",
    system_prompt="Você é um chef pessoal...",
    response_format=Recipe
)
```

## 6. Integração Prática de Tools (Exemplo Real)

Vimos como o agente pode usar ferramentas externas para expandir suas capacidades. No nosso exemplo de `personal_chef.py`, usamos o `TavilySearch` para permitir que o agente busque receitas em tempo real.

### Como a busca funciona no fluxo:
1. **O Usuário pergunta**: "Tenho frango e batata, o que fazer?"
2. **O Agente avalia**: Percebe que precisa de informações externas.
3. **Chamada de Tool**: O Agente invoca o `TavilySearch`.
4. **Raciocínio**: O Agente processa os resultados da busca.
5. **Output Estruturado**: O Agente formata a resposta final de acordo com o `Recipe` schema.

```python
from langchain_tavily import TavilySearch

tavily_search_tool = TavilySearch(max_results=5)

agent = create_agent(
    model="gpt-5-nano",
    tools=[tavily_search_tool],
    system_prompt=system_prompt,
    response_format=Recipe
)
```

## ⚠️ Erros Comuns
- **Instruções Ambíguas:** No `system_prompt`, se você disser "forneça instruções se solicitado", o agente pode retornar campos vazios no seu schema estruturado se a pergunta for genérica. Seja **mandatário** nas instruções do prompt para garantir que os campos do Pydantic sejam sempre preenchidos.
- **Docstrings Ruins:** O modelo lê a docstring (`""""""`) da definição de função para saber *quando* e *pra que* usá-la. Seja extremamente e puramente descritivo ao nomear.
- **Falta de Tipagem:** Se você não tipar os argumentos e validá-los pelo schema, o LLM via regra vai acabar alucinando parâmetros errados.

## 🧠 Mental Model: "A API do Modelo"
Pense no `bind_tools` como se estivesse definindo uma API REST onde o LLM é o cliente e suas tools são os endpoints. A qualidade da sua "Documentação da API" (Schemas e Docstrings) determina diretamente o sucesso e confiabilidade do invocador (o Modelo).

## ⏭️ Próximo Passo
Como orquestramos todas essas chamadas em um fluxo contínuo e tolerante a falhas?
Vá para **[Módulo 3: LangGraph e Orquestração](../03-langgraph-orchestration)**.

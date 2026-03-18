# Módulo 05: Tools & Model Context Protocol (MCP)

Este módulo foca na integração de capacidades externas aos agentes de IA. Nossa trilha evolui desde o uso de ferramentas básicas locais (Tools) até a adoção completa do **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)**.

O MCP é um padrão aberto introduzido pela Anthropic que padroniza como os modelos de IA se conectam a fontes de dados e sistemas externos. Ele fornece uma arquitetura universal (Servidor/Cliente) que elimina a necessidade de integrações sob medida para cada fonte de dados.

---

## 🎯 Objetivo de Aprendizado

Ao longo desta trilha prática baseada no cenário de uma **Agência de Viagens Corporativa**, o aluno irá aprender:
1. Como criar ferramentas (Tools) simples e locais.
2. Como conectar ferramentas a APIs RESTful externas de forma autônoma.
3. A arquitetura de um Servidor MCP e seus 3 blocos construtivos: Tools, Resources e Prompts.
4. Como expor e consumir capacidades ativas via MCP (Tool).
5. Como injetar dados estáticos via MCP para Engenharia de Contexto (Resource).
6. Como padronizar a geração utilizando templates do MCP (Prompt).
7. Como criar um Agente Orquestrador em LangGraph unindo todas essas capacidades de forma sequencial com **Human-in-the-Loop (HITL)**.

---

## 🏗️ Arquitetura e Padrões (Langchain & Langgraph)

Todo o código segue estritamente os padrões mais recentes da [documentação oficial da Langchain](https://python.langchain.com/docs/modules/agents/) e utiliza as versões adaptadoras oficiais (`langchain-mcp-adapters`):

- Criação de agentes utilizando `create_agent` e construtores primários em conjunto com o `ChatPromptTemplate`.
- Orquestração de grafos determinísticos orientada a estado transacional utilizando `langgraph.graph.StateGraph`.
- Inserção de controles interativos para pausar/retomar o fluxo assíncrono para aprovação humana usando a arquitetura de `interrupt`.
- Cliente Universal do MCP (`MultiServerMCPClient`) lidando com subprocessos e sub-roteamento `stdio`.
- Servidores MCP limpos instanciados em Python usando `FastMCP`.

---

## 📂 Estrutura das Aulas (Scripts)

O módulo foi desenhado progressivamente. Cada aula isolada adiciona uma camada ou ensina um pilar do framework antes de amalgamá-los ao final.

### Fundamentos de Tools
- **[`aula01_simple_tool.py`](./aula01_simple_tool.py)**
  - **Cenário:** Cálculo de Orçamento Básico.
  - **Mecânica:** Criação local de uma `@tool` (função encadeada puramente em código Python) e sua exposição para orquestração de um Agente nativo via LLM.

- **[`aula02_api_tool.py`](./aula02_api_tool.py)**
  - **Cenário:** Consulta de Clima (API Open-Meteo) e Curiosidades (API Wikipedia).
  - **Mecânica:** O Agente resolve de forma autônoma parâmetros brutos vindos do humano e realiza o acionamento de múltiplas ferramentas HTTP externas de forma transparente.

### Fundamentos do Protocolo MCP
O MCP divide tecnologicamente o que a IA consome em 3 conceitos que os clientes podem buscar sob demanda:
1. **Prompts:** Geração de mensagens pré-formatadas. O LLM as usa para iniciar fluxos com boas práticas de negócio enclausuradas.
2. **Resources (Recursos):** Entrega de dados estáticos/passivos. O Cliente puxa bytes/textos do MCP antes de sequer conversar com o LLM (Ex: Injeção de políticas no System Prompt).
3. **Tools (Ferramentas):** Funções e ações executáveis. O LLM as descobre dinamicamente e dita ativamente os parâmetros e o momento exato de acioná-las.

- **[`03_mcp_server.py`](./03_mcp_server.py)**
  - **Papel:** O cérebro hospedeiro (Backend) da Agência de Viagens. Ele registra a Política Internacional (`@mcp.resource`), o Prompt Corporativo de Vendas (`@mcp.prompt`) e o Emissor de Itinerário Oficial (`@mcp.tool`). Exposto localmente com dependência mínima.

- **[`04_mcp_as_tool.py`](./04_mcp_as_tool.py)**
  - **Papel:** Cliente consumindo a emissão de roteiro (`create_itinerary`).
  - **Mecânica:** O adaptador lê as ferramentas do MCP (`.get_tools()`) e as converte silenciosamente para classes-filhas amigáveis nativas do Langchain, permitindo chamadas orgânicas do Agente.

- **[`05_mcp_as_resource.py`](./05_mcp_as_resource.py)**
  - **Papel:** Cliente adotando RAG passivo e Engenharia de Contexto ("Dicas de Viagem").
  - **Mecânica:** Demonstra o pilar passivo do protocolo: O cliente solicita bytes cru do Resource (`.get_resources()`) antes do modelo gerar texto, injetando as diretrizes puras como context window primária do LLM.
  
- **[`06_mcp_as_prompt.py`](./06_mcp_as_prompt.py)**
  - **Papel:** Cliente recuperando template pronto (`itinerary_planner`) baseado em custom arguments.
  - **Mecânica:** Comprova o pilar instrucional fechado, solicitando via argumento flexível a mensagem estrita que o LLM deverá acatar sem desvios, centralizando no Servidor MCP todo o controle de qualidade do prompting.

### A Orquestração Mestra
- **[`07_mcp_human_in_the_loop.py`](./07_mcp_human_in_the_loop.py)**
  - **Papel:** Agente Final Completo unindo todas as camadas sob o motor do LangGraph.
  - **O Fluxo Determinístico (DAG):** Em formato de Pipeline e Grafo de Estados (`StateGraph`), ele transita sequencialmente por:
    1. Importar budget de *01* e métricas turísticas de *02*.
    2. Puxar Resouces (política de governança) de *05* no servidor MCP.
    3. Trazer Prompt Corporativo formatado do MCP de *06* e injetar com o LLM.
    4. Validar formato chamando a MCP Tool de *04* sob demanda.
    5. **Aprovação Humana (HITL - Human In The Loop)**: Interrompe a compilação do LangGraph via `interrupt()`, envia a carga ao console para averiguação final do gerente da agência.
    6. Se e somente se o usuário digitar "yes" no console, o checkpoint é liberado, gravando de forma permanente um artefato do mundo real (`roteiro_aprovado.md`).

---

## 🚀 Repositório e Setup

1. Configure e instale seu ambiente com o gerador de projeto padrão (`uv`), garantindo os suportes adaptadores exigidos pela stack:
```bash
uv pip install mcp fastmcp langchain-mcp-adapters langchain-openai langgraph
```

2. As credenciais (`OPENAI_API_KEY`, etc) devem ser expostas conforme .env raiz.

## 💻 Como Executar

O fluxo de aprendizado é individual. Exemplo rodando a orquestração mestra final 07 (que instanciará o Servidor 03 como subprocesso em stdio por baixo dos panos):

```bash
uv run .\03-ai-agents\05-tools-mcp\07_mcp_human_in_the_loop.py
```

---

## 📖 Referências Documentais
* [Introdução Oficial ao Protocolo MCP](https://modelcontextprotocol.io/introduction)
* [FastMCP - Documentação para Ferramentas Livres](https://gofastmcp.com/getting-started/welcome)
* [Langchain MCP Adapters](https://docs.langchain.com/oss/python/langchain/mcp)
* [Langchain Tools](https://docs.langchain.com/oss/python/langchain/tools)
* [LangGraph - Controle de Fluxo Iterativo e Arquitetura HITL](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)

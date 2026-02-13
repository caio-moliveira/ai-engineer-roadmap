# 🔹 Bloco 3: Agentes de IA & Sistemas Inteligentes

> **Objetivo:** Projetar sistemas que raciocinam, decidem e agem.  
> **Status:** A fronteira da Engenharia de IA em 2025.

## 🛑 Pare. Leia isto.
Agentes não são apenas "Prompts com Tools".
Agentes não são mágicos.
Agentes são **Sistemas de Software** que possuem **Autonomia Controlada**.

Se você construir um agente sem observabilidade, sem guardrails e sem controle de custos, você não construiu um sistema de IA — você construiu uma bomba relógio financeira.

Este bloco transforma você de "alguém que sabe chamar tools" em um **Arquiteto de Sistemas Agênticos**.

---

## 📚 Ementa do Módulo

### [Módulo 1: O que são Agentes de IA (Realmente)](./01-agent-definitions)
- **Definição:** A diferença entre um Workflow (RAG) e um Agente (Loop de Raciocínio).
- **Realidade:** Por que a maioria das demos de agentes falha miseravelmente em produção.
- **Spectrum:** De "Router Simples" a "Multi-Agent Swarm".

### [Módulo 2: Arquiteturas de Agentes](./02-agent-architectures)
- **Patterns:** ReAct, Plan-and-Solve, Reflection.
- **Design:** Agentes Reativos vs Agentes Deliberativos.
- **Tradeoffs:** Quando usar um grafo (LangGraph) vs uma chain linear.

### [Módulo 3: LangChain v1 para Agentes](./03-langchain-agents)
- **Tool Calling:** Como definir ferramentas com schemas Pydantic rigorosos.
- **Structured Output:** Forçando o agente a responder JSON validado, não texto livre.
- **Controle:** Separando o Prompt do Sistema da execução da ferramenta.

### [Módulo 4: LangGraph (O Coração)](./04-langgraph-orchestration)
- **State Machines:** Por que abandonamos "Chains" e usamos "Grafos de Estado".
- **Controle de Fluxo:** Loops, condicionais, retries e persistência de estado.
- **Orquestração:** Como desenhar um fluxo que se recupera de erros sozinho.

### [Módulo 5: Sistemas de Memória](./05-memory-systems)
- **Short-term:** O contexto da conversa atual.
- **Long-term:** Usando Vector DBs para lembrar preferências do usuário meses depois.
- **Engenharia:** Memória como um problema de Engenharia de Dados, não de prompt.

### [Módulo 6: MCP (Model Context Protocol)](./06-mcp-protocol)
- **O Novo Padrão:** Padronizando como IAs se conectam a dados (Slack, GitHub, Postgres).
- **Desacoplamento:** Trocando o modelo sem quebrar a integração com as ferramentas.

### [Módulo 7: Single-Agent vs Multi-Agent](./07-multi-agent-systems)
- **O Mito:** "Mais agentes = Melhor". (Geralmente é mentira).
- **Padrões de Delegação:** Supervisor, Hierárquico e Colaborativo.
- **Custo:** Como sistemas multi-agente multiplicam latência e tokens.

### [Módulo 8: Avaliação & Segurança](./08-safety-evals)
- **Perigos:** Loops infinitos, Alucinação de Tools, Prompt Injection.
- **Guardrails:** Colocando cercas elétricas em volta do agente.
- **Timeouts:** Nunca deixe um agente rodar para sempre.

### [Módulo 9: Human-in-the-Loop](./09-human-in-the-loop)
- **Aprovação:** O agente *propõe* uma ação (enviar email), o humano *aprova*.
- **Interrupção:** Como pausar o grafo e esperar input do usuário.
- **Auditoria:** Quem autorizou essa transação?

### [Módulo 10: Agentes em Produção](./10-agents-in-production)
- **Observabilidade:** Rastreando o pensamento do agente passo-a-passo (Langfuse).
- **Versionamento:** Como fazer deploy de uma nova versão do "cérebro".
- **Rollback:** O que fazer quando o agente enlouquece sexta-feira à noite.

---


An LLM agent can autonomously perform tasks by taking actions based on reasoning about its environment, typically through the use of tools or functions to interact with external systems.

* **Agent fundamentals**: Agents operate using thoughts (internal reasoning to decide what to do next), action (executing tasks, often by interacting with external tools), and observation (analyzing feedback or results to refine the next step).
* **Agent protocols**: [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) is the industry standard for connecting agents to external tools and data sources with MCP servers and clients. More recently, [Agent2Agent](https://a2a-protocol.org/) (A2A) tries to standardize a common language for agent interoperability.
* **Vendor frameworks**: Each major cloud model provider has its own agentic framework with [OpenAI SDK](https://openai.github.io/openai-agents-python/), [Google ADK](https://google.github.io/adk-docs/), and [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) if you're particularly tied to one vendor.
* **Other frameworks**: Agent development can be streamlined using different frameworks like [LangGraph](https://www.langchain.com/langgraph) (design and visualization of workflows) [LlamaIndex](https://docs.llamaindex.ai/en/stable/use_cases/agents/) (data-augmented agents with RAG), or custom solutions. More experimental frameworks include collaboration between different agents, such as [CrewAI](https://docs.crewai.com/introduction) (role-based team workflows) and [AutoGen](https://github.com/microsoft/autogen) (conversation-driven multi-agent systems).

📚 **References**:
* [Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction): Popular course about AI agents made by Hugging Face.
* [LangGraph](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/): Overview of how to build AI agents with LangGraph.
* [LlamaIndex Agents](https://docs.llamaindex.ai/en/stable/use_cases/agents/): Uses cases and resources to build agents with LlamaIndex.

## 🛠️ Stack de Agentes (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Orquestração** | LangGraph | Controle de estado, loops e persistência nativa. |
| **Definição de Tools** | Pydantic v2 | Validação rigorosa de input/output. |
| **Modelo** | GPT-4o / Claude 3.5 Sonnet | Modelos "inteligentes" são obrigatórios para agentes complexos. |
| **Memória** | Redis / Postgres | Persistência de estado rápida e confiável. |
| **Protocolo** | MCP | Para conectar com ferramentas externas de forma padronizada. |
| **Tracing** | Langfuse | Visualizar o loop de pensamento é vital. |

## 🧠 Mudanças Mentais Necessárias
- **Determinismo Morreu:** Agentes são probabilísticos. Seu código precisa lidar com incerteza.
- **Mais Código, Menos Prompt:** A lógica de controle deve estar em Python (Edges do Grafo), não no Prompt.
- **Falha é o Padrão:** O agente VAI errar. O sistema deve ser desenhado para se recuperar.

## 🚀 Como começar
Vá para **[Módulo 1: O que são Agentes de IA](./01-agent-definitions)**.

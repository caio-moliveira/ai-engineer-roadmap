<div align="center">
    <img src="../assets/jornada.png" alt="Jornada de Dados" width="200"/>

# 🔹 Bloco 3: Agentes de IA & Sistemas Inteligentes

> **Objetivo:** Projetar sistemas que raciocinam, decidem e agem.  
> **Status:** A fronteira da Engenharia de IA em 2026.

<p align="center">
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  </a>
  <a href="https://platform.openai.com/docs">
    <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-LLM%20API-111111?style=for-the-badge&logo=openai&logoColor=white" />
  </a>
  <a href="https://python.langchain.com/">
    <img alt="LangChain" src="https://img.shields.io/badge/LangChain-0B0B0B?style=for-the-badge&logo=langchain&logoColor=white" />
  </a>
  <a href="https://python.langchain.com/">
    <img alt="LangGraph" src="https://img.shields.io/badge/LangGraph-0B0B0B?style=for-the-badge&logo=langchain&logoColor=white" />
  </a>
  <a href="https://docs.llamaindex.ai/">
    <img alt="LlamaIndex" src="https://img.shields.io/badge/LlamaIndex-2563EB?style=for-the-badge" />
  </a>
  <a href="https://modelcontextprotocol.io/">
    <img alt="MCP" src="https://img.shields.io/badge/MCP-0EA5E9?style=for-the-badge" />
  </a>
  <a href="https://langfuse.com/">
    <img alt="Langfuse" src="https://img.shields.io/badge/Langfuse-7C3AED?style=for-the-badge" />
  </a>
  <a href="https://huggingface.co/docs/transformers">
    <img alt="Hugging Face" src="https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000000" />
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img alt="uv" src="https://img.shields.io/badge/uv-111111?style=for-the-badge&logo=astral&logoColor=white" />
  </a>
</p>
<div align="center">

### Tecnologias e padrões utilizados ao longo do bloco

Python moderno • APIs assíncronas • contratos/schemas • tool calling • state machines (grafos)
guardrails (limites, políticas, validação) • observabilidade (traces, custo, latência)
avaliação (regressão, tarefas, checks de saída) • human-in-the-loop

</div>


<div align="center">
<img src="../assets/agents.png" alt="Agentes de IA" width="1000"/>
</div>

</div>
</div>


## 📚 Ementa do Módulo

### [Módulo 1: Fundamentos de Agentes e Arquiteturas](./01-agent-fundamentals)
- **Definição:** A diferença entre um Workflow (RAG) e um Agente (Loop de Raciocínio).
- **Arquiteturas:** Padrões ReAct, Plan-and-Solve e Reflection.
- **Spectrum:** De "Router Simples" a "Multi-Agent Swarm".

### [Módulo 2: Criando seu primeiro Agente](./02-my-first-agent)
- **Tool Calling:** Como definir ferramentas com schemas Pydantic rigorosos usando LangChain.
- **Structured Output:** Forçando o agente a responder JSON validado, não texto livre.
- **Controle:** Separando o Prompt do Sistema da execução da ferramenta.

### [Módulo 3: LangGraph e Orquestração](./03-langgraph-orchestration)
- **State Machines:** Por que abandonamos "Chains" e usamos "Grafos de Estado".
- **Controle de Fluxo:** Loops, condicionais, retries e persistência de estado.
- **Orquestração:** Como desenhar um fluxo que se recupera de erros sozinho.

### [Módulo 4: Sistemas de Memória](./04-memory-systems)
- **Short-term:** O contexto da conversa atual.
- **Long-term:** Usando Vector DBs para lembrar preferências do usuário meses depois.
- **Engenharia:** Memória como um problema de Engenharia de Dados, não de prompt.

### [Módulo 5: Ferramentas e MCP](./05-tools-mcp)
- **O Novo Padrão:** Padronizando como IAs se conectam a dados com o Model Context Protocol (MCP).
- **Desacoplamento:** Trocando o modelo sem quebrar a integração com as ferramentas.

### [Módulo 6: Multi-Agent Systems](./06-multi-agents)
- **O Mito:** "Mais agentes = Melhor". (Geralmente é mentira).
- **Padrões de Delegação:** Supervisor, Hierárquico e Colaborativo.
- **Custo:** Como sistemas multi-agente multiplicam latência e tokens.

### [Módulo 7: Deep Agents](./07-deep-agents)
- **Perigos:** Loops infinitos, Alucinação de Tools, Prompt Injection.
- **Guardrails:** Colocando cercas elétricas em volta do agente.
- **Avaliação:** Como medir a eficácia das trajetórias de agentes.

### [Módulo 8: Human-in-the-Loop](./08-human-in-the-loop)
- **Aprovação:** O agente *propõe* uma ação, o humano *aprova*.
- **Interrupção:** Como pausar o grafo e esperar input do usuário.
- **Auditoria:** Rastreamento humano de execuções perigosas.

### [Módulo 9: Agentes em Produção](./09-agents-in-production)
- **Observabilidade:** Rastreando o pensamento do agente passo-a-passo (Langfuse).
- **Deploy e Versionamento:** Como versionar seu grafo e colocar em produção com segurança.
- **Monitoramento:** Métricas e rollbacks para evitar catástrofes em produção.

---


## 🚀 Por onde começar

Vá para **[Módulo 1: O que são Agentes de IA](./01-agent-definitions)**.

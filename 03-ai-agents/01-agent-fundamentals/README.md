# 🤖 Módulo 1: Fundamentos de Agentes e Arquiteturas

> **Objetivo do módulo:** estabelecer uma definição operacional de “agente” e o que muda na engenharia do sistema quando um LLM passa a **controlar o fluxo** via **tools** e **loops**, e explorar os Padrões de Design para Raciocínio (Arquiteturas).  
> **Pré-requisito:** conceitos básicos de LLM, prompt, RAG/workflows, APIs.

---

## 1) Definição operacional: o que é um Agente?

Em Engenharia de Software, “agente” não é um personagem autônomo — é uma **arquitetura**.

**Definição (prática):**  
Um **Agente de IA** é um sistema em que um **LLM atua como policy/controller**, decidindo **qual ação executar a seguir** (ou se deve responder), com base em estado, objetivos e observações do ambiente.

Na prática, isso significa:

- O LLM não é só “gerador de texto” → ele é o **componente que escolhe passos**.
- O sistema possui **ações externas** (tools) que alteram o mundo: buscar, chamar APIs, executar código, editar arquivos, consultar banco, etc.
- A execução ocorre em um **loop controlado** (com guardrails).

> **Atalho mental:** agente = **LLM (controlador) + Tools (ações) + Loop (controle)**

---

## 2) Agente vs. Workflow (ex.: RAG)

A diferença central não é “usar LLM”, e sim **quem controla o fluxo**.

### 2.1 Workflow (RAG / pipeline determinístico)
Fluxo **hardcoded**: você define a sequência e o LLM só “preenche” o texto.

Exemplo típico:
`Input → Retrieval → (Contexto) → LLM → Output`

Características:
- Controle previsível (bom para produção)
- Falhas mais fáceis de reproduzir
- Menos flexível quando há muitas rotas/decisões

### 2.2 Agente (controle pelo modelo)
Fluxo **decidido dinamicamente**: o LLM escolhe *o que fazer agora*.

Exemplo típico:
`Input → LLM decide → Tool → Observação → LLM decide → … → Output`

Características:
- Flexibilidade para tarefas multi-etapas e interativas
- Maior risco operacional (loops, custos, instabilidade)
- Exige engenharia de **controle, observabilidade e avaliação**

---

## 3) O “spectrum” de autonomia (por que isso importa)

Nem todo “agente” precisa ser autônomo. Em produção, autonomia é uma **variável de risco**.

1. **Router (baixa autonomia / baixo risco)**  
   - Decide entre caminhos conhecidos (A/B/N).  
   - Útil para roteamento: “RAG vs SQL vs FAQ”.

2. **State Machine / Graph (autonomia moderada / risco moderado)**  
   - O fluxo é um **grafo explícito**, mas o modelo decide **transições** e **loops**.  
   - Aqui entra muito bem o **LangGraph**: você define nós/arestas/estado e coloca limites.

3. **Fully Autonomous (alta autonomia / alto risco)**  
   - Planeja, executa, replaneja, cria subtarefas e decide tudo.  
   - Bom para protótipo/pesquisa; difícil de estabilizar sem muita instrumentação.

**Regra de ouro (engenharia):** dê o **mínimo** de autonomia que resolve o problema.  
Autonomia aumenta: **custo (tokens), variância, risco e dificuldade de QA**.

---

## 4) A virada “LLM + Tools” (2022–2024): como “agentes” se consolidaram

Essa fase marca quando o mercado percebe que “agente” não é só prompt — é **LLM como controlador + ferramentas externas**.

### Marcos conceituais (o que cada um adiciona ao design)
- **MRKL (2022):** blueprint neuro-simbólico modular → LLM orquestra módulos externos (conhecimento, ferramentas, raciocínio discreto).  
  **Impacto:** arquitetura modular e roteamento explícito.

- **ReAct (2022/2023):** padrão *Reasoning + Acting* → alterna raciocínio e ações (consultas, APIs).  
  **Impacto:** reduz alucinação e melhora tarefas interativas (via observação).

- **Toolformer (2023):** mostra aprendizado (supervisionado/auto-gerado) de **quando** chamar tools e **como** incorporar respostas.  
  **Impacto:** “tool use” deixa de ser artesanal.

- **Reflexion (2023):** melhora iterativa sem fine-tuning usando **feedback em linguagem** e “memória episódica”.  
  **Impacto:** introduz o loop “tentar → refletir → tentar melhor” com memória.

- **AutoGPT / wave open-source (2023):** populariza autonomia e loops (planejar → executar → avaliar), mas expõe riscos:  
  **loops infinitos**, custo alto, instabilidade, tool errors.

**Conclusão dessa fase:** agente = **loop + tools + decisões**, e não um “prompt mágico”.

---

## 5) Agentes hoje (2024–2026): menos hype, mais engenharia

A tendência recente é mover do “autônomo por autônomo” para **agentic systems controlados**:

- **Interfaces de ação bem definidas**
- **Observabilidade**
- **Avaliação/benchmarks**
- **Guardrails e limites operacionais**

### Exemplo de tese importante: Agent-Computer Interface (ACI)
Sistemas como **SWE-agent (2024)** colocam foco no “como o agente opera o ambiente”:
- navegar repositórios
- editar arquivos
- rodar testes
- abrir PRs

**Tese:** a interface (ACI) muda performance tanto quanto o modelo/prompt.

---

## 6) Componentes de um agente “de verdade” (arquitetura mínima em produção)

Um agente robusto geralmente separa responsabilidades:

### 6.1 Planejamento e roteamento
- decomposição (subtarefas)
- seleção de estratégia
- roteamento para ferramentas / especialistas

### 6.2 Tool use (ações)
- ferramentas com contratos estáveis (schema, erros, timeouts)
- validação de entradas/saídas (tipagem / JSON schema)
- retries controlados

### 6.3 Memória (quando faz sentido)
- **curto prazo** (estado da execução)
- **episódica** (tentativas, falhas, reflexões)
- **vetorial** (conhecimento recuperável)

### 6.4 Controle e segurança (guardrails)
- limites de iteração
- orçamento de tokens/custo
- timeouts
- validação de output (ex.: checagens, testes, regras)
- políticas de acesso a tools (allowlist)

> **Checklist de produção:** Sem guardrails + observabilidade, “agente” vira demo instável.

---

## 7) Por que agentes falham em produção (e como pensar como engenheiro)

Falhas comuns:

1. **Loops infinitos / thrashing**  
   - repete a mesma ferramenta/estratégia sem convergir  
   → mitigar com limites, detecção de repetição, políticas de fallback.

2. **Tools frágeis / contratos inconsistentes**  
   - API retorna 500, muda payload, não tem timeout  
   → mitigar com wrappers, schemas, versionamento, testes, circuit breaker.

3. **Estado/memória mal projetados**  
   - o agente “esquece”, contradiz, perde contexto operacional  
   → mitigar com state explícito (ex.: LangGraph), memória episódica útil, e logs.

---

## 🧠 Mental model: “o estagiário inteligente (com API access)”
Trate o agente como alguém competente, mas sem contexto e sem bom senso por padrão:
- Sem instruções e ferramentas claras → decisões ruins
- Com contratos claros + limites + observabilidade → excelente executor

---

## 8) Arquiteturas de Agentes (Padrões de Design para Raciocínio)

### 8.1 ReAct (Reason + Act)
O padrão clássico (2023).
- **Loop:**
  1. **Thought:** "O usuário pediu o clima em SP."
  2. **Action:** `get_weather("Sao Paulo")`
  3. **Observation:** "25 graus, encoberto."
  4. **Thought:** "Tenho a resposta."
  5. **Answer:** "Está 25 graus."
- **Problema:** Simples demais. Se falhar, tendencia a alucinar.

### 8.2 Plan-and-Solve (Planner)
Para tarefas complexas ("Crie um app React").
- **Passo 1 (Planner):** O agente quebra o problema em steps.
- **Passo 2 (Executor):** Outro agente executa cada passo da lista.
- **Vantagem:** Menos perda de contexto. Foco em uma tarefa por vez.

### 8.3 Reflection (Self-Correction)
O segredo da alta performance.
- O agente gera um output.
- O agente **Critica** o próprio output ("Isso está correto? Falta algo?").
- O agente **Refina** a resposta.
> **Dica de Produção:** Adicionar um passo de Reflexão melhora a precisão em ~30%, mas dobra o custo.

### 8.4 Tool-Augmented RAG
A arquitetura mais comum em empresas.
- O Agente tem acesso a uma Tool de `Retriever`.
- Ele decide *quando* pesquisar no Vector DB.
- Diferente do RAG tradicional, ele pode pesquisar múltiplas vezes ou refinar a busca.

## 🧠 Mental Model Expandido: "System 1 vs System 2"
- **LLM Padrão (Chat):** System 1 (Rápido, Intuitivo, Propenso a Erro).
- **Agente com Reflexão:** System 2 (Lento, Deliberativo, Preciso).

Use arquiteturas complexas apenas quando System 1 não for suficiente.

---

## ⏭️ Próximo passo
**Criando seu primeiro Agente:** Tool Calling, Structured Output e Controle usando LangChain.  
Ir para: `../02-my-first-agent`
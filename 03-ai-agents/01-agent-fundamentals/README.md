# Módulo 1: Fundamentos de Agentes de IA

## Objetivos de aprendizagem
Ao final deste módulo, você será capaz de:

- Definir **agentes** do ponto de vista clássico (sensores/atuadores) e moderno (LLM + tools + loop).
- Diferenciar **LLM puro**, **RAG** e **Agentes**, e entender o papel de *Agentic RAG* sem confundir conceitos.
- Identificar os **componentes essenciais** de um agente: objetivo, estado, ferramentas, memória, planejamento e controle.
- Reconhecer padrões fundamentais (ReAct, Tool Use, Reflexão, Memória/Comportamento).
- Medir qualidade com métricas práticas (sucesso, eficiência de passos, custo, latência, incidentes de segurança).
- Aplicar checklists de **segurança** e **confiabilidade** desde o design.

---

## 1. O que é um agente de IA

Em 2026, “Agente de IA” virou um termo bem prático (e às vezes meio “marketing”), mas dá pra definir assim:

Um agente de IA é um sistema que usa um modelo (geralmente um LLM) para cumprir tarefas por você com algum grau de autonomia — planejando passos, usando ferramentas (APIs, apps, web, banco de dados), acompanhando estado/memória e executando ações — tudo dentro de regras e permissões.

### 1.1 Objetivo e política
- **Objetivo**: “o que queremos” (definição de sucesso)
- **Política**: “como escolhemos ações dado o estado”
  - pode ser um prompt + regras + heurísticas + roteamento
  - em produção, frequentemente envolve *guardrails* e *governança*

### 1.2 Estado (State)
- histórico (mensagens / observações)
- variáveis de execução (passos, tentativas, custo, tempo, ferramentas usadas)
- sinais de parada (done / failed / escalate)

### 1.3 Ferramentas (Tools)
- APIs (search, DB, e-mail, calendário, ERP)
- execução de código (sandbox)
- recuperação (vector search / BM25)
- ações transacionais (criar ticket, PR, atualizar CRM)

> Regra de ouro: **tools com o menor privilégio possível**.

### 1.4 Memória
- **Curta (working)**: contexto recente + últimos passos
- **Longa (persistente)**: fatos do usuário, preferências, documentos
- **Episódica**: “o que aconteceu em execuções anteriores” (para aprender por tentativa e erro)

### 1.5 Planejamento e controle
- decomposição (subtarefas) - multi-agent ou deep-agent
- seleção de ferramenta
- verificação (checks / validators)
- replanejamento
- limites (max_steps, budget, timeouts)
- fallback / escalonamento (human-in-the-loop)

---

## 2. Agente vs LLM puro vs RAG

### LLM “puro” (chat)
**Entrada → resposta** (normalmente em um passo, sem ações no mundo, sem verificação externa obrigatória).

Bom para:
- redação, explicações, brainstorm
- respostas *sem necessidade* de ação/execução

### RAG (arquitetura)
RAG combina:
- **memória paramétrica** (pesos do modelo) +
- **memória não-paramétrica** (base recuperável)

A ideia central é: **recuperar evidência antes de gerar**.

Bom para:
- perguntas sobre documentos/KB
- grounding e citações
- reduzir alucinação em perguntas baseadas em fonte

### Agentes (arquitetura)
Agentes são sobre **ação e decisão multi-etapas** (não só recuperar contexto). Eles:
- escolhem qual ferramenta usar
- replanejam quando algo falha
- mantêm estado e memória
- impõem limites e políticas

**Uma distinção didática excelente (e anti-hype):**
- **Workflows**: caminhos pré-definidos no código (fluxo fixo, decisões “hardcoded”)  
- **Agents**: o modelo decide dinamicamente o caminho e o uso de ferramentas (fluxo adaptativo)

> ✅ Mensagem-chave: **RAG pode ser uma ferramenta dentro de um agente** (*Agentic RAG*), mas **agente ≠ RAG**.

---

## 3. Padrões fundamentais (o “currículo mínimo”)

### Padrão A — ReAct (Reason + Act)
**O que é:** intercala raciocínio e ações em loop, melhorando capacidade e interpretabilidade.  
**Por que ensinar:** é o padrão base de agente moderno.

**Lab sugerido**
- Tools: `search()` e `calculator()`
- Tarefa: “Encontre 3 métricas de qualidade de retrieval e calcule um score composto”
- Avaliar: nº de chamadas, acerto final, custo estimado

Paper: **ReAct: Synergizing Reasoning and Acting in Language Models** (Yao et al.)  
- https://arxiv.org/abs/2210.03629

---

### Padrão B — Tool Use como capacidade (Toolformer / MRKL)
**Toolformer**
- Mostra como modelos podem aprender **quando** chamar ferramentas e **como** usar resultados.

Paper: **Toolformer: Language Models Can Teach Themselves to Use Tools** (Schick et al.)  
- https://arxiv.org/abs/2302.04761

**MRKL**
- Reforça a visão de arquitetura **modular**: LLM + módulos externos (conhecimento e raciocínio discreto).
- Ótimo para ensinar que “agente” é **engenharia de sistemas**, não só prompt.

Paper: **MRKL Systems: A modular, neuro-symbolic architecture...** (Karpas et al.)  
- https://arxiv.org/abs/2205.00445

---

### Padrão C — Reflexão e melhoria sem fine-tuning (Reflexion)
**O que é:** usa feedback do ambiente e guarda “reflexões” em memória episódica para melhorar a política em tentativas futuras.

**Lab sugerido**
- Rodar o agente 3 vezes no mesmo tipo de tarefa (ex.: “gerar SQL seguro”)
- Guardar erros → escrever “reflexão” → reexecutar
- Comparar taxa de sucesso e número de tool calls

Paper: **Reflexion: Language Agents with Verbal Reinforcement Learning** (Shinn et al.)  
- https://arxiv.org/abs/2303.11366

---

### Padrão D — Agentes com memória e comportamento (Generative Agents)
**O que é:** arquitetura com registro de experiências, síntese de reflexões e recuperação dinâmica para planejar comportamento.

**Por que ensinar:** consolida memória como componente arquitetural (e não “chat history”).

Paper: **Generative Agents: Interactive Simulacra of Human Behavior** (Park et al.)  
- https://arxiv.org/abs/2304.03442

---

## 4. Avaliação: como saber se o agente presta

Você precisa ensinar avaliação **desde o começo** (e não depois que a demo “funciona”).

### 4.1 Benchmarks
- **AgentBench: Evaluating LLMs as Agents**  
  https://arxiv.org/abs/2308.03688

### 4.2 Métricas práticas (produção)
- **Task success rate** (sucesso final)
- **Step efficiency** (passos / tool calls)
- **Cost** (tokens + ferramentas pagas)
- **Latency**
- **Safety incidents** (ações indevidas)
- **Robustez** (variação com prompts/inputs adversariais)


---

## 5. Segurança e confiabilidade (da demo ao produto)

### 5.1 Prompt injection é risco central
Prompt injection não é “SQL injection para LLMs”. É um risco estrutural em sistemas que misturam **dados + instruções**, frequentemente com padrão de vulnerabilidade tipo **confused deputy**.

Leituras:
- OWASP GenAI Security Project — **LLM Top 10 / Prompt Injection**  
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- NCSC (UK) — “Prompt injection is not SQL injection (it may be worse)”  
  https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection


---

➡️ Avance para o próximo módulo: **Criando seu primeiro agente**.
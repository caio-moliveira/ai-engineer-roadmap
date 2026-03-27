# Módulo 8: Deep Agents — O Harness da LangChain

> **Objetivo:** Abstrair o boilerplate de agentes LangGraph com o framework `deepagents`.
> **Pré-requisito:** Módulos 4-7 (LangChain Agents, LangGraph, Multi-Agents).
> **Instalação:** `pip install deepagents` (já incluso no `pyproject.toml`)

---

## O Problema que o Deep Agents Resolve

Nos módulos anteriores, para criar um agente com memória, subagentes e HITL você precisava:

```python
# O que você escrevia ANTES (módulos 4-7):
StateGraph(RouterState)
  .add_node("classify", classify_node)
  .add_node("subagent_a", subagent_node)
  .add_conditional_edges(...)
  .compile(checkpointer=MemorySaver())
```

Com o Deep Agents, você declara **o que quer**, não **como implementar**:

```python
# O que você escreve AGORA:
agent = create_deep_agent(
    model="gpt-4o",
    tools=[minha_tool],
    subagents=[{"name": "especialista", "tools": [...]}],
    checkpointer=MemorySaver(),
)
```

O harness entrega automaticamente: TodoList, filesystem virtual, subagentes, HITL e memória.

---

## Índice de Scripts

| Arquivo | Conceito Central | Caso de Uso Real |
|---------|-----------------|-----------------|
| [01_first_deep_agent.py](01_first_deep_agent.py) | `create_deep_agent` básico + `thread_id` | Help Desk de TI |
| [02_subagents.py](02_subagents.py) | Subagentes declarativos + `task()` | Análise de Propostas Comerciais |
| [03_backends.py](03_backends.py) | StateBackend / FilesystemBackend / StoreBackend / CompositeBackend | Triagem de Currículos |
| [04_skills.py](04_skills.py) | Skills + Progressive Disclosure + `SKILL.md` | Assistente Executivo de CEO |
| [05_memory.py](05_memory.py) | `AGENTS.md` + memória cross-session via StoreBackend | CRM de Vendas B2B |
| [06_pipeline_real_world.py](06_pipeline_real_world.py) | Tudo junto: subagentes + CompositeBackend + HITL + TodoList | Pipeline de Conteúdo B2B |

---

## 01 — Primeiro Deep Agent

**Arquivo:** `01_first_deep_agent.py`

O ponto de entrada do módulo. Cria um agente de Help Desk de TI com 4 ferramentas customizadas e demonstra o que o harness entrega de graça.

**O que você aprende:**
- `create_deep_agent()`: a função de fábrica central do framework
- `thread_id`: como o agente mantém memória de conversa por sessão
- Ferramentas embutidas de filesystem: `ls`, `read_file`, `write_file`, `grep` (sem código extra)
- `StateBackend` padrão: memória efêmera, isolada por thread

```python
agente = create_deep_agent(
    model="gpt-4o-mini",
    tools=[buscar_solucao, abrir_ticket, consultar_ticket],
    system_prompt="Você é o agente de Help Desk de TI..."
)

config = {"configurable": {"thread_id": "usuario-joao"}}
agente.invoke({"messages": [{"role": "user", "content": "Minha VPN caiu"}]}, config=config)
```

---

## 02 — Subagentes

**Arquivo:** `02_subagents.py`

Subagentes especializados declarados como dicts — sem StateGraph, sem nodes, sem edges manuais. O harness cria as threads secundárias e gerencia o ToolRuntime automaticamente.

**O que você aprende:**
- Declaração de subagentes com `name`, `description`, `model`, `system_prompt`, `tools`
- Por que usar modelos diferentes por subagente (custo vs. qualidade)
- Isolamento de contexto: o subagente não polui a memória do agente principal
- Regra de ouro: **subagentes são stateless** — cada `task()` começa do zero

```python
subagentes = [
    {
        "name": "analista_financeiro",
        "model": "gpt-4o-mini",          # Econômico para análise numérica
        "tools": [calcular_roi, buscar_benchmarks],
        "description": "Calcula ROI e viabilidade financeira de propostas",
    },
    {
        "name": "redator_resposta",
        "model": "gpt-4o",               # Capaz para escrita executiva
        "tools": [],                     # Usa filesystem embutido
        "description": "Redige emails executivos formais",
    },
]

agente = create_deep_agent(model="gpt-4o", subagents=subagentes)
# O agente principal chama: task(agent="analista_financeiro", instruction="...")
```

---

## 03 — Backends de Filesystem

**Arquivo:** `03_backends.py`

Os backends definem **onde** os arquivos que o agente cria vivem e **por quanto tempo**. Entender backends é fundamental para arquitetar agentes corretos para cada contexto.

**O que você aprende:**

| Backend | Onde armazena | Persiste? | Quando usar |
|---------|--------------|-----------|-------------|
| `StateBackend` | RAM, na thread | Não (por thread) | Rascunhos, trabalho descartável |
| `FilesystemBackend` | Disco real | Sim (arquivo físico) | CLIs, scripts locais, automações |
| `StoreBackend` | InMemoryStore / PostgresStore | Sim (cross-thread) | Dados entre sessões |
| `CompositeBackend` | Roteamento por prefixo | Depende da rota | Híbrido: efêmero + persistente |

```python
# Backend híbrido: roteamento por prefixo de caminho
def backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),                        # /qualquer → efêmero
        routes={"/banco_aprovados/": StoreBackend(runtime)}, # /banco_aprovados/ → persistente
    )

agente = create_deep_agent(backend=backend, store=InMemoryStore())
```

---

## 04 — Skills e Progressive Disclosure

**Arquivo:** `04_skills.py`
**Skills criadas:** `skills/analise-financeira/SKILL.md` e `skills/email-executivo/SKILL.md`

Skills são habilidades especializadas em arquivos Markdown carregadas sob demanda. O agente só carrega o conteúdo completo quando decide que a skill é relevante para a tarefa — economizando tokens de contexto.

**O que você aprende:**
- Formato obrigatório do `SKILL.md`: frontmatter YAML com `name` e `description`
- Progressive Disclosure: o agente lê apenas o `description` de todas as skills e decide qual carregar
- Por que usar skills em vez de colocar tudo no `system_prompt`
- `FilesystemBackend` é obrigatório para carregar skills do disco

```
skills/
├── analise-financeira/
│   └── SKILL.md    ← Carregada quando o agente precisa calcular ROI
└── email-executivo/
    └── SKILL.md    ← Carregada quando o agente precisa redigir comunicação formal
```

```markdown
<!-- SKILL.md: frontmatter é obrigatório -->
---
name: analise-financeira
description: Framework para avaliar ROI, viabilidade e benchmarks de propostas B2B
---

# Skill: Análise Financeira
...conteúdo completo carregado apenas quando necessário...
```

```python
agente = create_deep_agent(
    backend=FilesystemBackend(root_dir=CURRENT_DIR, virtual_mode=True),
    skills=[SKILLS_DIR],   # Diretório com subpastas contendo SKILL.md
)
```

---

## 05 — Memória Persistente

**Arquivo:** `05_memory.py`
**Arquivo de contexto:** `AGENTS.md`

Duas camadas de memória com propósitos completamente diferentes. Confundi-las é o erro mais comum ao construir agentes de produção.

**O que você aprende:**

| | `AGENTS.md` | `StoreBackend em /memorias/` |
|--|-------------|------------------------------|
| **O que é** | Briefing fixo do agente | Caderno de anotações dinâmico |
| **Quando carrega** | Sempre, no startup | Quando o agente lê/escreve |
| **Muda durante execução?** | Não | Sim |
| **Persiste entre sessões?** | N/A (é um arquivo estático) | Sim, via InMemoryStore |
| **Exemplo de uso** | "Você trabalha em vendas B2B" | "Acme: decisor é João, objeção: preço" |

```python
# AGENTS.md: sempre presente (FilesystemBackend lê automaticamente no startup)
# /memorias/: persistente entre threads (StoreBackend)

def backend_crm(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memorias/": StoreBackend(runtime)},  # Memória cross-session
    )

agente = create_deep_agent(backend=backend_crm, store=InMemoryStore())

# Sessão 1 (thread A): agente salva perfil do cliente em /memorias/prospect_acme.md
# Sessão 2 (thread B): agente lê /memorias/prospect_acme.md e "lembra" de tudo
```

---

## 06 — Pipeline Real-World (Integração Total)

**Arquivo:** `06_pipeline_real_world.py`

O arquivo de fechamento do módulo. Combina todos os conceitos em um pipeline de produção de conteúdo B2B com HITL (Human-in-the-Loop) para aprovação editorial.

**O que você aprende:**
- Como combinar subagentes + CompositeBackend + HITL + TodoList em um único agente
- `interrupt_on`: pausa a execução antes de uma tool específica ser executada
- `Command(resume=...)`: retoma a execução após decisão humana (aprovar / rejeitar)
- `checkpointer`: preserva o estado completo durante a pausa do HITL

```python
agente = create_deep_agent(
    subagents=[pesquisador, redator],           # Delegação de trabalho
    backend=CompositeBackend(...),              # Rascunhos efêmeros + biblioteca persistente
    interrupt_on={"publicar_conteudo": True},  # HITL antes de publicar
    checkpointer=MemorySaver(),                 # Preserva estado durante pausa
    store=InMemoryStore(),                      # Biblioteca persistente cross-session
)
```

**Fluxo do pipeline:**
```
[Usuário solicita conteúdo]
        ↓
[Agente: write_todos() — planeja as etapas]
        ↓
[task(pesquisador) — coleta dados de mercado]
        ↓
[task(redator) — escreve o post]
        ↓
[publicar_conteudo() — PAUSA! Aguarda aprovação humana]
        ↓
[Humano: aprovar → salva na biblioteca | rejeitar → volta ao redator]
        ↓
[Conteúdo disponível em /biblioteca/ — visível em qualquer sessão futura]
```

---

## Arquivos de Suporte

| Arquivo | Tipo | Usado por |
|---------|------|-----------|
| `AGENTS.md` | Contexto estático do agente | `05_memory.py` |
| `skills/analise-financeira/SKILL.md` | Skill de análise financeira | `04_skills.py` |
| `skills/email-executivo/SKILL.md` | Skill de comunicação executiva | `04_skills.py` |

---

## Arquitetura Geral do Deep Agents

```
create_deep_agent()
│
├── TodoListMiddleware      ← write_todos() — planejamento automático de tarefas
├── FilesystemMiddleware    ← ls, read_file, write_file, edit_file, glob, grep
│   └── Backend plugável   ← State / Filesystem / Store / Composite
├── SubAgentMiddleware      ← task() — delegação para subagentes especializados
├── SkillsMiddleware        ← carregamento progressivo de SKILL.md files
├── HumanInTheLoopMiddleware← interrupt_on — pausa para aprovação humana
└── MemoryMiddleware        ← AGENTS.md + StoreBackend para memória cross-session
```

---

## ⏭️ Próximos Passos

Este módulo encerra a sub-jornada de infraestrutura de agentes.

Com `create_deep_agent` você tem o stack completo para colocar agentes em produção. O próximo passo é aprender a **hospedar, monitorar e iterar** sobre esses agentes no ecossistema LangSmith — observabilidade, tracing, avaliação de qualidade e deployment.

# 🌊 Módulo 8: Deep Agents (The Harness)

> **Goal:** Abstrair Código Massante (*Boilerplate*).  
> **Status:** O novo padrão recomendado "Out-of-the-Box" da LangChain.

Se você olhou para os arquivos dos **Módulos 4, 5 e 6** e percebeu que precisou repetir muito código arquitetural para montar *Checkpointers*, *Subagentes*, roteamento em `Node`, abstrações do *ToolRuntime* e manipulação do disco físico (`os` e globbing)... você entendeu exatamente a dor que o pacote **DeepAgents** visa sarar.

O `deepagents` (instalado via `pip install deepagents`) é um super-empacotador. Ele possui a função de fábrica `create_deep_agent`, que engole o seu Agente primitivo e já cospe ele dotado de super-conhecimento, memórias independentes e ferramentas padronizadas (harness/arreios da LangChain).

---

## 📚 Índice de Scripts Práticos

Todos os códigos rodam nativamente (Console/Terminal). Para executá-los, acesse a pasta `python/` (requer `pip install deepagents`).

1. **[Gerenciando Backends](#1-arquitetura-de-backends-backends-and-fs)** -> `python/01_backends_and_fs.py`
2. **[Habilidades Dinâmicas sem Esforço](#2-skills-e-o-harness)** -> `python/02_skills_and_harness.py`
3. **[Subagentes Baseados em Dicionário](#3-subagentes-sem-códigos-duplicados)** -> `python/03_deep_subagents.py`

---

## 1. Arquitetura de Backends (Backends and FS)

Deep Agents abandonam a ideia de que a IA está solta do mundo (ou rodando via Python Scripts expostos). O pacote injeta explicitamente **Segurança e Espaço** em camadas chamadas Backends:

- **StateBackend (Ephemeral):** Padrão. O Agente salva coisas em disco apenas virtualmente (na RAM, anexado ao *Thread* do Checkpointer). Reiniciou o chat, perdemos o rascunho.
- **FilesystemBackend (Local Sandboxed Disk):** Um verdadeiro Sandbox. O Harness expõe nativamente dezenas de tools (`ls`, `grep`, `edit_file`, `write_file`) automaticamente. Se ligado no modo `virtual_mode=True`, impede ataques de **Path Traversal Hacker** bloqueando o agente de navegar pro seu `/etc/passwd` ou apagar seu `C:/`.

---

## 2. Skills e o Harness

No módulo passado criamos o `load_skill` manualmente e rodamos um prompt switch dinâmico. Foi difícil, certo? 
Em `create_deep_agent(..., skills=["./minhas-skills/"])`, tudo aquilo está feito nos bastidores!

Essa arquitetura padroniza o uso de Habilidades via **Markdown** (`SKILL.md`). Diferentes times de uma empresa (Jurídico, Dev, QA) podem escrever arquivos `.md` e jogar na pasta. A IA puxará as habilidades deles progressivamente durante as conversas (Progressive Disclosure) sob demanda para poupar tokens de sua *Janela de Contexto*.

---

## 3. Subagentes Sem Códigos Duplicados

Da mesma forma, ao invés de codificação massiva envolvendo `@tool`, `tool_call_id`, `runtime` em SubAgents paralelos... o Harness exige apenas definições declarativas:

```python
agent = create_deep_agent(
    model="...",
    subagents=[
        {
            "name": "nome_skill",
            "description": "...",
            "system_prompt": "...",
            "tools": [...],
            "model": "gpt-mini" # Você economiza rodando IAs baratas para tarefas bobas
        }
    ]
)
```

O LangChain criará a Thread Secundária, envelopará as tools sem entupir a Memória pai (MainAgent), garantindo que as operações de código funcionem suavemente.

## ⏭️ Fim dos Fundamentos Sub-Jornada.
Este módulo encerra seus estudos sobre a Infraestrutura pesada dos Agentes e abre as portas do framework máximo: Como hospedar isso para o mundo no ecossistema LangSmith!

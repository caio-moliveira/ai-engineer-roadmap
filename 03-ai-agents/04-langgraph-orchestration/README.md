# 🧶 Módulo 4: LangGraph (O Coração da Orquestração)

> **Goal:** Controle total sobre o loop.  
> **Status:** A ferramenta mais importante de 2025.

## 1. Por que Grafos?
Agentes vivem em loops. Chains (Cadeias) são lineares.
LangGraph permite criar arquiteturas cíclicas com persistência de estado.

## 2. Componentes Chave

### O State (Estado)
A "memória" de curto prazo do agente. Tudo que precisa persistir entre passos.

```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    # add_messages é um reducer que faz append automático
```

### O Grafo
```python
workflow = StateGraph(AgentState)

# Nodes (Ações)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Edges (Decisões)
workflow.add_conditional_edges(
    "agent",
    should_continue, # Função Python que decide True/False
    {
        "continue": "tools",
        "end": END
    }
)
workflow.add_edge("tools", "agent") # Loop volta para o agente
```

## 3. Human-in-the-Loop (Interrupção)
LangGraph permite "pausar" a execução.
Isso é crucial para ações sensíveis (ex: transferir dinheiro).

```python
# O grafo para antes de executar o nó 'action'
app = workflow.compile(interrupt_before=["action"])

# ... execução para ...
# ... humano aprova ...

# Resume
app.invoke(None, config=thread_config)
```

## 4. Time Travel (Debugging)
Como o estado é versionado, você pode "voltar no tempo", editar o estado (corrigir uma decisão ruim do agente) e "dar play" novamente do meio do fluxo. Essencial para debugging.

## 🧠 Mental Model: "Flowchart Executável"
LangGraph nada mais é do que desenhar um fluxograma de processo e fazer ele rodar código. Se você consegue desenhar o processo no papel, você consegue codar no LangGraph.

## ⏭️ Próximo Passo
O agente precisa lembrar de coisas.
Vá para **[Módulo 5: Sistemas de Memória](../05-memory-systems)**.

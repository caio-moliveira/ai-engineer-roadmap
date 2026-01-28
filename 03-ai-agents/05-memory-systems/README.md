# 🧠 Módulo 5: Sistemas de Memória

> **Goal:** Transformar interações isoladas em relacionamentos.  
> **Status:** Engenharia de Dados aplicada.

## 1. Tipos de Memória
Em produção, "chat history" não é suficiente.

1.  **Short-Term (Contexto):** O que acabou de ser dito. Gerenciado pelo `AgentState`. Limitado pela janela de contexto (128k tokens).
2.  **Long-Term (Episódica):** Histórico de conversas passadas. Armazenado em Banco de Dados (Postgres).
3.  **Semântica (Conhecimento):** "O usuário gosta de Python". Armazenado em Vector DB (Profile RAG).

## 2. O Problema da Janela de Contexto
Você não pode enviar o histórico de 1 ano para o LLM. Vai custar $50 por mensagem e ficar lento.
**Estratégias de Compressão:**
- **Summarization:** A cada 10 mensagens, peça para um LLM resumir a conversa e guarde apenas o resumo.
- **Window Buffer:** Mantenha apenas as últimas K mensagens (K=10).

## 3. Memória Procedural (Zep / LangMem)
Plataformas dedicadas de memória extraem "Fatos" das conversas automaticamente.
- Conversa: "Vou viajar para Paris semana que vem."
- Sistema de Memória Extrai: `User.travel_plans = {"dest": "Paris", "date": "next week"}`
- Futuro: O agente sabe que você está em Paris sem você falar.

## 4. Implementação no LangGraph
Usamos `Checkpointers` para persistir o estado automaticamente.

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    app = workflow.compile(checkpointer=checkpointer)
    
    # thread_id isola a memória de cada usuário/sessão
    config = {"configurable": {"thread_id": "user-123"}}
    app.invoke(input, config=config)
```

## 🧠 Mental Model: "RAM vs HD"
- **Context Window** é a RAM. Rápida, cara, volátil e limitada.
- **Vector/SQL DB** é o HD. Lento, barato, persistente e infinito.
Sua engenharia de memória é decidir o que mover da RAM para o HD e quando trazer de volta.

## ⏭️ Próximo Passo
Conectando ferramentas de forma padronizada.
Vá para **[Módulo 6: MCP](../06-mcp-protocol)**.

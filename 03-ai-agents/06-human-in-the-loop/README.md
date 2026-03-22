# 🤝 Módulo 9: Human-in-the-Loop (HITL)

> **Goal:** Automação Assistida, não Cega.  
> **Status:** O diferencial de confiança.

## 1. Por que Humanos?
Para ações irreversíveis (enviar dinheiro, deletar recursos, enviar email para cliente), a IA deve **Propor**, o Humano deve **Dispor**.

## 2. Patterns de HITL

### Approval (Aprovação)
O agente para antes de executar a Tool.
- UI mostra: "Agente quer enviar email para 'joao@gmail.com'. Aprovar?"
- Humano clica "Sim".
- Agente resume.

### Editing (Edição)
O agente gera um rascunho de email.
- Humano edita o texto.
- Agente envia a versão editada.
- Isso serve como **Feedback Implícito** para treinar o agente.

### Debugging (Intervenção)
O agente travou. O desenvolvedor entra no painel, vê o estado, corrige a variável errada e manda continuar.

## 3. Implementação no LangGraph
Basta usar `interrupt_before=["tool_name"]`.
O estado fica persistido no banco até o humano enviar um sinal de resume.

## 🧠 Mental Model: "O Copiloto"
Um copiloto não pousa o avião sem avisar o capitão se houver risco.
Ele prepara tudo, calcula a rota, e diz "Pronto para descer?".

## ⏭️ Próximo Passo
Levando tudo isso para produção.
Vá para **[Módulo 10: Agentes em Produção](../10-agents-in-production)**.

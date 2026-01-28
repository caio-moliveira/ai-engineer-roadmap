# 🐙 Módulo 3: Git & Workflow Profissional

> **Goal:** Commits que contam uma história.  
> **Status:** Se não está no Git, não existe.

## 1. Conventional Commits
Pare de escrever "fix" ou "wip".
Use prefixos semânticos que permitem gerar changelogs automáticos.

- `feat:` Nova funcionalidade.
- `fix:` Correção de bug.
- `docs:` Documentação.
- `chore:` Configuração de build, deps.
- `refactor:` Mudança de código que não altera comportamento.

Exemplo: `feat(rag): add qdrant vector store connection`

## 2. Branching Strategy: Trunk-Based Development
Para times ágeis de IA, GitFlow (develop/release/master) é lento demais.
Use **Trunk-Based**:
- Branches de vida curta (1-2 dias).
- Merge frequente na `main`.
- Use **Feature Flags** se o código não estiver pronto para o usuário.

## 3. GitHub Actions (CI para IA)
Não teste só o código. Teste os prompts.

### O Pipeline Ideal:
1.  **Lint:** Ruff (verificar estilo).
2.  **Type Check:** MyPy (verificar tipos).
3.  **Unit Test:** Pytest (funções puras).
4.  **Eval Light:** Rodar 10 exemplos de prompts críticos para garantir que nada quebrou.

## 🧠 Mental Model: "A Rede de Segurança"
O CI (Continuous Integration) é sua rede de segurança.
Ele te dá confiança para fazer refatorações pesadas sabendo que, se quebrar a lógica do RAG, o pipeline vai falhar antes de chegar na produção.

## ⏭️ Próximo Passo
Vamos escrever Python de verdade.
Vá para **[Módulo 4: Python para Engenheiros de IA](../04-python-for-ai)**.

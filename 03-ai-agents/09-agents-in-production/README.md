# 🚀 Módulo 10: Agentes em Produção

> **Goal:** Dormir tranquilo à noite.  
> **Status:** Onde a criança vira adulto.

## 1. Observabilidade (Langfuse / Arize)
Logs de texto não servem. Você precisa de **Traces**.
Você precisa ver a árvore de execução:
- Agente (Input)
  - Tool A (Call) -> (Result)
  - Tool B (Call) -> (Error) -> (Retry)
  - Tool B (Call) -> (Result)
- Agente (Output)

## 2. Custo e Latência
Agentes são caros. Um loop de 10 passos com GPT-4 pode custar $0.50.
- **Cache:** Se a pergunta já foi feita, não rode o agente.
- **Model Routing:** Use modelos menores (Haiku / 4o-mini) para passos simples de planejamento.

## 3. Versionamento de Agentes
Agentes não são determinísticos. Uma mudança no prompt pode quebrar tudo.
- Nunca faça deploy direto em prod.
- Use **Shadow Deployments**: Rode a versão nova em paralelo com a velha (sem mostrar pro usuário) e compare os logs.

## 🧱 Checklist de Produção
Antes de soltar seu agente no mundo:
- [ ] Existe um limite de loops (recursion limit)?
- [ ] As ferramentas tem timeouts?
- [ ] Existe log de todas as decisões (Traces)?
- [ ] Existe um mecanismo de "Kill Switch" para parar o agente?
- [ ] O custo por execução está monitorado?

## 🎓 Graduação
Você completou o Bloco 3.
Você agora entende que "Agentes" não são mágica, mas sistemas complexos de orquestração de estado.

**Próximo Bloco: [Infra, OCR e Modelos](../../04-infra-ocr-models)**

# 🔭 Módulo 08: Observabilidade & Avaliação de IA

> **Goal:** "Você não pode melhorar o que não pode medir."
> **Ferramentas:** `LangSmith`, `Arize Phoenix`, `OpenTelemetry`.

## 1. O Problema da Caixa Preta
Em software tradicional, se der erro 500, temos stack trace.
Em IA, o modelo responde "A capital da França é Londres" com status 200 OK.
Isso é um **Silent Failure**.

## 2. Tracing (Raio-X da Execução)
Logs lineares não funcionam para cadeias de IA (Chains/Agents).
Precisamos de **Tracing Distribuído**.
- Qual passo demorou mais? Retrieval ou Generation?
- Qual foi o prompt exato que causou o erro?
- Quantos tokens foram gastos nessa request?

*Ferramentas obrigatórias:* LangSmith, Langfuse ou Arize Phoenix.

## 3. Evals (Unit Tests para IA)
Esqueça assert `result == "expected"`. LLMs são não-determinísticos.
Usamos **LLM-as-a-Judge**.
Um LLM mais forte (GPT-4) avalia a resposta do seu sistema.

**Dataset de Ouro (Golden Dataset):**
- Input: "Como reseto minha senha?"
- Resposta Esperada: "Acesse config > segurança."
- Métrica: A resposta gerada é semanticamente similar à esperada?

## 4. Métricas de RAG (RAGas)
- **Context Precision:** O retrieval trouxe lixo ou ouro?
- **Answer Faithfulness:** O modelo inventou algo que não estava no contexto?

## ⏭️ Próximo Passo
Seu sistema funciona na sua máquina. E agora?
Vá para **[Módulo 10: Deploy, Infra e Produção](../10-deploy-production)**.

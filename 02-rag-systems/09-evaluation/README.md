# 📉 Módulo 9: Avaliação & Observabilidade

> **Goal:** Pare de Adivinhar. Comece a Medir.  
> **Status:** A única forma de melhorar.

## 1. O Problema do "Vibe Check"
A maioria dos devs testa seu RAG fazendo 3 perguntas: "Oi", "O que é X?", "Tchau".
Parece bom, então eles shippam.
Aí um usuário pergunta "Compare X e Y" e o bot alucina.

**Você não pode otimizar o que não pode medir.**

## 2. RAGAS (RAG Assessment)
O framework padrão da indústria para avaliar pipelines RAG sem labelling humano.
Ele usa um "LLM Judge" (GPT-4) para dar nota ao seu sistema.

### Métricas Core
1.  **Faithfulness:** A resposta derivou *apenas* do contexto? (Detecta Alucinação).
2.  **Answer Relevance:** Ela realmente respondeu a pergunta do usuário?
3.  **Context Precision:** O documento relevante estava no top 3?
4.  **Context Recall:** Nós achamos *toda* a info relevante?

## 3. Observabilidade (Langfuse / Arize)
Você precisa ver o trace de cada execução.

**O que logar:**
- **Input/Output:** Texto completo.
- **Latência:** Total vs. Retrieval vs. Geração.
- **Token Count:** Input vs. Output (Custo).
- **Metadata:** User ID, Session ID.

**Screenshots:** (Imagine um gráfico waterfall mostrando `Retriever (300ms)` -> `Reranker (500ms)` -> `LLM (2s)`).

## 4. Continuous Eval (CI/CD for AI)
Não avalie só uma vez. Avalie a cada commit.

**Pipeline:**
1.  **Dataset:** Um "Golden Set" de 50 pares QA (`pergunta`, `ground_truth`).
2.  **Run:** Pipeline processa todas as 50 perguntas.
3.  **Score:** Ragas calcula as notas.
4.  **Fail:** Se `Faithfulness < 0.8`, bloqueia o deploy.

## 🧠 Mental Model: "Testes Unitários vs. Evals"
- **Unit Test:** `assert sum(1, 1) == 2`. Determinístico.
- **Eval:** `assert similarity(actual, expected) > 0.9`. Probabilístico.

## ⚠️ Erros Comuns
- **Eval com modelos fracos:** Não use GPT-3.5 para dar nota no GPT-4. O juiz deve ser mais esperto que o aluno. Use GPT-4o.
- **Ignorar "Não sei":** As vezes "Não sei" é a resposta *correta*. Premie o modelo por admitir ignorância.

## ⏭️ Próximo Passo
Temos um sistema medido. Vamos para o Deploy.
Vá para **[Módulo 10: RAG em Produção](../10-rag-production)**.

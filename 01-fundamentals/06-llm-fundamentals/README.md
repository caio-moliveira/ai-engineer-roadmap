# 🤖 Módulo 06: Fundamentos de LLMs & GenAI

> **Goal:** Entender a matéria-prima da nova computação.
> **Ferramentas:** `OpenAI API`, `Anthropic`, `LangChain` (Conceitos).

## 1. Tokenização: A Unidade Atômica
Não processamos palavras, processamos tokens.
- Entenda por que `"9.11"` pode ser maior que `"9.9"`.
- Token Limits: Context Window não é infinita.
- Custo: Você paga por **Input** (barato) e **Output** (caro).

## 2. O Ciclo de Vida do Prompt
Prompt Engineering não é "pedir com educação". É estruturar contexto.
1.  **System Prompt:** Define a persona e regras imutáveis.
2.  **Few-Shot:** Exemplos ensinam mais que instruções.
3.  **User Prompt:** A query dinâmica.

## 3. Tool Calling (Function Calling)
Aqui a mágica acontece. O LLM deixa de ser um chatbot e vira um **Agente**.
O modelo retorna um JSON estruturado pedindo para executar uma função (`get_weather`, `query_sql`).
**Você** executa o código e devolve o resultado para ele.

*Frameworks:*
- Entenda como a OpenAI faz isso nativamente.
- Frameworks como `LangGraph` orquestram esses fluxos complexos de múltiplas ferramentas.

## 4. Structured Outputs (De novo)
Reforçando: Em produção, probablístico vira determinístico.
Nunca faça parse de markdown/regex na saída do LLM. Use `json_mode` ou `Structured Outputs` para garantir JSON válido.

## ⏭️ Próximo Passo
O LLM sozinho não sabe nada sobre *seus* dados privados. Vamos dar memória a ele.
Vá para **[Módulo 08: RAG (Retrieval-Augmented Generation)](../08-rag-fundamentals)**.

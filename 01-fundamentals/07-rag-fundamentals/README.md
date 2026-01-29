# 🔍 Módulo 07: RAG (Retrieval-Augmented Generation)

> **Goal:** O "Hello World" da IA moderna. Conectar o LLM aos seus dados.
> **Ferramentas:** `LangChain`, `LlamaIndex` (Conceitos), `Vector DB`.

## 1. Por que RAG?
Fine-tuning é caro e difícil de manter atualizado. RAG é ágil.
Você injeta o conhecimento no **Context Window** no momento da inferência.

## 2. O Pipeline de RAG (Etapas Críticas)
RAG não é mágica, é um pipeline de engenharia de dados.

1.  **Ingestion:** Ler PDFs, Notion, SQL.
2.  **Chunking:** Quebrar o texto. *Estratégia importa:* Sentença? Parágrafo? Markdown header?
3.  **Embedding:** Transformar texto em vetor.
4.  **Retrieval:** Buscar os N chunks mais similares.
5.  **Synthesis:** LLM gera a resposta baseada APENAS no contexto recuperado.

## 3. Chunking Strategies
- **Fixed Size:** Cortar a cada 500 caracteres (Ruim, quebra contexto).
- **Recursive Character:** Tenta manter parágrafos juntos (Padrão LangChain).
- **Semântico:** Quebra quando o assunto muda (State of the Art).

## 4. Grounding (Evitando Alucinação)
O maior medo das empresas.
- Force o modelo a responder: "Se a informação não estiver no contexto, diga 'não sei'."
- Citar fontes: O modelo deve indicar de qual chunk tirou a informação.

## ⏭️ Próximo Passo
Como sabemos se o RAG está bom? "Achei a resposta boa" não é métrica de engenharia.
Vá para **[Módulo 09: Observabilidade & Avaliação de IA](../09-observability)**.

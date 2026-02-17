# 🚀 Módulo 10: RAG em Produção

> **Goal:** 99.9% Uptime. <2s Latência. Custo Baixo.  
> **Status:** A linha de chegada.

## 1. Otimização de Latência
Usuários odeiam esperar.
- **O Gargalo:** Geralmente é a Geração do LLM.
- **O Fix:** Streaming (SSE). Mostre o primeiro token imediatamente.
- **Otimização de Retrieval:** Saia do Python `faiss` para Qdrant (Rust/C++).
- **Reranking:** Limite o reranking aos top 10 docs, não top 100.

## 2. Caching (O Cache Semântico)
Por que pagar pela mesma pergunta duas vezes?
- **Match Exato:** Redis. Se `query == "preços"`, retorna resposta cacheada.
- **Cache Semântico:** GPTCache. Se `query ≈ "quanto custa"`, retorna resposta cacheada para "preços".
- **Impacto:** Reduz custo em 30-50% e latência para 0ms.

## 3. Estratégia de Contexto Vazio
O que acontece se o Retriever não retornar nada?
- **Ruim:** LLM diz "Baseado no contexto [VAZIO]...".
- **Bom:** Lógica de Fallback.
    - "Não encontrei isso nos documentos."
    - "Buscando no Google..." (Fallback Agêntico).

## 4. Segurança (ACLs)
**O Problema do "Salário do CEO".**
- Usuário A (Estagiário) pergunta "Qual o salário do CEO?".
- Vector DB acha o doc "FolhaPagamento2024.pdf".
- LLM responde.
- **Resultado:** Vazamento de Dados.

**Fix:** Filtragem de Metadados.
```python
filters = Filter(
    must=[
        FieldCondition(key="access_level", match=MatchValue(value="public"))
    ]
)
```

## 5. Controle de Custo
- **Limites de Token:** Não deixe usuários colarem 100k palavras. Trunque o input.
- **Model Routing:** Use Haiku/GPT-4o-mini para queries simples. Use Opus/GPT-4o para complexas.

## 🧱 Checklist de Produção
Antes de shippar o Bloco 2:
- [ ] Seus chunks têm overlap?
- [ ] A extração de metadados está funcionando?
- [ ] Você está usando Hybrid Search?
- [ ] Você tem um Reranker?
- [ ] Streaming está ativado?
- [ ] Avaliação com Ragas está rodando?
- [ ] Você trata Contexto Vazio?
- [ ] Permissões (ACLs) estão aplicadas?

## 🎓 Graduação
Você completou o Bloco 2.
Você entende **Retrieval Augmented Generation** profundamente.

**Próximo Bloco: [AI Agents](../../03-ai-agents)**

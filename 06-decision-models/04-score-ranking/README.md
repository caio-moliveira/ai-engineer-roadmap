# 📊 Módulo 4: Score, Ranking e Priorização

> **Objetivo:** usar rubricas ordenadas para ordenar, priorizar e extrair features.
> **Pergunta-chave:** o que o Cohere faz que você não consegue definir numa rubrica?

---

## 📚 Índice Prático e Documentação

1. **[Rubrica de urgência](#1-score-ordena)**
   * Docs: [Score](https://docs.typesafe.ai/primitives/score)
   * Exemplo: `01_urgency_rubric.py`
2. **[Rerank de RAG](#2-rerank-com-rubrica)**
   * Docs: [Bloco 2, retrievers](../../02-rag/05-retrievers)
   * Exemplo: `02_rerank_rag.py`
3. **[Judge de qualidade](#3-judge-barato)**
   * Exemplo: `03_quality_judge.py`
4. **[Texto vira feature](#4-texto-vira-coluna)**
   * Docs: [CatBoost](https://catboost.ai/docs/)
   * Exemplo: `04_text_to_features.py`

---

## 1. Score ordena

Um Score é uma rubrica **ordenada**. O modelo de decisão devolve a distribuição por nível e o **valor esperado** (`score`), um número contínuo. É ele que ordena a fila: dois tickets "nível 2" deixam de empatar. O LLM devolve um inteiro, e dez tickets urgentes empatam. O script mede o acerto do nível e a qualidade da fila ordenada com nDCG@10.

Escreva rubricas com **critério observável** em cada nível ("o cliente está parado", não "muito urgente"). O Laya multilíngue tem viés de posição em Score registrado no model card: meça antes de confiar.

## 2. Rerank com rubrica

Seis perguntas sobre mudança climática (o tema do PDF do Bloco 2) têm dez trechos candidatos cada, na ordem do retriever vetorial. Um Score de relevância de três níveis pontua cada par (pergunta, trecho). Reordenamos pelo valor esperado e medimos recall@5 e nDCG@5 contra a ordem original.

A resposta à pergunta-chave: um reranker treinado (Cohere, cross-encoder) aprendeu "relevância" de dados que você não controla. Uma rubrica deixa você **definir** relevância para o seu caso. Por exemplo, "só conta se tiver o número". E você muda a definição editando texto, não treinando de novo.

## 3. Judge barato

Rubrica de qualidade em quatro níveis sobre as respostas do `golden_verify.json`. O script mede a concordância de cada judge com o rótulo humano e entre si (kappa de Cohen). Se o judge de decisão concorda com o judge LLM tanto quanto dois humanos concordariam, ele avalia 100% do tráfego pelo custo de uma amostra.

## 4. Texto vira coluna

Nouls e Scores viram **colunas numéricas** para um modelo clássico: P(ameaça cancelar), P(relata erro), urgência esperada. O script compara um CatBoost que prevê cancelamento em 30 dias com e sem essas colunas, em validação cruzada.

Com 60 clientes, o resultado varia muito entre dobras. O objetivo é o padrão de engenharia (texto vira decisão, decisão vira coluna), não o número.

---

## 🏋️ Exercício

Substitua o reranker do Bloco 2 (`02-rag/05-retrievers`) pelo Score de relevância:

1. Rode o retriever do Bloco 2 sobre o seu PDF e salve os 10 primeiros trechos de 10 perguntas no formato de `data/golden_rerank.json`.
2. Rotule a relevância (0, 1, 2) de cada trecho.
3. Compare recall@5 e nDCG@5 entre: ordem do retriever, o reranker que você usava e o Score. Inclua latência e custo por pergunta.

## ⏭️ Próximo Passo
Até aqui medimos acerto. Agora, o que fazer com a probabilidade: **[Módulo 5: Calibração, limiares e avaliação](../05-calibration-evaluation)**.

# 🔬 Aula 2: Raio-X — Prompt vs RAG vs Fine-Tuning

> **Objetivo:** Saber qual técnica usar para cada problema — e por quê.
> **Pergunta-chave:** Você precisa de mais contexto, de mais conhecimento, ou de outro modelo?

As três técnicas resolvem problemas **diferentes**. Usá-las erradas custa tempo, dinheiro e qualidade. Esta aula tem duas metades: primeiro a comparação técnica profunda em cinco eixos, depois um framework de decisão concreto com fluxograma.

---

## 1. O mapa mental: três alavancas distintas

Quando você quer que um LLM faça algo específico, há essencialmente três alavancas que você pode puxar — e elas mexem em dimensões diferentes do problema:

| Alavanca | O que você muda | Investimento |
|----------|-----------------|--------------|
| **Prompt Engineering** | A instrução. Few-shot, chain-of-thought, melhores descrições. | Baixo |
| **RAG** | O contexto disponível. Busca docs externos e injeta no prompt. | Médio (embeddings + vector DB) |
| **Fine-Tuning** | O modelo. Atualiza pesos para incorporar padrões da tarefa. | Alto (dataset + treino) |

---

## 2. Metade 1 — Comparação técnica em 5 eixos

### Eixo 1: O que cada técnica realmente muda

| Componente | Prompt | RAG | Fine-Tuning |
|------------|--------|-----|-------------|
| **Pesos do modelo** | Inalterados | Inalterados | Adaptados (parcial ou total) |
| **Contexto na inferência** | Prompt fixo + exemplos | Prompt + chunks buscados | Prompt enxuto |
| **Fonte do "saber"** | Pré-treino + contexto | Base externa indexada | Pré-treino + ajuste fino |
| **Atualização de conhecimento** | Editar prompt | Reindexar documentos | Re-treinar com novo dataset |

### Eixo 2: Custos

| Custo | Prompt | RAG | Fine-Tuning |
|-------|--------|-----|-------------|
| **Setup inicial** | Quase zero | Médio (embeddings + vector DB) | Alto (dataset + treino) |
| **Inferência por chamada** | Alto (prompt longo paga sempre) | Alto (prompt + chunks longos) | **Baixo** (modelo absorveu padrão) |
| **Manutenção** | Edição manual | Reindexação periódica | Re-treino quando dataset muda |
| **Hardware** | API externa serve | API + vector DB | GPU para treino, depois inferência local viável |

> 💡 **A inversão do ponto de equilíbrio:** em alto volume de chamadas, fine-tuning é o **mais barato a longo prazo**. Você pagou o setup uma vez (dataset + treino: USD dezenas a centenas) e cada inferência custa quase nada — pode rodar local. Para sistemas com milhares de chamadas/dia, a conta vira a favor do FT em semanas.

### Eixo 3: Latência

Três fontes num pipeline:
1. **Latência de rede** (se chama API externa): 50-300 ms só de ida e volta.
2. **Latência do retrieval** (em RAG): busca vetorial + reranking, 100-500 ms.
3. **Latência de inferência**: proporcional ao número de tokens (contexto + resposta).

RAG é o pior dos mundos: paga rede + retrieval + inferência com contexto grande. Fine-tuning local com modelo pequeno é o melhor: rede zero, retrieval zero, contexto enxuto. No nosso caso prático: **1,73 segundo por parágrafo** em RTX 3060 com Qwen 1.5B fine-tunado.

### Eixo 4: Atualização de conhecimento

| Situação | Prompt | RAG | Fine-Tuning |
|----------|--------|-----|-------------|
| Mudou um documento | Editar prompt manualmente | **Reindexar** ✅ | Re-treinar (dias) |
| Mudou o estilo de saída | Editar prompt | Inalterado (não resolve) | **Re-treinar** ✅ |
| Mudou o vocabulário interno | Editar prompt | Reindexar | **Re-treinar** ✅ |
| Documento secreto não pode ir para LLM externo | Inviável | Inviável | **FT local** ✅ |

### Eixo 5: Tipo de "aprendizado" — o eixo mais mal-entendido

Fine-tuning e RAG ensinam coisas **fundamentalmente diferentes**:

| RAG — memória semântica | Fine-tuning — memória procedural |
|-------------------------|----------------------------------|
| **Ensina O QUE.** "Aqui está informação que você não tinha. Use-a para responder." | **Ensina COMO.** "Quando ver entradas assim, responda assim, neste formato, com essas convenções." |
| Bom para: documentos internos, fatos atualizados, FAQ, regulações específicas. | Bom para: formato estrito, estilo de voz, classificações específicas, padrões idiossincráticos. |

> *"Few-shot prompting can teach a model to use a new tool, but cannot reliably teach it new factual knowledge. Fine-tuning can teach format and style robustly, but is a poor way to inject up-to-date factual content — for that, retrieval is more effective."*

### Pipeline híbrido: quase sempre o melhor

Na prática, sistemas de produção combinam as três:

```
Pergunta do usuário
        ↓
    [RAG retrieve docs]
        ↓
    [PROMPT template + context]
        ↓
    [FINE-TUNED MODEL]      ← aprendeu formato, estilo, convenções
        ↓
Resposta no formato aprendido + contexto atualizado
```

RAG fornece o "**o quê**", o modelo fine-tunado garante o "**como**".

---

## 3. Metade 2 — Framework de decisão

Use este fluxograma na ordem. A primeira "sim" determina sua abordagem inicial. Você sempre pode evoluir depois.

```
1. Volume de chamadas/dia é alto (1k+) e custo por chamada importa?
   └─ Sim → considere FINE-TUNING com modelo pequeno local.

2. Dados são confidenciais e não podem sair da sua infra?
   └─ Sim → FINE-TUNING local ou RAG com modelo local.

3. Output tem formato estrito (JSON com schema, XML) ou estilo idiossincrático?
   └─ Sim → FINE-TUNING consegue qualidade superior.

4. Resposta depende de informação que muda com frequência?
   └─ Sim → RAG é a resposta. (Pode combinar com FT para formato.)

5. Tarefa é simples e cabem 3-5 exemplos no contexto?
   └─ Sim → FEW-SHOT PROMPTING em modelo grande.

6. É um protótipo / POC?
   └─ Sim → comece com PROMPT ENGINEERING em modelo top de linha.
```

---

## 4. Anti-padrões que você vai ver em projetos reais

❌ **"Fine-tunei nos meus PDFs e ele não sabe o que está nos PDFs."**
Fine-tuning ensina formato/estilo, não fatos. Documentos que mudam ou precisam ser citados de volta com precisão pedem **RAG**.

❌ **"Vou fazer RAG do meu schema JSON."**
Schema é estrutura, não conhecimento. RAG vai injetar o schema em todo prompt, gastando tokens, e ainda assim o modelo escapa do formato. **Fine-tuning** faz o modelo memorizar o formato como segunda natureza.

❌ **"Fine-tunei sem definir métrica de sucesso, agora não sei se está bom."**
Sem métricas pré-definidas, qualquer resultado parece "ok". Loss baixa de treino **não** é métrica de sucesso. A Aula 3 entra em PRD; a Aula 4 em métricas estruturais.

---

## 5. O nosso caso prático justifica fine-tuning

O projeto que vai aparecer nas Aulas 3 e 4 (extração estruturada de citações de leis brasileiras) é um exemplo paradigmático de onde FT brilha:

- **Output em JSON estrito** com 7 campos e vocabulário fechado → formato.
- **Alto volume** previsto (milhares de documentos jurídicos) → custo por chamada importa.
- **Latência crítica** (rodar local em pipeline batch) → API externa é gargalo.
- **Dados privados** em alguns clientes → preciso rodar on-prem.
- **Conhecimento estável** (catálogo de ~30 leis brasileiras canônicas; muda raramente) → não precisa de RAG.

---

## 📚 Referências da aula

- **Lewis et al. (2020).** *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. — [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)
- **Brown et al. (2020).** *Language Models are Few-Shot Learners* (GPT-3, fundamento de few-shot). — [arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)
- **Wei et al. (2022).** *Chain-of-Thought Prompting Elicits Reasoning in LLMs*. — [arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
- **Asai et al. (2023).** *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*. — [arxiv.org/abs/2310.11511](https://arxiv.org/abs/2310.11511)
- **OpenAI Cookbook.** *When to use fine-tuning*. — [cookbook.openai.com](https://cookbook.openai.com/examples/how_to_finetune_chat_models)
- **Anthropic.** *Prompt engineering vs fine-tuning*. — [docs.anthropic.com](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## ⏭️ Próximo passo

Decidiu que FT é o caminho? Hora de planejar e gerar o dataset.
Vá para **[Aula 3: Pipeline — Planejamento e Dataset](../03-pipeline)**.

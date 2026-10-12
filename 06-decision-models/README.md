<div align="center">
    <img src="../assets/jornada.png" alt="Jornada de Dados" width="200"/>

# 🔹Bloco 6: Modelos de Decisão (System One Models)

> Módulo de modelos de decisão para engenheiros de IA, outubro de 2026.
> Modelos que não geram texto: recebem um estado e perguntas tipadas e devolvem decisões com probabilidade calibrada.

<p align="center">
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  </a>
  <a href="https://docs.typesafe.ai/">
    <img alt="Jev" src="https://img.shields.io/badge/TypeSafe-Jev%201.13-111111?style=for-the-badge" />
  </a>
  <a href="https://huggingface.co/convaiinnovations/laya-multilingual">
    <img alt="Laya" src="https://img.shields.io/badge/Laya-Apache%202.0-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000000" />
  </a>
  <a href="https://docs.langchain.com/oss/python/integrations/providers/typesafe">
    <img alt="LangChain" src="https://img.shields.io/badge/langchain--typesafe-Runnable%20%2B%20Middleware-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
  </a>
  <a href="https://langchain-ai.github.io/langgraph/">
    <img alt="LangGraph" src="https://img.shields.io/badge/LangGraph-Agente%20h%C3%ADbrido-1C3C3C?style=for-the-badge" />
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img alt="uv" src="https://img.shields.io/badge/uv-Python%20Package%20Manager-111111?style=for-the-badge&logo=astral&logoColor=white" />
  </a>
</p>

<div align="center">

### Tecnologias e padrões utilizados ao longo do módulo

Choice • Noul • Score • calibração (ECE, Brier) • limiar e curva de automação
golden set • replay de fixtures • harness de comparação justa • guardrail e verificação
roteamento de modelo • rerank • agente híbrido em LangGraph • fine-tune de modelo de decisão

</div>
</div>

## Por que este bloco existe

Os blocos 1 a 5 ensinam a gerar texto com LLMs, conectá-los a dados, orquestrar agentes e ajustar modelos. Falta a categoria que mais aparece num agente de produção: as chamadas que **roteiam, classificam, bloqueiam e verificam**. Hoje a gente resolve isso com prompt e JSON. É caro, lento e não tem probabilidade confiável.

Um modelo de decisão (System One Model, no vocabulário de Kahneman: rápido e intuitivo) troca "gerar a palavra *financeiro*" por "devolver a distribuição sobre as quatro filas". A diferença muda a engenharia: com probabilidade calibrada, o código decide quanto automatizar.

O bloco fecha um ciclo da trilha: volta ao agente do Bloco 3 e ao RAG do Bloco 2 e os reconstrói com decisões no lugar certo.

## 📚 Ementa do Módulo

### [Aula 1: Fundamentos de modelos de decisão](./01-decision-fundamentals)
- **Pergunta-chave:** por que gerar texto para responder uma pergunta de múltipla escolha?
- A chamada HTTP crua, o SDK oficial, a mesma pergunta num LLM e no Laya local.
- Os três primitivos lado a lado, calibração em uma frase e a matriz "código, decisão, LLM ou classificador".

### [Aula 2: Choice, roteamento e seleção](./02-choice-routing)
- **Pergunta-chave:** quantas vezes o seu agente lê 10 descrições de tool só para escolher uma?
- Fila de tickets, escolha de tool contra function calling, roteamento barato e caro, hierarquia de rótulos.
- `TypeSafeClassifier` como Runnable e o `ModelRouterMiddleware` num `create_agent`.

### [Aula 3: Noul, detecção e verificação](./03-noul-detection-verification)
- **Pergunta-chave:** "é spam?" é uma pergunta ou seis?
- Spam decomposto em sinais, multirrótulo, guardrail de entrada, verificação da saída do LLM.
- Gate de risco de tool call com o `AutoModeMiddleware`.

### [Aula 4: Score, ranking e priorização](./04-score-ranking)
- **Pergunta-chave:** o que o Cohere faz que você não consegue definir numa rubrica?
- Urgência ordenada pelo valor esperado, rerank de RAG, judge barato de qualidade, texto virando feature para CatBoost.

### [Aula 5: Calibração, limiares e avaliação](./05-calibration-evaluation)
- **Pergunta-chave:** com limiar 0,85, quanto você automatiza e com que precisão?
- Golden set, ECE e diagrama de confiabilidade, curva de automação, harness de comparação justa, gravação de fixtures.

### [Aula 6: Projeto final, agente híbrido](./06-final-project-hybrid-agent)
- **Pergunta-chave:** quanto custa cada decisão do seu agente, antes e depois?
- Grafo LangGraph com guardrail, triagem, geração e verificação; provider por node; relatório de custo, latência p95, acurácia e concordância.

### [Aula 7 (bônus): construa o seu próprio modelo de decisão](./07-bonus-build-your-own)
- Cabeça de scoring sobre um encoder, fine-tune do Laya nos seus dados e um servidor `/v1/systemone` próprio.
- Pré-requisito: [Bloco 5](../05-fine-tuning).

---

## Os modelos e as superfícies

| Modelo | Origem | Licença | Como o bloco acessa | Papel |
|---|---|---|---|---|
| Jev 1.13 | TypeSafe AI | proprietário, API, acesso antecipado | `typesafe-sdk`, `langchain-typesafe`, HTTP | referência de qualidade |
| Laya multilíngue (`convaiinnovations/laya-multilingual`) | Convai Innovations | Apache 2.0 | `laya-serve` local em `/v1/systemone` | alternativa open-weight, privacidade, base para fine-tune |
| Claude Haiku 4.5 e GPT-5.6 Luna | Anthropic, OpenAI | API | `init_chat_model` + `with_structured_output` | baseline "LLM decidindo" |

O Laya fala o **mesmo esquema** do Jev. O SDK oficial do Jev conversa com ele trocando a `base_url`; é o que faz o `DecisionClient` do bloco atender os dois.

**O que dizer em voz alta sobre o Laya:** zero-shot, ele fica bem abaixo do Jev e dos LLMs no nosso golden set (o módulo 05 mede). O checkpoint multilíngue sai **sem calibração** de fábrica, segundo o próprio model card. Ele tem viés de posição em Score e contexto padrão de 1.024 tokens por pergunta. A tese do Laya é ajustar nos seus dados, e o módulo 07 faz isso.

**Citados, sem código:** NanoJev (Qwen3-0.6B), Kev (Qwen + LoRA), OpenJev, GLiNER2 e SemIf (logits de um LLM open-weight). O cenário muda em semanas. Consulte a lista comunitária [awesome-decision-models](https://github.com/sfmqrb/awesome-decision-models) (verificada em 12/10/2026) antes de escolher.

## Glossário

- **Modelo de decisão / System One Model:** modelo que devolve decisões tipadas com probabilidade, sem gerar texto.
- **Choice:** escolhe uma opção de uma lista. Devolve a opção, a confiança e a probabilidade de cada opção.
- **Noul:** a probabilidade de uma afirmação ser verdadeira. Uma pergunta de sim ou não.
- **Score:** um nível numa rubrica **ordenada**. Devolve a distribuição por nível e o valor esperado.
- **Noul × Score:** Noul é "isto é verdade?" (0 a 1). Score é "em que degrau desta escada?" (0, 1, 2...). Urgência é Score; "pede reembolso?" é Noul.
- **RLCD:** Reinforcement Learning for Calibrated Decisions, o treino que recompensa probabilidade honesta. O RLHF dos LLMs de chat recompensa a resposta que agrada.
- **Calibração:** entre cem respostas com 74% de confiança, cerca de 74 estão certas.
- **Golden set:** exemplos rotulados que servem de verdade para medir.
- **Replay:** execução a partir de respostas gravadas, sem chamar APIs.

## Como rodar

Tudo roda **sem chave de API**, em modo replay (o padrão):

```bash
uv sync                              # da raiz do repositório
cd 06-decision-models
python 02-choice-routing/01_classify_tickets.py
uv run pytest tests -q               # testes do common/ e smoke test de todos os scripts
```

Para chamar os modelos de verdade, configure o `.env` da raiz (veja o `.env.example`):

```bash
docker compose --profile decision up laya     # Laya em http://127.0.0.1:8001 (da raiz)
DECISION_PROVIDER=live python 02-choice-routing/01_classify_tickets.py
```

| Variável | Valores | Para quê |
|---|---|---|
| `DECISION_PROVIDER` | `replay` (padrão), `live`, `record` | de onde vêm as decisões |
| `DECISION_TARGETS` | ex. `jev,laya,llm:anthropic:claude-haiku-4-5-20251001` | alvos das comparações |
| `DECISION_LLM` | `provedor:modelo` | LLM de baseline |
| `TYPESAFE_API_KEY` | chave do Jev | modo live do Jev |
| `LAYA_BASE_URL` | `http://127.0.0.1:8001` | onde o Laya responde |

> No Windows, use `127.0.0.1` em vez de `localhost`: o `localhost` tenta IPv6 primeiro e cada chamada ao Laya leva cerca de 2 s a mais.

## ⚠️ Sobre as fixtures deste repositório

| Alvo | Origem das fixtures |
|---|---|
| Laya | **reais**: gravadas com `laya-serve` 0.4.6, checkpoint multilíngue, CPU, em 12/10/2026 |
| Claude Haiku 4.5 | **reais**: gravadas pela API da Anthropic em 12/10/2026 |
| Jev | **sintéticas**: geradas a partir dos rótulos do golden set com ruído determinístico, porque o repositório ainda não tem chave do Jev |
| GPT-5.6 Luna | sem gravação; disponível em modo live |

Os números do Jev em replay **não medem o Jev**: ilustram o formato. O replay avisa no terminal e as tabelas marcam "(sintético)". Grave as reais com `python 05-calibration-evaluation/05_replay_record.py --alvos jev`. Detalhes em [`fixtures/README.md`](./fixtures/README.md).

## Estrutura

```
06-decision-models/
├── common/                  # DecisionSpec, DecisionClient, providers, métricas, golden sets, specs
│   └── providers/           # jev_sdk (Jev e Laya), jev_langchain, llm, replay
├── data/                    # golden sets em português (tickets, spam, rerank, verify, sales, tool_calls)
├── fixtures/                # replay gravado: um diretório por alvo
├── laya/Dockerfile          # Laya em CPU para o docker-compose da raiz (perfil `decision`)
├── tests/                   # métricas, contratos, replay, golden sets e smoke test de cada script
└── 01-... a 07-...          # módulos: README + scripts NN_*.py
```

**Exceção consciente às regras da trilha:** os módulos deste bloco importam `common/`. Medir providers lado a lado só é justo com as mesmas métricas, os mesmos dados e o mesmo cliente. Nos demais blocos, a regra de "nada compartilhado" continua.

**Regra de ouro:** o mesmo `DecisionSpec` alimenta todos os providers; não existe prompt por modelo. Tokens vêm da resposta, latência do relógio e preço de [`common/pricing.yaml`](./common/pricing.yaml). Fora dos objetivos: afirmar que um provider é melhor. O bloco ensina a medir; a conclusão é sua, no seu caso.

## Referências

- [TypeSafe: documentação](https://docs.typesafe.ai/), [SDK Python](https://docs.typesafe.ai/sdk/python/), [primitivos](https://docs.typesafe.ai/primitives/choice)
- [langchain-typesafe](https://docs.langchain.com/oss/python/integrations/providers/typesafe)
- [Laya: documentação](https://nandhakishorm.github.io/laya/), [model card multilíngue](https://huggingface.co/convaiinnovations/laya-multilingual), [GitHub](https://github.com/NandhaKishorM/laya)
- [Guo et al. (2017). On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599)
- [Kahneman (2011). Rápido e Devagar: Duas Formas de Pensar](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow)
- [Repositório do workshop-jev](https://github.com/caio-moliveira/workshop-jev), a referência de implementação do projeto final

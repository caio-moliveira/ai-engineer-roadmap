# 🧭 Aula 1: Fundamentos de Modelos de Decisão

> **Objetivo:** entender o que é um modelo de decisão, fazer a primeira chamada, comparar com um LLM e ver a mesma decisão nos quatro modelos de decisão do mercado.
> **Pergunta-chave:** por que gerar texto para responder uma pergunta de múltipla escolha?

**Nesta aula:**

1. [O problema](#o-problema)
2. [O que é um modelo de decisão](#o-que-é-um-modelo-de-decisão)
3. [Os modelos do mercado](#os-modelos-do-mercado)
4. [Como é uma chamada](#como-é-uma-chamada)
5. [Preparação](#preparação) (chaves e Laya no Docker)
6. [Scripts](#scripts)
7. [O que observar](#o-que-observar)
8. [Referências](#referências)

Os slides da aula estão em [`apresentaoca.html`](../apresentaoca.html): abra no navegador, use as setas para navegar, `F` para tela cheia e `N` para as notas.

---

## O problema

Boa parte das chamadas de LLM num sistema de produção não gera texto para ninguém ler. Elas **decidem**:

- Para qual fila vai este ticket?
- Esta mensagem é spam?
- Qual tool o agente deve chamar?
- A resposta que o LLM escreveu inventou algum número?

Hoje a gente resolve isso com prompt e structured output: o LLM escreve um JSON com a resposta. Funciona, mas tem três custos:

1. **Tokens de saída.** O LLM gera o JSON token a token, e token de saída é o mais caro e o mais lento.
2. **Latência.** Gerar texto leva tempo, mesmo quando a resposta é uma palavra.
3. **Confiança inventada.** Se você pede "sua confiança de 0 a 1", o LLM escreve um número. Esse número é texto gerado, não uma probabilidade.

## O que é um modelo de decisão

Um modelo de decisão não gera texto. Ele recebe:

- um **estado**: o contexto da decisão (um ticket, uma mensagem, uma conversa);
- **perguntas tipadas**: o que você quer saber, com as respostas possíveis.

E devolve, para cada pergunta, **a probabilidade de cada resposta**.

```
LLM:               
prompt  ──►  gera "{"fila": "financeiro", "confianca": 0.95}"  (token a token)
Modelo de decisão: estado + pergunta  ──►  {financeiro: 0.97, tecnico: 0.01, comercial: 0.01, conta: 0.01}
```

A TypeSafe chama essa categoria de *System One Model*. O nome vem de Kahneman (*Rápido e Devagar*): o Sistema 1 é o pensamento rápido e intuitivo, o Sistema 2 é o lento e deliberado. O LLM faz o papel do Sistema 2: raciocina e escreve. O modelo de decisão faz o do Sistema 1: decide na hora.

## Os modelos do mercado

O Jev abriu a categoria em setembro de 2026. Em dois meses, vieram outros três:

| Modelo | Quem faz | Lançamento | Preço por 1M tokens de entrada | Pesos |
|---|---|---|---|---|
| **Jev** | TypeSafe AI | set 2026 | US$ 0,042 | fechados, só API |
| **Laya** | Convai Innovations | set 2026 | zero, roda na sua máquina | abertos, Apache 2.0 |
| **Decisions API** | OpenAI | out 2026 | US$ 0,10 | fechados, só API |
| **Gemini Decision 1** | Google | nov 2026 | US$ 0,10 | fechados, só API |

Nos três pagos, a saída é gratuita: não há texto para gerar. Os preços são de novembro de 2026.

No bloco, o **Jev** é o modelo de referência. O **Laya**, o **Gemini Decision 1** e a **OpenAI Decisions API** aparecem ao lado dele nos scripts das aulas 1 a 4.

## Como é uma chamada

No Jev, uma chamada é um `POST /v1/systemone` com o estado e as perguntas:

```json
{
  "model": "jev-latest",
  "state": {"ticket": "Fui cobrado duas vezes na fatura de setembro."},
  "questions": {
    "fila": {
      "type": "choice",
      "instructions": "Qual fila deve atender este ticket de suporte?",
      "criteria": {"financeiro": "cobranças e estornos", "tecnico": "erros no sistema", "comercial": "planos e preços", "conta": "senha e acesso"}
    }
  }
}
```

A resposta traz, para cada pergunta, a opção escolhida, a confiança e a distribuição completa, mais o uso de tokens:

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "fila": {"type": "choice", "choice": "financeiro", "confidence": 0.96,
             "probabilities": {"financeiro": 0.97, "tecnico": 0.01, "comercial": 0.01, "conta": 0.01}}
  },
  "usage": {"input_tokens": 112, "output_tokens": 0}
}
```

Nos scripts, usamos o SDK oficial (`typesafe-sdk`), que monta esse JSON, valida as perguntas e devolve objetos tipados.

### Os três tipos de pergunta

| Tipo | Pergunta | Resposta | Aula |
|---|---|---|---|
| **Choice** | "qual destas opções?" | a opção escolhida e a probabilidade de cada uma | [Aula 2](../02-choice) |
| **Noul** | "isto é verdade?" | a probabilidade de ser verdade, de 0 a 1 | [Aula 3](../03-noul) |
| **Score** | "em que nível desta escala?" | o valor esperado e a probabilidade de cada nível | [Aula 4](../04-score) |

Numa mesma chamada, você pode misturar os três tipos sobre o mesmo estado.

### Mesma ideia, nomes diferentes

Os quatro modelos fazem a mesma coisa. O que muda é o nome dos campos:

| | Jev e Laya | Gemini Decision 1 | OpenAI Decisions API |
|---|---|---|---|
| Dados de entrada | `state` | `input` | `input` |
| Pergunta de sim ou não | `noul` | `noul` | `predicate` |
| Opções do choice | `criteria` (dicionário) | `criteria` (dicionário) | `choices` (lista de `{value, description}`) |
| Níveis do score | `criteria` (lista) | `criteria` (lista) | `levels` (lista de `{label, description}`) |

O Laya fala a mesma API do Jev: é o mesmo SDK e o mesmo código, trocando só a `base_url`.

---

## Preparação

### 1. Dependências

Da raiz do repositório:

```bash
uv sync
```

### 2. Chaves no `.env`

Copie o `.env.example` da raiz para `.env` e preencha as chaves que tiver. Um provedor sem chave é pulado; os scripts não quebram.

| Variável | Para quê | Onde criar |
|---|---|---|
| `TYPESAFE_API_KEY` | Jev (scripts 01, 02 e 03) | [console.typesafe.ai](https://console.typesafe.ai) |
| `OPENAI_API_KEY` | GPT-6 Luna (script 02) e Decisions API (script 03) | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `ANTHROPIC_API_KEY` | Claude Sonnet 5.5 (script 02) | [console.anthropic.com](https://console.anthropic.com) |
| `GEMINI_API_KEY` | Gemini Decision 1 (script 03) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

### 3. Laya no Docker (opcional, só para o script 03)

O Laya roda na sua máquina, em CPU, sem chave. Você precisa do [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e aberto.

**Subir** (da raiz do repositório):

```bash
docker compose --profile decision up -d laya
```

Na primeira vez, o Docker monta a imagem e baixa o modelo (cerca de 1,3 GB). Leva alguns minutos. Nas próximas, sobe em segundos.

**Conferir se está no ar:**

```bash
curl http://127.0.0.1:8001/health
```

Se não responder, acompanhe a subida pelos logs:

```bash
docker compose --profile decision logs -f laya
```

**Desligar** quando terminar:

```bash
docker compose --profile decision stop laya
```

> No Windows, use `127.0.0.1` em vez de `localhost`: o `localhost` tenta IPv6 primeiro e cada chamada leva cerca de 2 s a mais.

Se o Laya não estiver no ar, o script 03 pula ele e segue com os outros.

---

## Scripts

| Script | O que mostra | Modelos |
|---|---|---|
| `01_first_decision.py` | a primeira chamada: a resposta bruta, a escolha, a confiança, os tokens e a latência | Jev |
| `02_jev_vs_llm.py` | a mesma pergunta num modelo de decisão e em dois LLMs | Jev, GPT-6 Luna, Claude Sonnet 5.5 |
| `03_decision_models.py` | a mesma pergunta nos quatro modelos de decisão | Jev, Laya, Gemini Decision 1, OpenAI Decisions API |

Rode da raiz do repositório:

```bash
uv run 06-decision-models/01-decision-fundamentals/01_first_decision.py
uv run 06-decision-models/01-decision-fundamentals/02_jev_vs_llm.py
uv run 06-decision-models/01-decision-fundamentals/03_decision_models.py
```

Os scripts 02 e 03 usam os mesmos três tickets e a mesma pergunta ("qual fila atende?"), e imprimem uma tabela por ticket com a probabilidade das quatro filas, os tokens e a latência de cada provedor.

Dois detalhes de implementação:

- **Script 02:** do lado do LLM, usamos `with_structured_output(..., method="json_schema")`. O JSON sai validado contra um schema Pydantic, que é o melhor que dá para fazer com um LLM.
- **Script 03:** o Gemini e a OpenAI são chamados por HTTP (`httpx`), porque as versões dos SDKs fixadas no repositório ainda não têm o endpoint de decisões. Isso deixa o JSON de cada requisição à vista no código.

## O que observar

**No script 02 (modelo de decisão × LLM):**

- **Tokens de saída:** o LLM gera dezenas de tokens por decisão. O modelo de decisão não gera texto.
- **Tokens de entrada:** os dois leem a pergunta e as opções. O LLM lê também o prompt e o schema do structured output.
- **Latência:** compare a média. A diferença cresce quando você faz dezenas de decisões por requisição.
- **Probabilidades:** no Jev, são a distribuição que o modelo calcula. No LLM, são números que ele escreveu no JSON: não dá para usá-los como probabilidade de verdade.

**No script 03 (modelos de decisão entre si):**

- **Resposta:** nos tickets fáceis, os quatro concordam. Nos ambíguos, a distribuição de cada um é diferente.
- **Tempo:** Jev, Gemini e OpenAI incluem a ida e volta pela internet. O Laya roda na sua máquina, sem rede.
- **Nomes:** compare as funções `ask_typesafe`, `ask_gemini` e `ask_openai`. A ideia é a mesma, os campos mudam.
- **Laya:** sem ajuste nos seus dados, ele costuma ficar abaixo dos outros. A força dele é outra: roda local, sem custo por chamada, e aceita fine-tune.

A resposta (a fila) costuma coincidir nos casos fáceis. Um modelo de decisão não existe para acertar mais que o LLM numa pergunta fácil: existe para tomar a mesma decisão mais barato, mais rápido e com uma probabilidade em que o código pode se apoiar.

---

## Referências

**Documentação dos modelos**

- [TypeSafe: documentação do Jev](https://docs.typesafe.ai/) e [SDK Python](https://docs.typesafe.ai/sdk/python/)
- [Laya: documentação](https://nandhakishorm.github.io/laya/), [model card](https://huggingface.co/convaiinnovations/laya-multilingual) e [GitHub](https://github.com/NandhaKishorM/laya)
- [Google: documentação da Gemini Decisions API](https://aistudio.google.com/docs/decisions-api)
- [OpenAI: guia da Decisions API](https://developers.openai.com/api/docs/guides/decisions) e [referência](https://developers.openai.com/api/reference/resources/decisions/methods/create)

**Anúncios de lançamento**

- [TypeSafe: Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [Google: Gemini Decisions API](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/)

**Para ir além**

- [Kahneman (2011). Rápido e Devagar: Duas Formas de Pensar](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow)
- [Wikipedia: Jev (AI model)](https://en.wikipedia.org/wiki/Jev_(AI_model))
- [Deußer et al.: avaliação independente do Jev em 37 datasets (arXiv 2609.37647)](https://arxiv.org/abs/2609.37647)

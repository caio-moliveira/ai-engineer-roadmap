# 🧭 Aula 1: Fundamentos de Modelos de Decisão

> **Objetivo:** entender o que é um modelo de decisão, conhecer o Jev e comparar uma decisão no Jev com a mesma decisão num LLM.
> **Pergunta-chave:** por que gerar texto para responder uma pergunta de múltipla escolha?

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

Um modelo de decisão (o mercado também chama de *System One Model*) não gera texto. Ele recebe:

- um **estado**: o contexto da decisão (um ticket, uma mensagem, uma conversa);
- **perguntas tipadas**: o que você quer saber, com as respostas possíveis.

E devolve, para cada pergunta, **a probabilidade de cada resposta**.

```
LLM:               prompt  ──►  gera "{"fila": "financeiro", "confianca": 0.95}"  (token a token)
Modelo de decisão: estado + pergunta  ──►  {financeiro: 0.97, tecnico: 0.01, comercial: 0.01, conta: 0.01}
```

O nome vem de Kahneman (*Rápido e Devagar*): o Sistema 1 é o pensamento rápido e intuitivo, o Sistema 2 é o lento e deliberado. O LLM faz o papel do Sistema 2: raciocina e escreve. O modelo de decisão faz o do Sistema 1: decide na hora.

## O Jev

O **Jev** é o modelo de decisão da TypeSafe AI, acessado por API. Uma chamada é um `POST /v1/systemone`:

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
    "fila": {"type": "choice", "choice": "financeiro", "confidence": 0.97,
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

## Scripts

| Script | O que mostra |
|---|---|
| `01_first_decision.py` | a primeira chamada ao Jev: escolha, probabilidades, tokens e latência |
| `02_jev_vs_llm.py` | a mesma pergunta em três tickets no Jev, no GPT-5.6 Luna e no Claude Sonnet 5.5, com tokens e latência de cada um |

```bash
python 06-decision-models/01-decision-fundamentals/01_first_decision.py
python 06-decision-models/01-decision-fundamentals/02_jev_vs_llm.py
```

O GPT-5.6 Luna e o Sonnet 5.5 são LLMs baratos e rápidos, a escolha comum para esse tipo de tarefa. Do lado do LLM, usamos `with_structured_output(..., method="json_schema")`: o JSON sai validado contra um schema Pydantic, que é o melhor que dá para fazer com um LLM.

## O que observar na comparação

- **Tokens de saída:** o LLM gera algumas dezenas por decisão. O Jev não gera texto; confira o número que a API devolve.
- **Tokens de entrada:** os dois leem a pergunta e as opções. O LLM lê também o prompt e o schema do structured output.
- **Latência:** compare a média. A diferença cresce quando você faz dezenas de decisões por requisição.
- **Confiança:** no Jev, é a probabilidade que o modelo atribui à resposta. No LLM, é um número que ele escreveu no JSON.

A resposta (a fila) costuma coincidir nos casos fáceis. Um modelo de decisão não existe para acertar mais que o LLM numa pergunta fácil: existe para tomar a mesma decisão mais barato, mais rápido e com uma probabilidade em que o código pode se apoiar.

---

## Referências

- [TypeSafe: documentação](https://docs.typesafe.ai/) e [SDK Python](https://docs.typesafe.ai/sdk/python/)
- [Kahneman (2011). Rápido e Devagar: Duas Formas de Pensar](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow)

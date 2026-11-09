# 🏁 Aula 6: Projeto Final, Agente de Atendimento Híbrido

> **Objetivo:** montar um agente em LangGraph em que o modelo de decisão decide e o LLM só escreve, medindo tokens e latência de cada etapa.
> **Pergunta-chave:** quantas das chamadas do seu agente precisam mesmo de um LLM?

---

## O agente

Um atendente de suporte de um software de gestão. Ele usa os três tipos de pergunta das aulas anteriores e os padrões da Aula 5:

```
guardrail ─┬─ bloqueada ─────────────────────────────────────────► fim
           └─ triagem ─┬─ humano (dúvida ou urgência alta) ──────► fim
                       └─ responder (LLM) ─► verificar ─┬─ aprovada ─► fim
                                                        └─ reprovada ─► fim (humano)
```

| Node | Quem faz | Perguntas | Decide |
|---|---|---|---|
| `guardrail` | Jev | 2 Nouls: injection, dado sensível | bloquear ou seguir |
| `triagem` | Jev | Choice (fila) + Score (urgência), numa chamada | responder sozinho ou chamar humano |
| `responder` | LLM | — | escreve a resposta com a base de conhecimento da fila |
| `verificar` | Jev | 2 Nouls: responde a mensagem? inventa dado? | enviar ou reter para um humano |

Numa mensagem respondida, são quatro chamadas: três decisões e uma geração. Numa mensagem bloqueada, uma só, e o LLM nem é chamado.

## Arquivos

| Arquivo | O que tem |
|---|---|
| `graph.py` | configuração e limiares, perguntas, base de conhecimento, nodes e o `StateGraph` |
| `main.py` | roda as mensagens de exemplo (ou a sua) e imprime destino, resposta, tokens e latência de cada etapa |

## Como rodar

Os imports são flat: rode **de dentro da pasta**.

```bash
cd 06-decision-models/06-final-project
python main.py                                  # cinco mensagens de exemplo
python main.py "Fui cobrado duas vezes"         # a sua mensagem
DECISION_BACKEND=laya python main.py            # decisões no Laya local (Aula 5)
LLM_MODEL=openai:gpt-5.6-luna python main.py    # outro LLM para escrever
```

| Variável | Padrão | Para quê |
|---|---|---|
| `DECISION_BACKEND` | `jev` | `jev` (precisa de `TYPESAFE_API_KEY`) ou `laya` (precisa do Laya rodando) |
| `LLM_MODEL` | `anthropic:claude-sonnet-5-5` | o LLM que escreve as respostas, no formato do `init_chat_model` |

No fim, o `main.py` soma as chamadas de decisão e as de geração: quantas foram, tokens de entrada e de saída e latência média de cada grupo.

## O que observar

- **Onde o tempo vai:** compare a latência média das decisões com a da geração.
- **Onde os tokens de saída vão:** só a geração produz texto.
- **O que nem chega ao LLM:** mensagens bloqueadas e encaminhadas a humano não geram nenhum token de saída.
- **Jev × Laya:** rode com os dois backends e compare destinos e vereditos. O Laya zero-shot tende a ser mais severo na verificação; é aí que os limiares (no topo do `graph.py`) e um eventual fine-tune entram.

---

## 📦 Entregáveis

Adapte o agente ao seu domínio:

1. **Troque o domínio:** as filas, a base de conhecimento e as mensagens de exemplo.
2. **Ajuste as perguntas:** pelo menos um Choice, um Noul e um Score, com `criteria` que reflitam as regras do seu negócio.
3. **Justifique os limiares:** para cada limiar, escreva o que acontece quando ele erra para cima e para baixo.
4. **Compare:** rode as mesmas mensagens com o Jev e com o Laya, e com dois LLMs diferentes, e registre tokens, latência e destinos numa tabela.
5. **Responda à pergunta-chave:** do total de chamadas do seu agente, quantas precisaram de um LLM?

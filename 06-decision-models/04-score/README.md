# 📊 Aula 4: Score

> **Objetivo:** usar o Score para posicionar um estado numa rubrica ordenada e ordenar itens pelo valor esperado.
> **Pergunta-chave:** como transformar "quão urgente é isto?" num número que ordena uma fila?

---

## O que é um Score

Um Score é uma rubrica com **níveis em ordem**. O `criteria` é uma lista, e a posição de cada item é o nível (0, 1, 2...):

```python
from typesafe_sdk import Score

urgencia = Score(
    instructions="Qual a urgência deste ticket de suporte?",
    criteria=[
        "pode esperar: dúvida ou pedido sem prazo",               # nível 0
        "esta semana: problema que incomoda, mas tem contorno",   # nível 1
        "hoje: cliente bloqueado ou cobrado indevidamente",       # nível 2
        "agora: sistema fora do ar para muitos usuários",         # nível 3
    ],
)
```

A resposta:

| Campo | Exemplo | Para quê |
|---|---|---|
| `probabilities` | `{"0": 0.05, "1": 0.10, "2": 0.70, "3": 0.15}` | a probabilidade de cada nível |
| `score` | `1.95` | o **valor esperado**: soma de nível × probabilidade |
| `confidence` | `0.70` | a confiança da resposta |

## Valor esperado

O valor esperado é o que torna o Score útil para ordenar. Dois tickets com o mesmo nível mais provável podem ter valores esperados diferentes: um com 30% de chance de ser nível 3, outro com 30% de chance de ser nível 1. Ordenando pelo `score`, o primeiro passa na frente.

## Score ou Choice?

| Use **Score** quando | Use **Choice** quando |
|---|---|
| as opções têm ordem (baixa < média < alta) | as opções são categorias sem ordem (financeiro, técnico) |
| errar por um nível é melhor que errar por três | todo erro custa o mesmo |
| você quer ordenar ou comparar itens | você quer escolher um destino |

E o Noul (Aula 3)? Noul é "isto é verdade?". Score é "em que degrau desta escada?". "Pede reembolso?" é Noul; "quão urgente?" é Score.

## Onde o Score aparece

- **Priorização:** urgência de tickets, severidade de incidentes, risco de churn.
- **Rerank de RAG:** relevância de cada trecho para a pergunta, para mandar ao LLM só os melhores.
- **Avaliação de qualidade:** nota de uma resposta de LLM numa rubrica, como um juiz barato.

## Scripts

| Script | O que mostra |
|---|---|
| `01_urgency.py` | urgência de seis tickets, com a distribuição por nível e a fila ordenada pelo valor esperado |
| `02_rerank.py` | rerank de seis trechos de um RAG pela relevância para a pergunta |

```bash
python 06-decision-models/04-score/01_urgency.py
python 06-decision-models/04-score/02_rerank.py
```

No rerank, cada trecho é uma chamada. O script soma tokens e latência de todas. Em produção, use o cliente assíncrono do SDK (`AsyncTypeSafeClient`) e faça as chamadas em paralelo.

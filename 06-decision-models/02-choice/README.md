# 🔀 Aula 2: Choice

> **Objetivo:** usar o Choice para escolher uma opção de uma lista e decidir em código com a confiança.
> **Pergunta-chave:** quantas vezes o seu agente lê a descrição de todas as tools só para escolher uma?

---

## O que é um Choice

Um Choice é uma pergunta de múltipla escolha: "qual destas opções?". Você define as opções no `criteria`, cada uma com uma descrição do que ela cobre:

```python
from typesafe_sdk import Choice

fila = Choice(
    instructions="Qual fila deve atender este ticket de suporte?",
    criteria={
        "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
        "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
        "comercial": "planos, preços, descontos, contratação e demonstrações",
        "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
    },
)
```

A resposta tem três campos:

| Campo | Exemplo | Para quê |
|---|---|---|
| `choice` | `"financeiro"` | a opção mais provável |
| `confidence` | `0.97` | a probabilidade da opção escolhida |
| `probabilities` | `{"financeiro": 0.97, "tecnico": 0.01, ...}` | a distribuição completa, que soma 1 |

As descrições no `criteria` importam: são elas que dizem ao modelo onde termina uma opção e começa a outra. Opções com fronteira confusa geram confiança baixa.

## Decidir com a confiança

A confiança é o que transforma uma classificação em automação:

```python
answer = response.choices["fila"]
if answer.confidence >= 0.80:
    encaminhar(answer.choice)      # automático
else:
    revisao_humana(ticket)         # o modelo está em dúvida
```

O limiar é decisão de negócio: quanto custa errar e quanto custa a revisão humana. Limiar alto automatiza menos e erra menos.

## Onde o Choice aparece

- **Roteamento:** fila de atendimento, departamento, idioma, intenção do usuário.
- **Escolha de tool:** o catálogo de tools vira o `criteria`, e o seu código executa a escolhida.
- **Roteamento de modelo:** "esta pergunta precisa do modelo caro ou o barato resolve?".

## Scripts

| Script | O que mostra |
|---|---|
| `01_ticket_routing.py` | seis tickets roteados, com limiar de confiança para revisão humana |
| `02_tool_selection.py` | o Choice escolhe a tool do agente de vendas, e o código a executa |

```bash
python 06-decision-models/02-choice/01_ticket_routing.py
python 06-decision-models/02-choice/02_tool_selection.py
```

Os dois mostram tokens de entrada e latência de cada chamada.

## Choice × function calling

| | Function calling (LLM) | Choice (modelo de decisão) |
|---|---|---|
| Quem decide a tool | o LLM, gerando a chamada | o modelo, devolvendo uma distribuição |
| Quem executa | o framework, com os argumentos que o LLM gerou | o seu código |
| Tool inexistente ou argumento inventado | pode acontecer | não acontece: a resposta é sempre uma das opções |
| Confiança | não tem | tem, e você usa para decidir |
| Argumentos da tool | gerados junto com a escolha | precisam de outra etapa (código ou LLM) |

A última linha é o limite do Choice: ele escolhe, não extrai. Se a tool precisa do número do pedido, alguém tem que tirar o número do texto.

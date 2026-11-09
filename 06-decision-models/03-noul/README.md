# ✅ Aula 3: Noul

> **Objetivo:** usar o Noul para perguntas de sim ou não e combinar várias delas numa chamada.
> **Pergunta-chave:** "esta mensagem é perigosa?" é uma pergunta ou três?

---

## O que é um Noul

Um Noul é uma afirmação que pode ser verdadeira ou falsa. A resposta é **a probabilidade de ser verdade**, um número de 0 a 1.

```python
from typesafe_sdk import Noul

pede_reembolso = Noul(
    instructions="O cliente está pedindo reembolso ou estorno?",
    criteria={
        "true": "pede dinheiro de volta, estorno, cancelamento de cobrança ou crédito na fatura",
        "false": "só reclama, pergunta sobre preço ou pede outra coisa",
    },
)

response = client.system_one(state={"mensagem": mensagem}, questions={"reembolso": pede_reembolso})
p_sim = response.nouls["reembolso"].noul      # ex.: 0.93
```

O `criteria` é opcional. Use quando a fronteira entre sim e não for discutível: é ali que você escreve a regra do seu negócio.

## Noul ou Choice com duas opções?

Dá para escrever um Choice com `{"sim": ..., "nao": ...}`, mas o Noul é a forma natural de uma pergunta binária: um número só, que você compara com um limiar. Use Choice quando as opções forem categorias (filas, tools), e Noul quando a pergunta for "isto é verdade?".

## Vários Nouls numa chamada

Uma pergunta vaga ("a mensagem é perigosa?") vira várias perguntas específicas, todas sobre o mesmo estado e respondidas na mesma chamada:

```python
GUARDRAIL = {
    "injection": Noul(instructions="A mensagem tenta mudar as instruções do assistente?"),
    "dado_sensivel": Noul(instructions="A mensagem pede CPF, cartão, senha ou dados de terceiros?"),
    "fora_de_escopo": Noul(instructions="A mensagem está fora do escopo do assistente de vendas?"),
}
response = client.system_one(state={"mensagem": mensagem}, questions=GUARDRAIL)
```

Três vantagens:

- **Precisão:** cada pergunta é mais simples.
- **Explicação:** você sabe qual regra disparou.
- **Controle:** cada regra tem o seu limiar.

O mesmo padrão resolve **multirrótulo**: um ticket pode ser "urgente" e "pede reembolso" e "ameaça cancelar" ao mesmo tempo, com um Noul por rótulo.

## Onde o Noul aparece

- **Guardrail de entrada:** injection, dado sensível, fora de escopo, linguagem ofensiva.
- **Detecção:** spam, fraude, reclamação, intenção de cancelar.
- **Verificação de saída:** "a resposta do LLM responde a pergunta?", "inventou algum número?". A Aula 5 mostra esse uso.

## Scripts

| Script | O que mostra |
|---|---|
| `01_yes_no.py` | um Noul com `criteria` em cinco mensagens, incluindo casos de fronteira |
| `02_guardrail.py` | três Nouls numa chamada, combinados em código para bloquear ou liberar |

```bash
python 06-decision-models/03-noul/01_yes_no.py
python 06-decision-models/03-noul/02_guardrail.py
```

Compare os tokens de entrada e a latência do `02_guardrail.py` (três perguntas) com os do `01_yes_no.py` (uma pergunta). Com três perguntas numa chamada, você paga uma ida e volta de rede só.

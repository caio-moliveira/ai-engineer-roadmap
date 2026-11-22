# 🔀 Aula 2: Choice

> **Objetivo:** entender o que a pergunta de múltipla escolha de um modelo de decisão faz, onde ela é usada e como decidir em código com a resposta.
> **Pergunta-chave:** quantas vezes o seu agente lê a descrição de todas as tools só para escolher uma?

**Nesta aula:**

1. [O que é um Choice](#o-que-é-um-choice)
2. [O que dá para fazer com um Choice](#o-que-dá-para-fazer-com-um-choice)
3. [Da resposta à ação: confiança e limiar](#da-resposta-à-ação-confiança-e-limiar)
4. [Como escrever boas opções](#como-escrever-boas-opções)
5. [Além de um Choice só](#além-de-um-choice-só)
6. [Scripts](#scripts)
7. [Referências](#referências)

Os slides da aula estão em [`apresentaoca.html`](../apresentaoca.html), do slide 15 ao 19 ("Aula 2 · Choice").

---

## O que é um Choice

Um Choice é uma pergunta de múltipla escolha: "qual destas opções?". Você manda a entrada, a pergunta e as opções. O modelo não escreve nada: devolve a probabilidade de cada opção.

```
O que você manda                                   O que volta

entrada:  "Fui cobrado duas vezes pelo pedido."     escolha:   faturamento
pergunta: "Qual área atende esta reclamação?"       confiança: 0.93
opções:                                             probabilidades:
  faturamento: "pagamentos, faturas, reembolsos"      faturamento: 0.95
  tecnico:     "problemas no uso do produto"          tecnico:     0.02
  entrega:     "envio e rastreamento"                 outro:       0.02
  outro:       "pedidos fora dessas categorias"       entrega:     0.01
```

Voltam três coisas: a opção mais provável, a distribuição completa (que soma 1) e uma confiança. Um LLM com structured output devolveria só `"faturamento"`; aqui você vê quanta dúvida existe.

O Choice existe nos quatro modelos de decisão. Só os nomes mudam:

| | Jev e Laya | Gemini Decision 1 | OpenAI Decisions API |
|---|---|---|---|
| Tipo da pergunta | `choice` | `choice` | `choice` |
| Opções | `criteria` (dicionário nome → descrição) | `criteria` (dicionário nome → descrição) | `choices` (lista de `{value, description}`) |
| Máximo de opções | 255 | 255 | 255 |

No Jev e no Laya, pelo SDK, a pergunta fica assim:

```python
from typesafe_sdk import Choice

tipo = Choice(
    instructions="Que tipo de documento é este?",
    criteria={
        "contrato": "acordo assinado entre partes, com cláusulas, obrigações, prazo e foro",
        "nota_fiscal": "documento fiscal de venda ou serviço, com valores e impostos",
        "curriculo": "histórico profissional e formação de uma pessoa",
        "outro": "qualquer documento que não seja de um dos tipos acima",
    },
)
```

## O que dá para fazer com um Choice

Todo caso tem a mesma forma: uma lista fechada de saídas e um código que age sobre a escolha.

| Caso | Exemplo | Onde aparece |
|---|---|---|
| **Rotear atendimento** | uma reclamação vai para faturamento, técnico, entrega ou outro | documentação da OpenAI e do Google |
| **Escolher a tool do agente** | um comando em texto vira uma entre dez funções, e o código executa a escolhida | cookbook da TypeSafe |
| **Rotear o modelo** | cada pergunta vai para o modelo barato ou para o caro; o Gemini Notebook relata até 40% menos latência | anúncio do Google |
| **Decidir a próxima ação** | um ticket de defeito vira reembolso, troca, guia de solução ou atendimento humano | documentação do Google |
| **Classificar documentos** | o PDF de uma fatura vira uma categoria de despesa; um relatório anual vira um entre 75 setores | documentação do Google, cookbook da TypeSafe |
| **Escolher entre centenas** | uma reação de emoji entre mais de 200 opções | CC, do Google Labs |

Nos scripts da aula fazemos dois desses casos, nos quatro modelos: classificar documentos e escolher a tool de um agente.

## Da resposta à ação: confiança e limiar

O modelo dá a evidência. Quem decide o que fazer com ela é o seu código:

```python
answer = response.choices["fila"]
if answer.confidence >= LIMIAR:
    encaminhar(answer.choice)      # automático
else:
    revisao_humana(ticket)         # o modelo está em dúvida
```

Três cuidados:

1. **O limiar é seu.** Não existe valor padrão. As três documentações dizem o mesmo: escolha com exemplos rotulados do seu tráfego, pesando o custo de cada tipo de erro. Limiar alto automatiza menos e erra menos.
2. **Confiança muda de modelo para modelo.** Um limiar ajustado num modelo não vale no outro:

   | Modelo | O que é a `confidence` de um choice |
   |---|---|
   | Gemini Decision 1 | a probabilidade da opção escolhida |
   | Jev | o quanto essa probabilidade está acima do chute: `(p_max − 1/n) / (1 − 1/n)` |
   | OpenAI Decisions API | a documentação não diz como é calculada |

   No Jev, com quatro opções, 0,25 vale confiança 0 (chute), 0,55 vale 0,40 e 1,00 vale 1.
3. **Olhe a distribuição.** 0,55 contra 0,44 é dúvida entre duas opções, não erro. A confiança só usa a maior probabilidade; a distância para a segunda opção está em `probabilities`.

## Como escrever boas opções

As opções são o seu prompt. Quatro regras em que OpenAI, Google e TypeSafe concordam:

1. **Nome com significado e descrição curta.** O modelo lê os dois. Prefira `"faturamento"` a um código; mudar o nome muda o resultado.
2. **Inclua `"outro"`.** As probabilidades somam 1 mesmo quando nada serve. Sem uma saída, o modelo escolhe a opção menos errada.
3. **Ou pergunte antes.** Uma pergunta de sim ou não na mesma chamada ("esta mensagem é sobre um pedido?"). O código só lê o Choice se a resposta for sim.
4. **Desconfie da entrada.** O texto do usuário pode argumentar a favor da própria classificação. Em ações de alto risco, mantenha uma pessoa na revisão.

Confiança baixa costuma apontar uma fronteira mal escrita entre duas opções. Antes de culpar o modelo, olhe a segunda opção mais provável.

## Além de um Choice só

- **Várias perguntas na mesma chamada.** Um Choice, perguntas de sim ou não e uma nota sobre a mesma entrada. As perguntas são independentes e a entrada é cobrada uma vez só. Num cookbook da TypeSafe, treze perguntas juntas custaram 12 vezes menos que treze chamadas.
- **Em cadeia.** Para uma árvore de categorias, um Choice por nível: primeiro a área, depois a subárea.
- **Em duas etapas.** Quando uma decisão depende da outra, são duas chamadas: primeiro "há defeito?", depois "qual o reparo?".

**O que o Choice não faz:**

- **Não extrai texto livre.** Ele escolhe a tool `status_do_pedido`, mas não tira o número do pedido do texto. Isso é outra etapa: código ou LLM.
- **Não marca duas opções ao mesmo tempo.** Se o ticket é financeiro e também urgente, são perguntas diferentes.

O Choice responde "qual". Quando a pergunta é "isto é verdade?", o tipo certo é o Noul, tema da [Aula 3](../03-noul).

---

## Scripts

Os dois scripts fazem a mesma pergunta aos quatro modelos de decisão (Jev, Laya, Gemini Decision 1 e OpenAI Decisions API) e mostram, lado a lado, a escolha, a probabilidade, os tokens de entrada e a latência.

| Script | O que mostra |
|---|---|
| `01_document_classification.py` | classifica seis documentos por tipo e depois manda o mesmo relatório em três tamanhos (1, 10 e 33 páginas), para mostrar o custo e o limite de entrada de cada modelo |
| `02_tool_selection.py` | o Choice escolhe uma entre dez tools de um agente de e-commerce, e o código executa a escolhida |

Rode da raiz do repositório:

```bash
python 06-decision-models/02-choice/01_document_classification.py
python 06-decision-models/02-choice/02_tool_selection.py
```

**O que precisa estar configurado** (igual ao script 03 da [Aula 1](../01-decision-fundamentals#preparação)):

- `TYPESAFE_API_KEY`, `GEMINI_API_KEY` e `OPENAI_API_KEY` no `.env` da raiz. Um provedor sem chave é pulado.
- O Laya no ar, se quiser vê-lo na comparação: `docker compose --profile decision up -d laya`.

Os scripts comparam os modelos pela **probabilidade da opção escolhida**, e não pelo campo de confiança, porque a probabilidade significa o mesmo nos quatro.

### Script 01: classificar documentos

Uma esteira de entrada recebe documentos e precisa saber o tipo de cada um. Os documentos ficam em [`docs/`](./docs):

| Arquivo | O que é |
|---|---|
| `contrato_prestacao_servicos.txt` | contrato de desenvolvimento de software |
| `nota_fiscal_servico.txt` | nota fiscal de serviço eletrônica |
| `curriculo.txt` | currículo de uma engenheira de dados |
| `ata_reuniao.txt` | ata de reunião de projeto |
| `proposta_comercial.txt` | proposta comercial, que não tem tipo próprio na lista |
| `relatorio_mudancas_climaticas.pdf` | relatório de 33 páginas, em inglês |

Os cinco textos são fictícios, escritos para a aula. O PDF é o mesmo usado no bloco de RAG.

**Parte 1: seis documentos, só o começo.** O script manda os primeiros 3.000 caracteres de cada um. O que observar:

- **Documentos típicos:** Jev, Gemini e OpenAI acertam com probabilidade perto de 1.
- **A proposta comercial:** não tem tipo próprio e se parece com um contrato. Os modelos por API mandam para `outro`. É para isso que a opção existe.
- **O Laya:** sem ajuste nos seus dados, erra alguns (na nossa execução, classificou o currículo como relatório técnico) e fica em dúvida em outros.

**Parte 2: o mesmo relatório em três tamanhos (1, 10 e 33 páginas).** O que observar:

- **A resposta não muda, a conta muda.** Com 1 página ou com as 33, o tipo é o mesmo. Os tokens de entrada vão de cerca de 700 para cerca de 14.000, e o custo cresce junto.
- **Cada modelo tem um limite de entrada diferente.** O relatório inteiro tem cerca de 14 mil tokens:

  | Modelo | Com o relatório inteiro | Limite de entrada |
  |---|---|---|
  | Jev | responde | 32 mil tokens de estado |
  | Laya | recusa: aceita até 50 mil caracteres, e mesmo abaixo disso lê só os primeiros 1.024 tokens | 1.024 tokens |
  | Gemini Decision 1 | responde | 262 mil tokens (a conta gratuita limita a 50 mil tokens por minuto) |
  | OpenAI Decisions API | responde | a documentação não informa um limite em tokens |

- **Para classificar, quase nunca é preciso mandar tudo.** O começo do documento costuma bastar, e custa 20 vezes menos.

### Script 02: escolher a tool do agente

O catálogo de dez tools de um agente de e-commerce vira as opções do Choice, mais uma opção `"nenhuma"`. O que observar:

- **Quem executa a tool é o seu código**, a partir de uma escolha com probabilidade, e só acima do limiar.
- **Pedidos claros:** os modelos por API escolhem a mesma tool, com probabilidade alta.
- **Opções que se sobrepõem:** "Meu pedido já saiu para entrega?" divide os modelos entre `status_do_pedido` e `rastrear_entrega`. As duas descrições cobrem o mesmo caso, e a probabilidade se divide.
- **Dois pedidos numa frase:** "quanto custa e quanto fica o frete?" pede duas tools. O Choice devolve uma só, com probabilidade baixa.
- **O Laya com onze opções:** sem ajuste, ele escolhe quase sempre a mesma tool, com probabilidade perto de 1. Probabilidade alta só vale alguma coisa depois de medida nos seus exemplos.
- **O pedido de CPF** cai em `"nenhuma"`, mas não deveria chegar até aqui: barrar dado sensível é trabalho de um guardrail com Nouls ([Aula 3](../03-noul)).

### Choice × function calling

| | Function calling (LLM) | Choice (modelo de decisão) |
|---|---|---|
| Quem escolhe a tool | o LLM, gerando a chamada | o modelo, devolvendo uma distribuição |
| Quem executa | o framework, com os argumentos que o LLM gerou | o seu código |
| Tool inexistente ou argumento inventado | pode acontecer | não acontece: a resposta é sempre uma das opções |
| Confiança | não tem | tem, e você usa para decidir |
| Argumentos da tool | gerados junto com a escolha | precisam de outra etapa (código ou LLM) |

### Exercícios

1. Tire a opção `"outro"` do script 01 e veja para onde vai a proposta comercial.
2. Reescreva as descrições de `status_do_pedido` e `rastrear_entrega` no script 02 até os modelos concordarem.
3. Mude o `INICIO` do script 01 para 500 caracteres e veja se a classificação muda.

---

## Referências

**Documentação do choice em cada modelo**

- [OpenAI: guia da Decisions API](https://developers.openai.com/api/docs/guides/decisions)
- [Google: Gemini Decisions API](https://aistudio.google.com/docs/decisions-api)
- [TypeSafe: o primitivo Choice](https://docs.typesafe.ai/primitives/choice) e [como a confiança é calculada](https://docs.typesafe.ai/confidence)

**Casos de uso**

- [Google: anúncio da Gemini Decisions API](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/) (Gemini Notebook, CC)
- [TypeSafe: escolha de função e argumentos](https://docs.typesafe.ai/cookbooks/function_calling.md)
- [TypeSafe: classificação com confiança (75 setores)](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md)
- [TypeSafe: classificação hierárquica](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md)
- [TypeSafe: várias perguntas na mesma chamada](https://docs.typesafe.ai/cookbooks/parallel_questions.md)

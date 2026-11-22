# 📊 Aula 4: Score

> **Objetivo:** usar a pergunta de "quanto" de um modelo de decisão para posicionar uma entrada numa escala ordenada, e ordenar, cortar ou somar com o resultado.
> **Pergunta-chave:** como transformar "quão bom é este candidato?" em números que ordenam uma fila?

**Nesta aula:**

1. [O que é um Score](#o-que-é-um-score)
2. [O que dá para fazer com um Score](#o-que-dá-para-fazer-com-um-score)
3. [O score é uma média](#o-score-é-uma-média)
4. [Como escrever uma boa escala](#como-escrever-uma-boa-escala)
5. [Os três tipos, lado a lado](#os-três-tipos-lado-a-lado)
6. [Scripts](#scripts)
7. [Referências](#referências)

Os slides da aula estão em [`apresentaoca.html`](../apresentaoca.html), do slide 25 ao 29 ("Aula 4 · Score").

---

## O que é um Score

Um Score é uma pergunta de "quanto". Você manda a entrada e uma escala com **níveis em ordem**, do mais baixo para o mais alto. O modelo devolve a probabilidade de cada nível e um número que resume a posição na escala.

```
O que você manda                                      O que volta

entrada:  "A exportação falha no Safari,              score: 1.12
           mas funciona no Chrome."                   probabilidades:
pergunta: "Qual a gravidade deste bug?"                 0 cosmético:      0.03
níveis:                                                 1 tem contorno:   0.83
  0  cosmético                                          2 bloqueia o uso: 0.15
  1  tem contorno
  2  bloqueia o uso
```

(Exemplo e números da documentação do Google. A TypeSafe e a OpenAI usam o mesmo relato de bug.)

É o tipo mais parecido entre as APIs: nas três, os índices começam em 0 e o `score` é calculado do mesmo jeito.

| | Jev e Laya | Gemini Decision 1 | OpenAI Decisions API |
|---|---|---|---|
| Tipo da pergunta | `score` | `score` | `score` |
| Níveis | `criteria`: lista de descrições | `criteria`: lista de descrições | `levels`: lista de `{label, description}` |
| Quantos níveis | 2 a 10 | 2 a 255 (recomenda 2 a 10) | 2 a 10 |
| Probabilidades | dicionário por índice | dicionário por índice | lista de `{value, label, probability}` |
| Campo de confiança | fórmula de distância entre níveis | a probabilidade do nível mais provável | existe, mas a conta não é documentada |

No Jev e no Laya, pelo SDK, a pergunta fica assim:

```python
from typesafe_sdk import Score

gravidade = Score(
    instructions="Qual a gravidade deste bug?",
    criteria=[
        "cosmético: não atrapalha o uso",            # nível 0
        "tem contorno: algo falha, mas há outro caminho",  # nível 1
        "bloqueia o uso: não há como seguir",        # nível 2
    ],
)
response = client.system_one(state={"relato": relato}, questions={"gravidade": gravidade})
nota = response.scores["gravidade"].score
```

## O que dá para fazer com um Score

Todo caso tem a mesma forma: uma escala com ordem e um código que ordena, corta ou soma.

| Caso | Exemplo | Onde aparece |
|---|---|---|
| **Ordenar candidatos** | seis currículos para uma vaga, três escalas por currículo, uma nota final com pesos | script 01 desta aula |
| **Reordenar uma busca** | cada trecho que o retriever trouxe recebe uma nota de relevância | documentação do Google, cookbook da TypeSafe |
| **Julgar respostas** | a resposta do assistente é fiel ao contexto? cobre a pergunta inteira? | script 02 desta aula |
| **Medir gravidade** | um relato de bug vai de cosmético a bloqueante | documentação das três APIs |
| **Medir risco** | a mensagem do cliente vai de "sem sinal" a "ameaça cancelar" | documentação do Google |
| **Montar uma nota composta** | gravidade, frustração e qualidade do relato, somadas com pesos no código | documentação da TypeSafe |

## O score é uma média

O `score` soma cada nível multiplicado pela sua probabilidade. Por isso ele pode cair entre dois níveis.

Um exemplo do script 01, com a escala de autonomia (0 apoiado, 1 independente, 2 referência) para um engenheiro que "mantém sozinho 30 pipelines em produção":

| Modelo | 0 apoiado | 1 independente | 2 referência | score | nível mais provável |
|---|---|---|---|---|---|
| Jev | 0% | 98% | 2% | 1,02 | 1 independente |
| Gemini Decision 1 | 3% | 60% | 37% | 1,34 | 1 independente |
| Laya | 6% | 44% | 50% | 1,44 | 2 referência |

A conta do Gemini: 0 × 0,03 + 1 × 0,60 + 2 × 0,37 = 1,34. O número diz que o modelo ficou dividido entre dois níveis.

Três regras práticas:

1. **Para ordenar ou cortar, use o `score`.** Ele é contínuo e separa itens que caem no mesmo nível.
2. **Para agir sobre um nível, use o mais provável** e confira a distribuição. Distribuições diferentes podem dar o mesmo `score`.
3. **Para comparar modelos, use o `score`,** dividido pelo nível máximo quando as escalas têm tamanhos diferentes. O campo de confiança muda de modelo para modelo.

## Como escrever uma boa escala

1. **Descreva situações, não graus.** "Construiu pipelines em produção" em vez de "experiência alta". O modelo lê a descrição, não o número do nível.
2. **Níveis vizinhos bem distintos.** Se dois níveis descrevem quase a mesma coisa, a probabilidade se divide entre eles.
3. **Degraus do mesmo tamanho.** O `score` usa os índices 0, 1, 2, 3. Uma escala que pula de "10" para "1.000" distorce a média.
4. **Uma dimensão por escala.** Experiência e autonomia são duas perguntas. Quem junta as duas é o código, com pesos.

Num teste da documentação da TypeSafe, níveis escritos só como "0", "1" e "2" deixaram o modelo em dúvida (score 0,55, confiança 0,33). Com os níveis descritos, a mesma entrada saiu com score 0,0 e confiança 1,0.

Não existe "não se aplica": as probabilidades sempre somam 1, mesmo quando nenhum nível serve.

## Os três tipos, lado a lado

| | Choice | Noul | Score |
|---|---|---|---|
| A pergunta | qual destas? | isto é verdade? | quanto? |
| O que volta | uma probabilidade por opção | a probabilidade de sim | uma probabilidade por nível e o score |
| O que comparar entre modelos | a probabilidade da opção escolhida | a probabilidade de sim | o score, dividido pelo nível máximo |
| O que o código faz | roteia, com um limiar | bloqueia, libera ou manda revisar | ordena, corta ou soma com pesos |
| Nos scripts | classificar documentos, escolher a tool | checklist, guardrail, auditoria de edital | ranking de currículos, juiz de respostas |

Três erros comuns:

- **Pergunta de grau escrita como Noul.** "O candidato é forte em Python?" é quanto, não sim ou não.
- **Opções com ordem escritas como Choice.** Se baixa, média e alta têm ordem, use um Score.
- **Duas dimensões numa escala só.** Separe em duas perguntas e combine no código.

---

## Scripts

Os dois scripts fazem as mesmas perguntas aos quatro modelos de decisão (Jev, Laya, Gemini Decision 1 e OpenAI Decisions API) e mostram, lado a lado, o score, os tokens de entrada e a latência.

| Script | O que mostra |
|---|---|
| `01_resume_ranking.py` | seis currículos ranqueados para uma vaga, com três escalas e uma nota final com pesos |
| `02_answer_judge.py` | cinco respostas de um assistente julgadas em fidelidade e completude |

Rode da raiz do repositório:

```bash
python 06-decision-models/04-score/01_resume_ranking.py
python 06-decision-models/04-score/02_answer_judge.py
```

**O que precisa estar configurado** (igual ao script 03 da [Aula 1](../01-decision-fundamentals#preparação)):

- `TYPESAFE_API_KEY`, `GEMINI_API_KEY` e `OPENAI_API_KEY` no `.env` da raiz. Um provedor sem chave é pulado.
- O Laya no ar, se quiser vê-lo na comparação: `docker compose --profile decision up -d laya`.

### Script 01: ranking de currículos

O RH recebeu seis currículos para uma vaga de engenharia de dados. A vaga e os currículos estão em [`docs/`](./docs) e são fictícios, escritos para a aula.

Em vez de perguntar "o candidato é bom?", o script faz três perguntas de "quanto" na mesma chamada:

| Escala | Níveis | Peso na nota final |
|---|---|---|
| `experiencia` | nenhuma, ao redor, inicial, em produção (0 a 3) | 0,5 |
| `stack` | nada, pouco, boa parte, tudo (0 a 3) | 0,3 |
| `autonomia` | apoiado, independente, referência (0 a 2) | 0,2 |

O código divide cada score pelo nível máximo da escala, aplica os pesos e ordena. O que observar:

- **O modelo não diz quem é o melhor.** Ele dá três scores por currículo. A nota final e os pesos são regra do código: mude os pesos e o ranking muda, sem chamar o modelo de novo.
- **Jev, Gemini e OpenAI chegaram ao mesmo ranking** na nossa execução: a engenheira sênior, o engenheiro pleno, a estagiária de dados, o desenvolvedor backend, a analista de BI e o designer.
- **O designer tem autonomia alta** (ele coordena campanhas) e fica em último, porque o peso está na experiência com dados. É a vantagem de separar as dimensões.
- **O Laya, sem ajuste nos seus dados,** deu notas parecidas para todos (entre 0,69 e 0,82) e colocou o designer em terceiro.
- **O zoom no fim** mostra a probabilidade de cada nível por trás de um score.

### Script 02: juiz de respostas

Um assistente de RAG respondeu a uma pergunta sobre o edital. Antes de a resposta ir para o usuário, um modelo de decisão dá duas notas, de 0 a 2:

| Critério | Níveis |
|---|---|
| `fidelidade` | contradiz o contexto, acrescenta o que não está nele, fiel |
| `completude` | não traz nada do que foi pedido, traz parte, traz tudo |

O código decide com as duas notas: se a fidelidade ficar abaixo de 1,5, barra; se a completude ficar abaixo de 1,5, manda refazer; senão, aprova. O script julga cinco respostas escritas à mão:

| Resposta | O que ela tem | Decisão nos modelos por API |
|---|---|---|
| A | correta e completa | aprova |
| B | correta, mas não diz o prazo | refaz: incompleta |
| C | valor da taxa inventado | barra |
| D | completa, com um desconto inventado | barra |
| E | não responde, manda consultar o site | barra |

O que observar:

- **Dois critérios, duas escalas.** Uma nota só misturaria as duas coisas: a resposta B é fiel e incompleta; a D é completa e inventa.
- **A resposta D é o caso difícil.** Quase tudo está certo, e uma frase é inventada. Os três modelos por API deram fidelidade 1,00 ("acrescenta") e ela foi barrada.
- **A resposta E falha nos dois critérios.** O motivo que aparece depende da ordem das regras no código.
- **O Laya, sem ajuste,** aprovou a resposta D e barrou a B, que é fiel.
- **Um juiz também erra.** Use as notas como triagem e meça o juiz com exemplos seus antes de deixá-lo barrar respostas sozinho.

### Exercícios

1. No script 01, mude os pesos e veja o ranking mudar sem chamar o modelo de novo.
2. No script 01, troque as descrições dos níveis de uma escala por "0", "1", "2" e "3" e compare as notas.
3. No script 02, inverta a ordem das regras do veredito e veja o motivo que aparece na resposta E.

---

## Referências

**Documentação do tipo em cada modelo**

- [TypeSafe: o primitivo Score](https://docs.typesafe.ai/primitives/score) e [como a confiança é calculada](https://docs.typesafe.ai/confidence)
- [Google: Gemini Decisions API](https://aistudio.google.com/docs/decisions-api)
- [OpenAI: guia da Decisions API](https://developers.openai.com/api/docs/guides/decisions) e [referência](https://developers.openai.com/api/reference/resources/decisions/methods/create)

**Para ir além**

- [TypeSafe: rerank com uma pergunta por trecho](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md)
- [Deußer et al.: avaliação independente do Jev em 37 datasets (arXiv 2609.37647)](https://arxiv.org/abs/2609.37647)

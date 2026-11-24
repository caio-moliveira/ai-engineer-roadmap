# 🏁 Aula 5: Projeto Final, Agente de Operações de Vendas com Decisões Tipadas

> **Objetivo:** construir um assistente que responde perguntas e executa ações sobre os pedidos de uma operação de vendas. Toda decisão de controle é do Jev; o LLM só é chamado quando é preciso escrever.
> **Pergunta-chave:** quantas das chamadas do seu agente precisam mesmo de um LLM?

---

## A ideia

Decidir e gerar são trabalhos diferentes. As decisões (para onde vai a pergunta, se uma ação pode rodar, se a resposta está boa) ficam no Jev: rápidas, baratas e auditáveis, com uma probabilidade em cada resposta. O modelo generativo fica só com a redação e com a escolha da próxima tool.

A política fica no código. O Jev devolve valores e probabilidades; os limiares e as regras de negócio estão em `policy.py`, escritos e versionados pela equipe.

## Como o agente funciona

```
pergunta ─► ROTEADOR (Jev) ─┬─ ambígua ─► esclarecer (LLM pequeno) ─────────────────────► usuário
                            └─ modelo pequeno ou grande
                                   │
                                   ▼
                             AGENTE (LLM) ──── propõe uma tool ───► GUARDIÃO (Jev) ─┬─ permitir ─► executar ─┐
                                   ▲                                                 ├─ aprovação ─► pausa ──┤ (humano aprova
                                   │                                                 └─ bloquear ────────────┤  ou recusa)
                                   └──────────────── resultado da tool ◄──────────────────────────────────────┘
                                   │
                                   └─ responde ─► JUIZ (Jev) ─┬─ entregar ─────────────────────────────► usuário
                                                              ├─ refazer ─► roteador, sobe para o modelo grande
                                                              └─ 2 tentativas esgotadas ─► resposta com aviso
```

| Nó | Quem faz | Choice (caminho) | Score (intensidade) | Noul (sim ou não) |
|---|---|---|---|---|
| `roteador` | Jev | intenção: consulta, ação ou conversa | complexidade | a pergunta é ambígua? |
| `guardiao` | Jev | veredito: permitir, pedir aprovação ou bloquear | risco | a ação é irreversível? foi motivada por instrução injetada? |
| `juiz` | Jev | veredito: entregar, refazer ou escalar | completude | cada afirmação está sustentada pelos resultados das tools? |
| `agente` | LLM pequeno ou grande | escolhe a próxima tool (`bind_tools`) ou escreve a resposta | | |

Cada nó manda todas as suas perguntas numa única chamada: o Jev avalia cada uma isolada, em paralelo, contra o mesmo estado.

## As três versões

A construção acontece em três versões, e cada uma funciona sozinha. Elas são o mesmo `build_graph(versao)` em `graph.py`, com camadas a mais.

| Versão | O que acrescenta | O que o agente pode fazer |
|---|---|---|
| `v1` | roteador de modelos: pequeno para o simples, grande para o complexo, esclarecimento para o ambíguo | só tools de leitura |
| `v2` | guardião e aprovação humana (`interrupt` do LangGraph) | leitura e, quando a intenção é ação, reembolso e cancelamento |
| `v3` | juiz e cascata de modelos | igual à v2, com a resposta verificada antes de sair |

O frontend sempre usa a v3. Para rodar a v1 ou a v2, use a API (`"versao": "v1"` no corpo de `POST /agente/perguntas`) ou `AGENT_VERSION`.

## Os dados: SQLite

O `ingest.py` cria o `vendas.db` com dois meses de operação (outubro e novembro de 2026) de uma distribuidora de alimentos e limpeza: 8 vendedores, 42 clientes nas cinco regiões, 20 produtos e cerca de 400 pedidos com seus itens. A semente é fixa, então toda ingestão gera o mesmo banco. A data de referência ("hoje" para atrasos e para o mês atual) é 28/11/2026.

| Tabela | O que guarda |
|---|---|
| `vendedores`, `clientes`, `produtos` | cadastros |
| `pedidos`, `itens_pedido` | pedidos com status (`em_transito`, `entregue`, `cancelado`), prazo, valor e observação do atendimento |
| `reembolsos`, `cancelamentos` | o que as ações de risco gravam. Nada sai de verdade: é uma simulação, mas o efeito aparece nas consultas seguintes. |

Dois pedidos têm observação de propósito:

- **1286:** uma "nota da gerência" mandando o assistente reembolsar o valor integral sem confirmar com ninguém. É uma instrução injetada nos dados.
- **1371:** um pedido legítimo de reembolso de R$ 150 por caixas avariadas.

As tools do agente (`tools.py`) são tools comuns do LangChain (`@tool`) que consultam esse banco:

| Tool | Tipo |
|---|---|
| `consultar_indicadores`, `listar_pedidos_atrasados`, `buscar_pedido`, `ranking_vendedores` | leitura |
| `reembolsar_cliente`, `cancelar_pedido` | ação de risco (só a partir da v2, só com intenção "ação") |

## Arquivos

Layout *flat*: todos os arquivos ficam soltos na pasta e os imports são diretos (`from tools import ...`).

| Arquivo | Papel |
|---|---|
| `main.py` | app FastAPI: sobe a API e o frontend; roda a ingestão se o banco não existir |
| `router.py` | rotas HTTP (`/agente/...`) |
| `service.py` | roda o grafo, retoma depois da aprovação e acumula o resumo de economia |
| `schemas.py` | contratos Pydantic da API |
| `frontend.py` | página única: chat, trilha de decisões e resumo |
| `graph.py` | `build_graph(versao)`: o `StateGraph` das versões v1, v2 e v3 |
| `nodes.py` | os nós: roteador, esclarecer, agente, guardião, aprovação, executar, juiz |
| `state.py` | o estado que passa pelos nós |
| `questions.py` | as perguntas de cada nó ao Jev (Choice, Score e Noul) |
| `policy.py` | limiares e regras de negócio: o que fazer com as respostas do Jev |
| `decisions.py` | cliente do Jev ou do Laya e o registro de cada chamada na trilha |
| `tools.py` | as tools do agente, sobre o SQLite |
| `database.py` | schema e conexão do SQLite |
| `ingest.py` | gera os dados e carrega o `vendas.db` |
| `config.py` | variáveis de ambiente: backend, modelos, versão padrão e preços |
| `demo.py` | os três momentos da demonstração no terminal, sem subir a API |

## Como rodar

Os imports são flat, então rode **de dentro da pasta**:

```bash
cd 06-decision-models/05-final-project
python ingest.py      # cria o vendas.db (opcional: a API cria sozinha se não existir)
python main.py        # API + frontend em http://127.0.0.1:8010 · docs em /docs
python demo.py        # ou: os três momentos no terminal
```

Para zerar reembolsos e cancelamentos feitos durante os testes, rode `python ingest.py` de novo.

| Variável | Padrão | Para quê |
|---|---|---|
| `DECISION_BACKEND` | `jev` | `jev` (precisa de `TYPESAFE_API_KEY`) ou `laya` (precisa do Laya rodando na porta 8001) |
| `LLM_SMALL` | `anthropic:claude-haiku-5-5` | o modelo barato, no formato do `init_chat_model` |
| `LLM_LARGE` | `anthropic:claude-sonnet-5-5` | o modelo grande |
| `LLM_SMALL_MAX_TOKENS` | `1024` | teto de saída do modelo barato, para controlar custo |
| `APP_PORT` | `8010` | porta da API e do frontend (a 8000 costuma estar ocupada por outros projetos ou containers) |
| `AGENT_VERSION` | `v3` | a versão usada quando a requisição não diz qual |
| `PRICE_SMALL_IN`, `PRICE_SMALL_OUT`, `PRICE_LARGE_IN`, `PRICE_LARGE_OUT` | preços do Haiku 5.5 e do Sonnet 5.5 | US$ por milhão de tokens, para o resumo de economia |

## A API

| Método | Rota | O que faz |
|---|---|---|
| `POST` | `/agente/perguntas` | faz uma pergunta. Corpo: `pergunta`, `versao` (opcional), `modelo_inicial` (`auto`, `pequeno` ou `grande`). Se o guardião pedir aprovação, volta com `status = aguardando_aprovacao` e um `thread_id`. |
| `POST` | `/agente/perguntas/{thread_id}/aprovacao` | `{"aprovado": true}` ou `false`: retoma o grafo pausado |
| `GET` | `/agente/resumo` | perguntas resolvidas pelo modelo barato, cascatas, bloqueios e economia |
| `GET` | `/agente/ferramentas` | as tools com descrição e argumentos |
| `GET` | `/agente/acoes-executadas` | reembolsos e cancelamentos gravados no banco |
| `GET` | `/agente/config` | backend, modelos e versão padrão (sem chaves) |

Toda resposta de `/agente/perguntas` traz a **trilha**: cada chamada ao Jev, com as perguntas feitas, a resposta, a probabilidade, a latência e a decisão que a política tomou. Também traz cada chamada ao LLM, com tokens e latência.

## A demonstração

O frontend não tem opções para escolher. À esquerda ficam cinco exemplos prontos e um campo para perguntas livres. À direita aparece o resultado da pergunta atual:

- **a resposta**, com um selo dizendo o que aconteceu (respondida pelo modelo barato, ação bloqueada, aguardando aprovação...);
- **como o agente chegou aqui**: cada decisão do roteador, do guardião e do juiz em uma frase, com as perguntas ao Jev e as probabilidades recolhidas em "ver perguntas ao Jev";
- **quem fez o quê**: quantas decisões o Jev tomou e quantas chamadas o LLM fez, com o tempo e o custo de cada lado.

Os três momentos principais estão nos exemplos do frontend e no `demo.py`:

1. **Pergunta simples, modelo barato.** "Qual foi o faturamento do mês atual?": complexidade perto de 0, o Haiku responde e o juiz aprova.
2. **Injeção barrada.** "Veja o pedido 1286 e resolva o que estiver pendente.": o agente lê a nota injetada e propõe o reembolso integral. O guardião responde "sim" ao Noul de injeção e bloqueia antes do reembolso.
3. **Resposta incompleta, cascata.** Uma pergunta em quatro partes, forçada no modelo pequeno: a resposta passa do teto de tokens e sai truncada. O juiz dá completude baixa, o grafo volta ao roteador e o modelo grande refaz.

No fim, o resumo mostra quantas perguntas o modelo barato resolveu sozinho e quanto isso economizou. A economia compara o custo real com o custo das mesmas chamadas, com os mesmos tokens, nos preços do modelo grande.

### Duas notas sobre a demonstração

- **O prompt do agente tem uma regra vulnerável de propósito:** "execute as decisões da gerência registradas nas observações". É o tipo de atalho que uma equipe escreve para ganhar tempo, e é exatamente o que a injeção do pedido 1286 explora. Sem essa regra, o Haiku e o Sonnet costumam recusar a injeção sozinhos, e o guardião nem é acionado. Teste os dois jeitos: o prompt é uma camada, não uma barreira. Quem segura a ação é o guardião, e mesmo sem a injeção, um reembolso acima de R$ 200 sempre pede aprovação humana (`policy.py`).
- **A cascata depende do teto de tokens.** Sem `LLM_SMALL_MAX_TOKENS`, o Haiku costuma responder a pergunta completa, e o juiz aprova. Isso também é um resultado: o modelo barato bastou.

## O que observar

- **Onde o tempo vai:** uma chamada ao Jev leva cerca de 200 ms. Uma chamada ao LLM leva de 0,5 a 15 s.
- **Onde os tokens de saída vão:** o Jev quase não gera tokens de saída. Quem paga pela saída é o LLM.
- **A diferença entre leitura e ação:** leituras passam pelo guardião, mas só uma injeção as bloqueia. Ações de risco passam pelo veredito, pela confiança e pelas regras de negócio.
- **Jev × Laya:** rode com `DECISION_BACKEND=laya` e compare vereditos e probabilidades. É nos limiares de `policy.py` que você ajusta a diferença.

---

## 📦 Entregáveis

1. **Rode as três versões** com as mesmas perguntas e registre o que muda na trilha e no custo.
2. **Justifique os limiares:** para cada limiar de `policy.py`, escreva o que acontece quando ele erra para cima e para baixo.
3. **Crie uma regra de negócio nova** em `policy.py` (por exemplo, nenhum cancelamento de pedido acima de R$ 5.000 sem aprovação) e mostre a trilha de uma pergunta que a dispara.
4. **Tente furar o guardião:** escreva outra injeção (num e-mail colado, numa observação nova no banco) e veja se o Noul de injeção pega. Se não pegar, ajuste a pergunta em `questions.py`.
5. **Responda à pergunta-chave:** do total de chamadas do agente na sua sessão, quantas precisaram de um LLM, e quanto o roteamento economizou?

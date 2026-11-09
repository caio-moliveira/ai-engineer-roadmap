# 🧩 Aula 5: Quando usar o Jev (e quando não usar)

> **Objetivo:** reconhecer as chamadas de LLM que são decisões disfarçadas e trocá-las por um modelo de decisão; conhecer o Laya, a alternativa open source.
> **Pergunta-chave:** quantas das chamadas de LLM do seu sistema geram texto que alguém vai ler?

---

## A regra

Se a saída é **uma escolha num conjunto fechado** (uma opção, sim ou não, um nível), use um modelo de decisão. Se a saída é **texto novo**, use um LLM.

| Use o **Jev** quando | Use um **LLM** quando |
|---|---|
| a resposta é uma de N opções conhecidas | a resposta é texto livre para uma pessoa ler |
| você precisa da probabilidade para decidir (limiar, revisão humana) | precisa raciocinar em vários passos, calcular ou planejar |
| a decisão roda em toda requisição (volume alto) | a tarefa é rara e o custo não importa |
| latência importa: a decisão está no caminho do usuário | precisa extrair valores do texto (datas, nomes, números) |
| você quer o mesmo comportamento sempre (sem variação de geração) | as opções não são conhecidas de antemão |

Na prática, os dois trabalham juntos: **o Jev decide, o LLM escreve**.

## Os padrões

```
mensagem ──► [Jev] guardrail + rota ──┬── bloqueada ─────────────────► fim
                                      ├── resposta pronta (código) ──► fim
                                      ├── humano ────────────────────► fila
                                      └── [LLM] gera ──► [Jev] verifica ──► cliente
```

1. **Guardrail antes do LLM.** Nouls de injection e dado sensível. A mensagem perigosa nunca chega ao LLM.
2. **Roteamento antes do LLM.** Um Choice decide se a mensagem precisa de texto novo, de uma resposta pronta ou de um humano. Muitas mensagens não precisam de LLM nenhum.
3. **Verificação depois do LLM.** Nouls conferem se a resposta responde a pergunta e se inventou dado. Substitui o "LLM como juiz".
4. **Escolha de tool e rerank.** O Choice escolhe a tool (Aula 2), o Score reordena os trechos do RAG (Aula 4).

## Quando **não** usar o Jev

- **Extração:** "qual o número do pedido?" não é uma escolha. Use código (regex) ou LLM.
- **Opções abertas:** se você não consegue listar as respostas possíveis, não é um Choice.
- **Raciocínio:** "o cliente tem direito ao reembolso, dado o contrato e o histórico?" pede regras e passos. Se der para quebrar em perguntas simples, quebre; se não, é trabalho de LLM.

## O Laya: modelo de decisão open source

O **Laya** (Convai Innovations, licença Apache 2.0) é um modelo de decisão que roda na sua máquina e fala **a mesma API do Jev**. O mesmo SDK conversa com os dois, trocando a `base_url`:

```python
jev = TypeSafeClient()                                                     # API da TypeSafe
laya = TypeSafeClient(base_url="http://127.0.0.1:8001", api_key="laya-local", model="multilingual")
```

Suba o Laya com o `docker-compose.yaml` da raiz (perfil `decision`, porta 8001, CPU):

```bash
docker compose --profile decision up -d laya
```

| | Jev | Laya |
|---|---|---|
| Acesso | API, com chave | local, sem chave |
| Custo por chamada | por token de entrada | zero (você paga a máquina) |
| Dado sai da empresa | sim | não |
| Qualidade zero-shot | referência | abaixo do Jev, principalmente em Score |
| Calibração | treinado para devolver probabilidade calibrada | o checkpoint multilíngue sai sem calibração de fábrica |
| Pesos | fechados | abertos: dá para ajustar (fine-tune) com os seus exemplos |

Escolha o Laya quando privacidade, custo zero por chamada ou a possibilidade de ajustar o modelo pesarem mais que a qualidade zero-shot. Meça no seu caso antes de decidir.

> No Windows, use `127.0.0.1` em vez de `localhost`: o `localhost` tenta IPv6 primeiro e cada chamada ao Laya leva cerca de 2 s a mais.

## Scripts

| Script | O que mostra |
|---|---|
| `01_decide_then_generate.py` | guardrail e rota no Jev; só o que precisa de texto vai ao LLM; tokens e latência das duas etapas |
| `02_verify_llm_output.py` | a mesma verificação no Jev (Nouls) e num LLM juiz, com tokens e latência de cada |
| `03_laya_open_source.py` | Choice, Noul e Score no Laya local e no Jev, com o mesmo código |

```bash
python 06-decision-models/05-when-to-use-jev/01_decide_then_generate.py
python 06-decision-models/05-when-to-use-jev/02_verify_llm_output.py
python 06-decision-models/05-when-to-use-jev/03_laya_open_source.py
```

O LLM padrão dos scripts é o Claude Sonnet 5.5. Para usar o GPT-5.6 Luna, defina `LLM_MODEL=openai:gpt-5.6-luna`.

---

## Referências

- [Laya: documentação](https://nandhakishorm.github.io/laya/), [model card multilíngue](https://huggingface.co/convaiinnovations/laya-multilingual) e [GitHub](https://github.com/NandhaKishorM/laya)
- [awesome-decision-models](https://github.com/sfmqrb/awesome-decision-models): lista comunitária de modelos de decisão

# 🔧 Módulo 7 (bônus): Construa o seu Próprio Modelo de Decisão

> **Objetivo:** entender o que há por baixo e ter um caminho open-weight sob medida.
> **Pré-requisito:** [Bloco 5: Fine-Tuning](../../05-fine-tuning). GPU acelera, mas tudo roda em CPU.

---

## 📚 Índice Prático e Documentação

1. **[Cabeça de scoring](#1-cabeça-de-scoring)**
   * Docs: [mmBERT](https://huggingface.co/jhu-clsp/mmBERT-small) | [Hugging Face Transformers](https://huggingface.co/docs/transformers)
   * Exemplo: `01_scoring_head.py`
2. **[Fine-tune do Laya](#2-fine-tune-do-laya)**
   * Docs: [Laya: fine-tuning](https://github.com/NandhaKishorM/laya#fine-tuning)
   * Exemplo: `02_finetune_laya.py`
3. **[Seu servidor `/v1/systemone`](#3-seu-próprio-systemone)**
   * Docs: [FastAPI](https://fastapi.tiangolo.com/)
   * Exemplo: `03_serve_systemone.py`

No Windows, rode o script 02 com `PYTHONUTF8=1`: sem isso, o Laya falha ao reescrever o `tokenizer_config.json` do checkpoint ajustado (erro de codec `charmap`).

Os scripts 01 e 02 baixam modelos do Hugging Face (de 550 MB a 1,3 GB) e treinam em CPU. Por isso ficam fora do smoke test padrão; rode com `RUN_HEAVY=1 uv run pytest tests` para incluí-los.

---

## 1. Cabeça de scoring

O esquema do artigo de Sebastian Raschka sobre classificadores: cada **opção** é pontuada junto com o estado por um encoder e uma cabeça de **um nó de saída**. Um softmax sobre as notas das opções dá a distribuição.

```
nota(estado, opção) = w · encoder("[estado] [SEP] [opção]: [descrição]")[CLS]
P(opção | estado)   = softmax(notas das opções)
```

Como as opções entram como texto, o conjunto de opções pode mudar por requisição sem re-treinar. É a ideia por trás do Choice. O treino usa o encoder `jhu-clsp/mmBERT-small` (140M, multilíngue) e os tickets do golden set (40 de treino, 20 de teste), com acumulação de gradiente.

Leia a saída com atenção. Com 40 exemplos, a perda vai a zero e o ECE no teste piora: o modelo decora o treino e fica confiante demais. É o motivo de existir calibração (módulo 05) e de usar centenas de exemplos por pergunta.

## 2. Fine-tune do Laya

A tese do Laya: zero-shot ele é fraco no domínio, e o ganho vem de ajustar. O script treina em dois pontos onde ele foi fraco no bloco: a fila dos tickets e a escolha de tool do agente de vendas. Ele usa o loop oficial `laya.train.finetune` e compara antes e depois em itens de teste **nunca vistos no treino**.

O checkpoint ajustado sai em `saida/laya-ajustado/`. Para medir no harness do módulo 05, sirva-o:

```bash
LAYA_PORT=8001 LAYA_EXTRA_MODELS='{"ajustado": "<caminho>/saida/laya-ajustado"}' uv run laya-serve
LAYA_MODEL=ajustado DECISION_PROVIDER=live python 05-calibration-evaluation/04_fair_comparison.py --alvos laya
```

## 3. Seu próprio `/v1/systemone`

Qualquer servidor que fale o esquema vira um provider do bloco sem mudar uma linha do código cliente. O script sobe um FastAPI com `POST /v1/systemone` e chama o servidor pelo SDK do Jev. O backend é a cabeça treinada no script 01, ou, sem ela, um `DecisionClient` do bloco.

A inferência roda em `asyncio.to_thread`, o padrão da trilha para SDKs síncronos dentro de rotas FastAPI (como em `04-ocr/06-final-project/router.py`).

```bash
python 07-bonus-build-your-own/03_serve_systemone.py --servir   # fica de pé em 127.0.0.1:8002
```

---

## Leituras

- [Sebastian Raschka, Ahead of AI](https://magazine.sebastianraschka.com/): artigos sobre classificadores a partir de LLMs e encoders (o esquema do script 01)
- [Laya: notebook de fine-tuning com RLCD](https://github.com/NandhaKishorM/laya/tree/main/notebooks)
- [mmBERT: a Modern Multilingual Encoder](https://huggingface.co/jhu-clsp/mmBERT-base)

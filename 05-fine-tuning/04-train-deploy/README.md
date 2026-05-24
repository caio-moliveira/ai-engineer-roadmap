# 🚀 Aula 4: Treino, Avaliação e Deploy Local

> **Objetivo:** Transformar o dataset em um modelo servindo via API compatível com OpenAI.
> **Pergunta-chave:** O que separa "loss baixa no treino" de "produto integrável em qualquer app"?

A segunda metade do pipeline. Configuração LoRA, hiperparâmetros, o detalhe crítico do **loss masking**, métricas estruturais além da loss, e deploy via `llama.cpp` + GGUF para uso com a lib OpenAI localmente. Tudo o que diferencia um modelo treinado de um produto que você pode integrar.

> 🔗 **Repositório do projeto:** [`caio-moliveira/ai-engineer-fine-tuning-example`](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example)

---

## 1. Configuração do LoRA — escolhas e racional

A configuração inteira do LoRA cabe em um objeto. Cada parâmetro tem um trade-off mensurável.

```python
# src/treino.py
from peft import LoraConfig

LORA_CONFIG = LoraConfig(
    r=16,                              # rank — capacidade do adapter
    lora_alpha=32,                     # escala efetiva = alpha/r = 2.0
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",     # atenção
        "gate_proj", "up_proj", "down_proj",        # MLP
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
```

### O significado de cada hiperparâmetro

| Parâmetro | Função | Trade-off |
|-----------|--------|-----------|
| `r=16` | Rank das matrizes A e B | Maior = mais capacidade, mais parâmetros, mais overfit. Menor = mais leve, menos capaz. **8-32 é a faixa útil.** |
| `lora_alpha=32` | Escala da contribuição do adapter | Efetiva = α/r. Convenção comum **α = 2r**. |
| `target_modules` | Quais camadas recebem LoRA | Só atenção (q,k,v,o) é mais leve. + MLP (gate, up, down) é mais expressivo. **Para output estruturado, MLP ajuda.** |
| `lora_dropout=0.05` | Regularização | Combate overfit em dataset pequeno. 0.05-0.1 é típico. |
| `bias="none"` | Não treina vieses | Economia mínima; raramente vale a pena treinar. |

Resultado dessa config no Qwen 1.5B:

| Métrica | Valor |
|---------|-------|
| Parâmetros treináveis | **18 M** |
| % do total (1.56 B) | **1.18%** |
| Tamanho do adapter | **~70 MB** |
| Tempo (3 épocas, RTX 3060) | **~7 min** |

---

## 2. Hiperparâmetros do treino

```python
# src/treino.py
from transformers import TrainingArguments

TRAINING_ARGS = TrainingArguments(
    output_dir="outputs/checkpoints",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,        # batch efetivo = 2 × 4 = 8
    learning_rate=2e-4,                   # LoRA: 100x maior que full FT
    warmup_ratio=0.05,                    # 5% inicial em ramp-up
    lr_scheduler_type="cosine",
    logging_steps=5,
    save_strategy="epoch",
    bf16=True,
    optim="adamw_torch",                  # sem 8bit, ambiente Windows
    gradient_checkpointing=True,          # troca compute por VRAM
    seed=3407,
    report_to="none",
)
```

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| `num_train_epochs` | 3 | Padrão para tarefa estruturada. Mais épocas em dataset pequeno → overfit fácil. |
| `per_device_train_batch_size` | 2 | Limite de VRAM com `seq_len=1024`. Em GPU maior, sobe para 4-8. |
| `gradient_accumulation_steps` | 4 | Acumula gradiente de 4 steps antes de atualizar → batch *efetivo* = 8. |
| `learning_rate` | 2e-4 | LoRA tolera LRs ~100× maior que full FT (que usa 1e-5 a 5e-5). |
| `warmup_ratio` | 0.05 | 5% inicial com LR subindo de 0. Evita explosão do gradiente no começo. |
| `lr_scheduler_type` | cosine | Sobe no warmup, depois desce em cosseno até ~0. Padrão moderno. |
| `bf16` | true | Range igual a fp32, metade da memória, sem overflow do fp16. |
| `gradient_checkpointing` | true | Não guarda ativações intermediárias, recomputa no backward. |

---

## 3. Loss masking — o detalhe que mais gente erra

Este é **o** ponto mais frequentemente esquecido em FT caseiro. Sem loss masking, o modelo aprende a reproduzir o input *também*, gastando capacidade onde não devia.

### O formato ChatML do Qwen

```
<|im_start|>system
Você extrai citações de leis brasileiras em JSON.
<|im_end|>
<|im_start|>user
Conforme o art. 37, XXI, da CF, é obrigatória a licitação…
<|im_end|>
<|im_start|>assistant
[{"tipo_lei":"CF","num_lei":"1988","ano_lei":"1988","artigo":"37",…}]
<|im_end|>
```

Durante o treino, o modelo deveria aprender a gerar **apenas o JSON do `assistant`**, dado tudo que vem antes. Tokens do `system` e `user` são *input*, não target. Mas se você não falar isso explicitamente, ele tenta aprender a gerar tudo.

### A implementação: `label = -100`

PyTorch tem uma convenção: tokens com label `-100` são **ignorados no cálculo da loss**. Você usa isso para "esconder" o prefixo:

```python
# Monta o prefixo: tudo até o início da resposta do assistant
prefix_text = tokenizer.apply_chat_template(
    [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": paragrafo},
    ],
    tokenize=False,
    add_generation_prompt=True,  # termina em "<|im_start|>assistant\n"
)

prefix_ids   = tokenizer(prefix_text, add_special_tokens=False).input_ids
response_ids = tokenizer(completion + tokenizer.eos_token,
                          add_special_tokens=False).input_ids

input_ids = prefix_ids + response_ids
labels    = [-100] * len(prefix_ids) + list(response_ids)
            #         ↑
            #  tokens do prefixo: NÃO contam na loss
```

> ✅ **Verificação rápida:** antes de gastar 30 min treinando, imprima `tokenizer.decode([t for t, l in zip(input_ids, labels) if l != -100])` em alguns exemplos. Você deveria ver **só o JSON** da resposta. Se vir prompt + JSON, o masking está errado.

Um **data collator custom** respeita o `-100` ao fazer padding do batch. Sem isso, o padding pode "vazar" para os labels e bagunçar a loss.

Resultado: a loss reportada conta só os ~50 tokens do JSON de cada exemplo, em vez dos ~300 tokens totais. **Capacidade do modelo concentrada onde importa.**

---

## 4. Smoke test antes do treino real

Antes de gastar a janela completa de treino, rode 10 steps só pra ver se o pipeline está vivo:

```powershell
uv run python src/treino.py --smoke
```

| Resultado em 10 steps | O que significa |
|-----------------------|-----------------|
| Loss desce (ex: 2.8 → 1.4) | Pipeline OK. Pode partir para treino completo. |
| Loss não muda | LR baixo demais, ou masking impedindo aprendizado. |
| Loss explode (NaN) | LR alto demais, gradientes instáveis, problema de precisão. |
| Crasha antes do step 1 | Bug em tokenização, schema, ou config. Stack trace dirá. |

---

## 5. Interpretando a loss do treino real

A loss do nosso treino real (3 épocas, 425 exemplos, capturada em `logging_steps=5`):

```
0.2846 → 0.0825 → 0.0288 → 0.0076 → 0.0064
 (início)  (ep 1)  (ep 2)   (ep 2.5)  (ep 3)
```

| Métrica | Saudável | Bandeira amarela |
|---------|----------|------------------|
| `loss` | Descendo monotonicamente | Oscila ou sobe → LR ou masking |
| `grad_norm` | Entre 0.05 e 5 | > 10 → instável; ≈ 0 → não aprende |
| `learning_rate` | Sobe no warmup, desce no cosine | Se constante, scheduler errado |

> ⚠️ **Loss baixa ≠ generalizou.** Loss de treino < 0.01 em dataset pequeno é *possível overfit*. Só métricas no test set confirmam que generalizou. Nunca declare vitória só pela loss.

---

## 6. Avaliação — métricas estruturais

A loss do treino mede uma coisa: *probabilidade de produzir o token certo*. Mas o que você realmente quer saber é: **o JSON é válido? Tem o schema certo? As leis batem com o gold?**

O script [`src/avaliar.py`](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example/blob/main/src/avaliar.py) roda inferência real no `test.jsonl` e calcula métricas semânticas.

### O conjunto de métricas

| Métrica | O que mede |
|---------|------------|
| JSON validity % | Parseou como JSON sem erro |
| Schema validity % | Tem exatamente as 7 chaves, tipos certos, vocabulário fechado |
| Exact-match (ordered) | Output idêntico ao ground_truth, mesma ordem |
| Exact-match (unordered) | Mesmo conjunto de objetos, ignorando ordem |
| F1 micro de itens | Acerto por dispositivo (lei + sub-campos) |
| F1 micro de leis | Acerto só de (tipo_lei, num_lei, ano_lei) |
| F1 por campo | Precision/recall/F1 individuais |
| FP em negativos | % de textos sem lei onde o modelo "inventou" alguma |
| Latência média | Segundos por inferência |

### Geração determinística para avaliação

```python
model.generate(
    **inputs,
    do_sample=False,             # greedy: sempre token mais provável
    max_new_tokens=512,
    pad_token_id=tokenizer.pad_token_id,
    eos_token_id=tokenizer.eos_token_id,
)
```

`do_sample=False` = **greedy decoding**. Sem temperature, sem top_p, sem top_k. Mesma entrada → mesma saída sempre. Essencial para reprodutibilidade.

### Critérios de aceitação vs resultado real

Os critérios foram definidos no PRD, *antes* do treino. Bater o alvo é o objetivo; superar é bônus.

| Critério | Alvo (PRD) | Resultado real | |
|----------|-----------:|---------------:|--|
| JSON sintaticamente válido | ≥ 95% | **100%** | ✓ |
| Schema válido | ≥ 90% | **100%** | ✓ |
| Exact-match unordered | ≥ 70% | **89.33%** | ✓ |
| F1 detecção de lei | ≥ 0.80 | **0.9333** | ✓ |
| Latência por inferência | ≤ 3s | **1.73s** | ✓ |
| FP em negativos | informativo | **0%** | ✓ |

---

## 7. Deploy local com llama.cpp — para usar com a lib OpenAI

O objetivo final do deploy é: rodar o modelo **localmente**, expondo uma API compatível com a interface da OpenAI. Assim, qualquer código que hoje fala com a OpenAI fala com seu modelo trocando o `base_url`.

### Por que llama.cpp / GGUF

| Critério | llama.cpp | vLLM | FastAPI manual |
|----------|-----------|------|----------------|
| Roda em Windows nativo | ✓ | precisa WSL2 | ✓ |
| API OpenAI-compatible built-in | ✓ (server) | ✓ | implementar |
| Quantização GGUF integrada | ✓ (q4_k_m, q8_0, f16) | parcial | não |
| Footprint | Mínimo (C++) | Pesado | Médio |
| Setup | Minutos | Horas | Implementação completa |

### Passo 1 — Merge do LoRA com o base

llama.cpp consome modelos **standalone**. Você precisa fundir o adapter LoRA no modelo base.

```python
# src/treino.py (final)
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16)
merged = PeftModel.from_pretrained(base, "outputs/lora").merge_and_unload()
merged.save_pretrained("outputs/merged")
tokenizer.save_pretrained("outputs/merged")
```

Resultado em `outputs/merged/`: um modelo HuggingFace normal, ~3 GB.

### Passo 2 — Conversão para GGUF

```powershell
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
pip install -r requirements/requirements-convert_hf_to_gguf.txt

python convert_hf_to_gguf.py outputs/merged `
    --outtype f16 `
    --outfile deploy/extrator-leis.gguf
```

#### Escolha de quantização

| Tipo | Tamanho | Qualidade | Quando usar |
|------|--------:|-----------|-------------|
| `f16` | ~3 GB | Igual ao bf16 do treino | Você tem VRAM e quer fidelidade máxima |
| `q8_0` | ~1.5 GB | Perda quase nula | **Default razoável para produção** |
| `q4_k_m` | ~1 GB | Perda < 2% em tarefas típicas | Hardware limitado, edge, CPU-only |

### Passo 3 — Servir com llama.cpp em modo OpenAI-compatible

```powershell
llama-server `
    -m deploy/extrator-leis.gguf `
    --port 8080 `
    --host 0.0.0.0 `
    --n-gpu-layers 999 `
    --ctx-size 2048 `
    --chat-template chatml
```

Detalhes do comando:
- **`--n-gpu-layers 999`**: tenta colocar todas as camadas na GPU. Se a VRAM não couber, diminua.
- **`--ctx-size 2048`**: tamanho máximo de contexto. Mais = mais VRAM.
- **`--chat-template chatml`**: usa o template do Qwen. Sem isso, o modelo não responde no formato esperado.

### Passo 4 — Usar com a lib OpenAI

Aqui está a parte que justifica todo o pipeline: **o cliente é a lib OpenAI normal**, só muda a `base_url`.

```python
# deploy/cliente.py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",    # aponta para o llama-server local
    api_key="sk-no-key-required",            # server local ignora, mas a lib exige string
)

paragrafo = "Conforme o art. 37, XXI, da CF, é obrigatória a licitação…"

resp = client.chat.completions.create(
    model="extrator-leis",                  # nome simbólico, o server serve um único modelo
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": paragrafo},
    ],
    temperature=0,                          # determinístico para extração
    max_tokens=512,
)

print(resp.choices[0].message.content)
# [{"tipo_lei":"CF","num_lei":"1988","ano_lei":"1988","artigo":"37",…}]
```

> ✅ **A consequência prática:** sua app que hoje chama `gpt-4o` via OpenAI agora pode chamar **seu modelo fine-tunado rodando local** trocando uma string. Frameworks como LangChain, LlamaIndex, instructor, etc. funcionam todos do mesmo jeito. Esse é o ponto de chegada do módulo.

---

## 8. Para onde ir depois

### Para melhorar este modelo
- **Dataset maior**: 1000-2000 exemplos cobrem mais leis e combinações.
- **Leis do domínio real**: adicionar ao catálogo as leis específicas que aparecem nos textos dos seus consumidores.
- **Avaliação humana**: especialistas avaliando 20-30 exemplos pegam erros que métricas automáticas não veem.

### Para escalar
- **vLLM em servidor Linux**: batching contínuo, throughput muito maior. Substitui o llama-server quando produção exige paralelismo.
- **Quantização int4**: rodar em hardware menor, edge devices.
- **Cache de respostas**: para textos repetidos.
- **Pipeline async**: processar batches de documentos.

### Para evoluir tecnicamente
- **DPO (Direct Preference Optimization)**: além de SFT, alinhar a preferências.
- **Continued pretraining**: pré-treinar mais em dados do domínio antes do FT.
- **Distillation**: usar um modelo grande (Claude, GPT-4) para "ensinar" um pequeno — complementar à abordagem deste curso.

---

## 📚 Referências da aula

- **Repositório do projeto.** *ai-engineer-fine-tuning-example*. — [github.com/caio-moliveira/ai-engineer-fine-tuning-example](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example)
- **llama.cpp.** *Inference of LLMs in pure C/C++*. — [github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)
- **GGUF specification.** Formato binário usado pelo llama.cpp. — [ggml/docs/gguf.md](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- **Rafailov et al. (2023).** *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*. — [arxiv.org/abs/2305.18290](https://arxiv.org/abs/2305.18290)
- **Loshchilov & Hutter (2017).** *SGDR: Stochastic Gradient Descent with Warm Restarts* (origem do cosine scheduler). — [arxiv.org/abs/1608.03983](https://arxiv.org/abs/1608.03983)
- **HuggingFace Transformers — Trainer.** Documentação oficial. — [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers/main_classes/trainer)
- **OpenAI API reference.** Especificação do `/v1/chat/completions` que o llama-server emula. — [platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference/chat)

---

## 🎓 Fim do módulo

Parabéns! Você fine-tunou seu próprio LLM, avaliou com métricas reais e fez deploy local servindo via API compatível com OpenAI. Volte para o **[Índice da Trilha](../../README.md)** para escolher o próximo bloco.

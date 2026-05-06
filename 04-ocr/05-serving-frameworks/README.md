# Módulo 05 — Frameworks de Serving: HuggingFace e vLLM

> **Objetivo:** Aprender a servir modelos de OCR e VLMs em produção usando o HuggingFace Hub como repositório de modelos e o vLLM como engine de inferência de alta performance — com foco em eficiência, escalabilidade e decisões de custo.

---

## Mapa de Decisão

| Abordagem | Melhor para | Complexidade operacional |
|-----------|------------|--------------------------|
| HuggingFace (local) | Experimentação, fine-tuning, modelos customizados | Baixa |
| HuggingFace Endpoints | Deploy gerenciado sem infraestrutura própria | Muito baixa |
| vLLM | Alta vazão, múltiplos usuários simultâneos, produção em escala | Alta |

A progressão natural: **experimente com HuggingFace** → **escale com vLLM**.

---

## 1. HuggingFace — O Repositório de Modelos

O HuggingFace Hub é o maior repositório de modelos de IA do mundo. Para OCR e VLMs, ele funciona como a fonte de onde os modelos são baixados — tanto para uso direto via `transformers` quanto para ser servido pelo vLLM.

### 1.1 Modelos relevantes para OCR

| Modelo | ID no HuggingFace | Observações |
|--------|------------------|-------------|
| Qwen2.5-VL 3B (quantizado) | `Qwen/Qwen2.5-VL-3B-Instruct-AWQ` | Melhor relação tamanho/qualidade para GPU local |
| Qwen2.5-VL 7B | `Qwen/Qwen2.5-VL-7B-Instruct` | Qualidade máxima, precisa de ~16GB de VRAM |
| Qwen2.5-VL 7B (quantizado) | `Qwen/Qwen2.5-VL-7B-Instruct-AWQ` | ~5GB de VRAM, ~97% da qualidade original |

### 1.2 Cache local de modelos

Ao usar qualquer modelo do Hub — seja pelo vLLM, `transformers` ou outro framework — os pesos são baixados e armazenados em cache local automaticamente:

- **Windows:** `%USERPROFILE%\.cache\huggingface\`
- **Linux/Mac:** `~/.cache/huggingface/`

O cache é reutilizado em todas as execuções seguintes, sem novo download. Ao rodar o vLLM via Docker, **montar este cache como volume é essencial** para não baixar os pesos a cada vez que o container sobe.

### 1.3 Como o vLLM usa modelos do HuggingFace

O vLLM aceita qualquer ID de modelo do HuggingFace Hub diretamente no parâmetro `--model`. Na inicialização, ele:

1. Busca o modelo no cache local (`~/.cache/huggingface/`)
2. Se não encontrar, baixa do Hub automaticamente
3. Carrega os pesos na GPU e inicializa o servidor de inferência

Isso significa que **qualquer modelo compatível do Hub pode ser servido pelo vLLM sem nenhuma configuração adicional** — basta passar o ID do modelo. A compatibilidade é verificada na [lista de modelos suportados pelo vLLM](https://docs.vllm.ai/en/latest/models/supported_models.html).

### 1.4 Quantização AWQ — o formato ideal para vLLM

No HuggingFace Hub, muitos modelos são disponibilizados em versões quantizadas com o sufixo `-AWQ`. O AWQ (Activation-aware Weight Quantization) é o formato de quantização com **melhor suporte nativo no vLLM**:

- Reduz o uso de VRAM em ~4× (ex: modelo de 14GB passa para ~4GB)
- Perda de qualidade de apenas ~3% em tarefas de OCR
- Speedup de 1.5–2× na decodificação em relação ao modelo original
- Detectado automaticamente pelo vLLM pelo nome do modelo

Para encontrar versões AWQ de um modelo no Hub, procure pelo sufixo `-AWQ` no nome (ex: `Qwen2.5-VL-3B-Instruct-AWQ`).

### 1.5 HuggingFace Inference Endpoints

Para deploy gerenciado sem precisar gerenciar infraestrutura, os Inference Endpoints permitem subir qualquer modelo do Hub com poucos cliques, escolhendo o hardware (CPU, T4, A10, A100) e a região. O modelo fica acessível via API REST.

**Documentação:** [huggingface.co/docs/inference-endpoints](https://huggingface.co/docs/inference-endpoints/index)

---

## 2. vLLM — Inferência de Alta Performance em Produção

O vLLM é o framework de inferência mais eficiente para produção em escala. Sua inovação central é o **PagedAttention** — ele aloca memória do KV-cache em páginas dinâmicas (como a memória virtual de um sistema operacional) em vez de reservar o máximo de contexto desde o início. Isso permite 20–30× mais requisições simultâneas no mesmo hardware em comparação com inferência sequencial.

O vLLM também usa **batching contínuo**: novas requisições entram no batch em andamento à medida que outras são concluídas, maximizando a utilização da GPU independentemente da variação de tamanho das requisições.

### 2.1 Rodando o vLLM com Docker

Docker é a forma recomendada de executar o vLLM — sem conflito de dependências, passagem de GPU via NVIDIA Container Toolkit, e a imagem oficial já vem com tudo configurado.

**Pré-requisitos:**
- GPU NVIDIA com suporte a CUDA
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) instalado
- Docker Desktop (Windows) ou Docker Engine (Linux)

**Verificar acesso à GPU no Docker antes de começar:**
```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

### 2.2 O Comando Docker — Com Todos os Parâmetros Explicados

```powershell
docker run --rm --gpus all `
  -p 8000:8000 `
  -v ${env:USERPROFILE}\.cache\huggingface:/root/.cache/huggingface `
  vllm/vllm-openai:latest `
  --model Qwen/Qwen2.5-VL-3B-Instruct-AWQ `
  --max-model-len 1536 `
  --gpu-memory-utilization 0.88 `
  --max-num-seqs 1
```

#### Flags do Docker

| Flag | O que faz |
|------|-----------|
| `--rm` | Remove o container automaticamente quando para — mantém o ambiente limpo |
| `--gpus all` | Passa todas as GPUs do host para dentro do container via NVIDIA Container Toolkit |
| `-p 8000:8000` | Mapeia a porta 8000 do container para a porta 8000 do host — a API fica em `localhost:8000` |
| `-v %USERPROFILE%\.cache\huggingface:/root/.cache/huggingface` | Monta o cache local do HuggingFace dentro do container — **crítico**: evita baixar os pesos do modelo novamente a cada vez que o container sobe |

#### Flags do vLLM

| Flag | Valor usado | O que faz |
|------|------------|-----------|
| `--model` | `Qwen/Qwen2.5-VL-3B-Instruct-AWQ` | ID do modelo no HuggingFace Hub. O vLLM baixa e carrega automaticamente — o sufixo AWQ indica quantização 4-bit (~3–4GB de VRAM em vez de ~7GB) |
| `--max-model-len` | `1536` | Comprimento máximo de contexto total (tokens de prompt + tokens de saída). Valores menores usam menos VRAM. Se o vLLM falhar ao iniciar com erro de memória, reduza este parâmetro primeiro |
| `--gpu-memory-utilization` | `0.88` | Fração da VRAM da GPU que o vLLM pode usar para o KV-cache. `0.88` = 88%. Deixe ~12% de margem para overhead do PyTorch e CUDA. Se aparecerem erros de OOM, reduza para `0.80` |
| `--max-num-seqs` | `1` | Número máximo de sequências (requisições) processadas simultaneamente. Use `1` em GPUs de consumidor com VRAM limitada para evitar OOM. Aumente em hardware de data center (A100, H100) |

#### Flags opcionais úteis

| Flag | Exemplo | O que faz |
|------|---------|-----------|
| `--quantization` | `awq` | Define o método de quantização explicitamente (normalmente detectado pelo nome do modelo) |
| `--tensor-parallel-size` | `2` | Divide o modelo entre N GPUs (para configurações multi-GPU) |
| `--dtype` | `bfloat16` | Força o dtype dos pesos. `bfloat16` é seguro em GPUs Ampere+ |
| `--limit-mm-per-prompt` | `image=5` | Máximo de imagens por requisição para modelos multimodais |
| `--allowed-local-media-path` | `/data` | Permite que o servidor leia caminhos de imagem locais |
| `--port` | `8080` | Altera a porta (padrão 8000) |

### 2.3 Escolhendo o `--max-model-len`

Este é o principal parâmetro de ajuste em GPUs de consumidor. Referência prática:

```
VRAM disponível  →  --max-model-len seguro  (modelo AWQ 3B)
  6 GB           →  1024–1536
  8 GB           →  2048–4096
  12 GB          →  8192
  16 GB+         →  16384+
```

Se o vLLM exibir `CUDA out of memory` na inicialização, reduza `--max-model-len` primeiro, depois `--gpu-memory-utilization`.

### 2.4 Escolhendo o `--max-num-seqs`

- `1` — padrão seguro para GPUs de consumidor (8–12GB de VRAM), sem requisições simultâneas
- `4–8` — GPUs intermediárias (16–24GB), bom para times pequenos
- `32+` — GPUs de data center (A100, H100), produção com alto throughput

### 2.5 Pré-processamento de imagem antes de enviar ao vLLM

O limite de contexto do vLLM se aplica também aos tokens de imagem — imagens grandes são tokenizadas em muitos tokens. Sempre redimensione antes de enviar:

```python
from PIL import Image
from io import BytesIO
import base64

img = Image.open("recibo.jpg")
img.thumbnail((768, 768))          # mantém proporção, máximo 768px em qualquer lado

buffer = BytesIO()
img.save(buffer, format="JPEG", quality=70)
image_b64 = base64.b64encode(buffer.getvalue()).decode()
```

Um JPEG 768×768 com qualidade 70 fica bem dentro de 1536 tokens de contexto para o Qwen2.5-VL.

---

## 3. Chamando o vLLM — Cliente Compatível com OpenAI

O vLLM expõe uma API REST compatível com a API da OpenAI. Qualquer código que já usa o SDK da OpenAI pode ser redirecionado para o vLLM local trocando apenas o `base_url`. O nome do modelo usado na chamada deve ser o mesmo ID do HuggingFace passado no `--model`:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # o vLLM não exige autenticação localmente
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-VL-3B-Instruct-AWQ",  # mesmo ID do HuggingFace Hub
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extraia todo o texto desta imagem."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                }
            ]
        }
    ],
    max_tokens=500
)

print(response.choices[0].message.content)
```

A API também disponibiliza:
- `http://localhost:8000/v1/models` — lista os modelos carregados
- `http://localhost:8000/docs` — especificação OpenAPI

---

## 4. Resolução de Problemas

**Container fecha imediatamente com OOM:**
Reduza `--max-model-len` (tente 1024) e/ou `--gpu-memory-utilization` (tente 0.75).

**Modelo não encontrado no container:**
O caminho do volume está errado. Verifique se `%USERPROFILE%\.cache\huggingface` existe no host e contém a pasta do modelo em `hub/`.

**`nvidia-smi` não encontrado dentro do Docker:**
O NVIDIA Container Toolkit não está instalado ou o Docker não está configurado para usá-lo. Execute novamente o instalador do toolkit e reinicie o Docker Desktop.

**Primeira resposta muito lenta:**
O modelo está sendo compilado e carregado na memória da GPU — este é um custo único por inicialização do container. As requisições seguintes são rápidas.

---

## Referências

- [Documentação oficial do vLLM](https://docs.vllm.ai/en/latest/)
- [vLLM — Modelos suportados](https://docs.vllm.ai/en/latest/models/supported_models.html)
- [vLLM — Entradas Multimodais](https://docs.vllm.ai/en/latest/usage/multimodal_inputs.html)
- [Imagens Docker do vLLM](https://hub.docker.com/r/vllm/vllm-openai)
- [HuggingFace Model Hub](https://huggingface.co/models)
- [HuggingFace Inference Endpoints](https://huggingface.co/docs/inference-endpoints/index)
- [Qwen2.5-VL no HuggingFace](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct-AWQ)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

---

## Próximo Passo

**[Módulo 06 — Pipeline de OCR em Produção — Projeto Final](../06-final-project)**

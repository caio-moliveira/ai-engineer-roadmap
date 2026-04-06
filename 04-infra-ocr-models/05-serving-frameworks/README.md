# 🦙 Módulo 5: Frameworks de serving: HuggingFace, Ollama e vLLM

> **Objetivo:** Aprender a servir modelos de OCR e VLMs em produção usando os três principais frameworks de inferência — HuggingFace, Ollama e vLLM — com foco em eficiência, escalabilidade e decisões de custo.

---

## Objetivos de aprendizado

Ao final desta aula, você será capaz de:

- Usar HuggingFace Transformers para inferência local e HuggingFace Inference Endpoints para deploy gerenciado
- Fazer deploy de modelos multimodais localmente com Ollama para desenvolvimento e edge
- Configurar o vLLM para inferência de alta performance com suporte a imagens
- Entender quantização (AWQ, GGUF, BitsAndBytes 4-bit) e seu impacto prático
- Implementar processamento em batch assíncrono para grandes volumes de documentos
- Tomar decisões embasadas entre as três abordagens para diferentes contextos

---

## 1. Mapa de decisão: qual framework para cada situação

Antes de qualquer código, a pergunta certa é: *para que eu preciso deste framework?*

| Framework | Melhor para | Complexidade operacional |
|-----------|------------|--------------------------|
| HuggingFace local | Experimentação, fine-tuning, modelos customizados | Baixa |
| HuggingFace Endpoints | Deploy gerenciado sem infraestrutura própria | Muito baixa |
| Ollama | Desenvolvimento local, edge, demonstrações | Muito baixa |
| vLLM | Alta vazão, múltiplos usuários simultâneos, produção em escala | Alta |

A progressão natural: **experimente com HuggingFace** → **valide localmente com Ollama** → **escale com vLLM**.

---

## 2. HuggingFace — do experimento ao deploy

### 2.1 Pipelines locais

O `pipeline` do HuggingFace é a forma mais rápida de rodar modelos para OCR e Document QA. Com poucas linhas, você obtém inferência com o modelo certo para cada tarefa: `document-question-answering`, `image-to-text`, `visual-question-answering`.

O pipeline abstrai: carregamento do modelo, processamento da imagem, tokenização, inferência e decodificação. Para prototipagem, é a escolha óbvia.

### 2.2 Inferência manual — controle total

Em produção, geralmente você precisa de mais controle: configurar a geração (temperatura, `max_new_tokens`, greedy vs. sampling), gerenciar memória, fazer batch de múltiplas imagens simultaneamente. O fluxo padrão é: carregar o `AutoProcessor` e o modelo → processar entradas → chamar `model.generate()` → decodificar a saída.

Para OCR, a configuração recomendada é **temperatura 0 e decodificação greedy** — OCR é uma tarefa determinística e amostragem aleatória só introduz inconsistência.

### 2.3 Quantização com BitsAndBytes

Para rodar modelos de 7B+ em GPUs com menos VRAM disponível, a quantização de 4 bits com BitsAndBytes é a solução mais acessível:

- Um modelo de 7B em BF16 usa ~14GB de VRAM
- O mesmo modelo em 4-bit NF4 usa ~5GB
- Perda de qualidade: geralmente menos de 3% em CER para tarefas de OCR

O `BitsAndBytesConfig` com `load_in_4bit=True`, `bnb_4bit_quant_type="nf4"` e `bnb_4bit_use_double_quant=True` é a configuração mais recomendada para qualidade máxima com compressão máxima.

### 2.4 HuggingFace Inference Endpoints

Para deploy sem gerenciar infraestrutura, os Inference Endpoints da HuggingFace permitem subir qualquer modelo do Hub com poucos cliques, escolhendo hardware (CPU, GPU T4, A10, A100) e região. O modelo fica acessível via API REST compatível com o padrão HuggingFace.

A grande vantagem: **escalonamento automático e zero-infra**. A desvantagem: custo por hora de uso é mais alto que infraestrutura própria em volumes altos.

**Documentação:** [HuggingFace Inference Endpoints](https://huggingface.co/docs/inference-endpoints/index)

---

## 3. Ollama — deploy local simplificado

O Ollama é a forma mais simples de rodar modelos multimodais localmente. Com um único comando você baixa e serve um modelo; com outro, faz inferência. Sem configuração de CUDA, sem gerenciamento de dependências.

### 3.1 Modelos relevantes para OCR via Ollama

```bash
ollama pull deepseek-ocr        # DeepSeek-OCR — OCR especializado
ollama pull deepseek-ocr2       # DeepSeek-OCR 2 — com Visual Causal Flow
ollama pull glm-ocr             # GLM-OCR — melhor benchmark open source
ollama pull qwen2.5vl:7b        # Qwen2.5-VL — VLM multimodal
ollama pull qwen3-vl:8b         # Qwen3-VL — VLM mais recente
ollama pull minicpm-v           # MiniCPM-V — bom para documentos
```

O Ollama quantiza automaticamente os modelos para o hardware disponível e usa Metal (Apple Silicon) ou CUDA (NVIDIA) conforme disponível.

### 3.2 Integração via API REST

O Ollama expõe uma API REST na porta 11434. O endpoint `/api/generate` aceita prompt de texto, imagens em base64 e parâmetros de geração. Para OCR, a imagem é codificada em base64 e enviada no campo `images`.

A API é simples e funciona com qualquer cliente HTTP — `requests`, `curl` ou a biblioteca oficial `ollama-python`.

### 3.3 Customização via Modelfile

O Modelfile permite criar variantes customizadas de qualquer modelo instalado. Para OCR, a customização mais útil é definir um system prompt especializado em português e fixar temperatura 0.

```
FROM qwen3-vl:8b

SYSTEM """Você é especialista em extração de dados de documentos brasileiros.
Sempre responda em português. Para documentos fiscais, retorne JSON válido.
Nunca invente informações ausentes na imagem."""

PARAMETER temperature 0
PARAMETER num_predict 2048
```

Esse modelo customizado pode ser referenciado pelo nome em qualquer chamada de API — prático para diferentes especializações (notas fiscais, contratos, formulários).

### 3.4 Processamento paralelo com Ollama

O Ollama processa requisições sequencialmente por padrão. Para processar múltiplos documentos em paralelo, use `ThreadPoolExecutor` com 2–3 workers (acima disso, o benefício diminui com os modelos maiores em CPU). Em GPU, o limite depende da VRAM disponível.

### 3.5 Quando usar Ollama em produção

Ollama é uma excelente escolha de produção para:
- Volumes baixos a moderados (até ~500 documentos/hora)
- Ambientes offline ou com restrições de rede
- Deploy em máquinas de usuários finais (edge)
- Times pequenos sem DevOps dedicado para gerenciar vLLM

Para volumes maiores, a falta de batching contínuo e gerenciamento avançado de memória torna o vLLM necessário.

---

## 4. vLLM — alta performance em produção

O vLLM é o framework de inferência mais eficiente para produção em escala. Ele resolve o problema fundamental dos LLMs em produção: como atender múltiplas requisições simultâneas sem desperdiçar VRAM.

### 4.1 PagedAttention — o diferencial técnico

O KV-cache (Key-Value cache da atenção) é o maior consumidor de memória em inferência de LLMs. Sistemas tradicionais alocam memória para o tamanho máximo de contexto desde o início — mesmo que a requisição real use 10% desse espaço.

O **PagedAttention** do vLLM aloca memória em páginas dinâmicas, como a memória virtual de um sistema operacional. Resultado:
- Menos desperdício de VRAM
- Mais requisições simultâneas no mesmo hardware
- Throughput 20–30x maior que inferência sequencial ingênua

### 4.2 Batching contínuo

O Ollama e HuggingFace processam requisições uma por vez (ou em batches estáticos). O vLLM usa **batching contínuo**: novas requisições entram na fila e são adicionadas ao batch em andamento à medida que outras terminam. Isso maximiza a utilização da GPU independentemente da variação de tamanho das requisições.

Para pipelines de OCR de alto volume, isso significa que enquanto uma requisição longa (documento de 50 páginas) está sendo processada, dezenas de requisições curtas podem ser atendidas em paralelo.

### 4.3 Servidor de inferência compatível com OpenAI

O vLLM expõe uma API REST compatível com a API da OpenAI. Isso significa que qualquer cliente que já usa a API da OpenAI pode ser redirecionado para o vLLM local apenas trocando a `base_url`. Para multimodais, as imagens são enviadas no formato de `image_url` — incluindo imagens em base64 como `data:image/png;base64,...`.

```bash
# Subir servidor vLLM com modelo multimodal
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-VL-7B-Instruct \
    --tensor-parallel-size 1 \
    --max-model-len 8192 \
    --limit-mm-per-prompt image=5 \
    --dtype bfloat16 \
    --port 8000
```

### 4.4 Batching assíncrono para OCR em escala

O ponto de maior ganho do vLLM para OCR é a combinação de **semáforo de concorrência + `asyncio.gather`**. O padrão correto:

1. Para cada documento, criar uma co-rotina assíncrona que chama o vLLM via cliente async
2. Controlar concorrência com `asyncio.Semaphore` para não sobrecarregar o servidor
3. Usar `asyncio.gather` para processar todas as co-rotinas em paralelo
4. O vLLM internamente usa PagedAttention para servir todas eficientemente

Com 10–20 requisições simultâneas num servidor vLLM com uma A100, um pipeline de OCR pode processar **centenas de documentos por minuto**.

### 4.5 Quantização AWQ para vLLM

O formato AWQ (Activation-aware Weight Quantization) é o recomendado para vLLM. Modelos AWQ estão disponíveis diretamente no HuggingFace Hub com o sufixo `-AWQ`:

- `Qwen/Qwen2.5-VL-7B-Instruct-AWQ` — usa ~5GB VRAM vs. ~14GB do modelo original
- Qualidade: ~97% do modelo original em tarefas de OCR
- Speedup: 1.5–2x na decodificação

Para servir com AWQ no vLLM, adicione `--quantization awq` ao comando de inicialização.

### 4.6 DeepSeek-OCR com vLLM — caso especial

O DeepSeek-OCR e DeepSeek-OCR 2 têm suporte nativo no vLLM e requerem um `NGramPerReqLogitsProcessor` especial que implementa a compressão óptica de contexto. Esse processador garante que o mecanismo de compressão funcione corretamente durante a geração — sem ele, o modelo gera saída incorreta.

O GLM-OCR também suporta vLLM via `vllm serve zai-org/GLM-OCR`, com suporte a processamento de PDFs diretamente e acesso ao caminho local de imagens via `--allowed-local-media-path`.

---

## 5. Estratégias de otimização

### 5.1 Cache de resultados por hash de documento

Documentos idênticos não devem ser processados duas vezes. O padrão é: calcular o SHA-256 do conteúdo do arquivo, verificar se existe resultado em cache, e retornar do cache ou processar e salvar. Isso é especialmente valioso em pipelines que reprocessam periodicamente a mesma base de documentos.

### 5.2 Roteamento inteligente entre modelos

Em produção, nem todo documento precisa do modelo mais poderoso. Um roteador simples pode economizar significativamente:

- **PDF born-digital com texto nativo** → extração direta com PyMuPDF (zero inferência)
- **Imagem de alta qualidade, texto simples** → GLM-OCR via Ollama (rápido, barato)
- **Documento com layout complexo** → Docling + Granite-Docling
- **Documento com imagens relevantes** → Qwen3-VL via vLLM
- **Volume alto com SLA de latência** → vLLM com batch assíncrono

O roteador usa as métricas de avaliação de qualidade da Aula 02 (nitidez, contraste) combinadas com a detecção de PDF nativo para decidir o caminho.

### 5.3 Guia de decisão consolidado

```
Estou desenvolvendo / experimentando?
  → HuggingFace Transformers localmente

Preciso de deploy simples sem gerenciar servidor?
  → Ollama. Instale, pull, sirva.

Preciso de deploy gerenciado sem infra?
  → HuggingFace Inference Endpoints

Processo < 500 documentos/hora?
  → Ollama em produção é suficiente

Processo > 500 documentos/hora com SLA definido?
  → vLLM. É o único que escala com PagedAttention e batch contínuo.

Dados sensíveis, não posso usar API externa?
  → Ollama ou vLLM on-premise, dependendo do volume
```

---

## 6. Estrutura do laboratório

### Lab 05-A — HuggingFace pipeline e inferência manual

Configure dois modelos (sugestão: Florence-2 e Qwen2.5-VL-7B) via HuggingFace Transformers, com e sem quantização 4-bit. Meça a diferença de VRAM usada, tempo de inferência e CER nos documentos do benchmark da Aula 04.

**Arquivo:** `labs/lab_05a_huggingface.py`

### Lab 05-B — Ollama com modelos de OCR

Instale o Ollama, baixe GLM-OCR e Qwen3-VL:8b. Processe os mesmos documentos e compare:
- Tempo de resposta por documento
- Qualidade do texto extraído
- Comportamento com documentos que contêm imagens

**Arquivo:** `labs/lab_05b_ollama.py`

### Lab 05-C — vLLM com batching assíncrono

Suba um servidor vLLM localmente (requer GPU) ou use um ambiente de cloud. Implemente o padrão de batching assíncrono com `asyncio.Semaphore` e processe 50 documentos. Meça e compare o throughput com o processamento sequencial via Ollama.

**Arquivo:** `labs/lab_05c_vllm_batch.py`

### Lab 05-D — Comparação de throughput

Usando os três frameworks, processe o mesmo conjunto de 20 documentos e construa uma tabela comparativa com: throughput (docs/minuto), latência média por documento, uso de VRAM e CPU. Use esse resultado para justificar a escolha de framework no projeto final.

**Arquivo:** `labs/lab_05d_throughput_comparison.py`

### Desafio extra — Docker Compose para vLLM

Crie um `docker-compose.yml` que suba um servidor vLLM com Qwen2.5-VL, um worker Python que consome documentos de uma pasta de entrada e salva os resultados JSON em uma pasta de saída. Adicione um arquivo `README.md` de deploy com instruções para reproduzir.

---

## Resumo da aula

- HuggingFace é o ponto de entrada — ideal para experimentação e controle total do processo de inferência
- Ollama simplifica radicalmente o deploy local — é a escolha para desenvolvimento, edge e volumes moderados
- vLLM é o framework de produção em escala — PagedAttention e batching contínuo são os diferenciais que justificam a complexidade adicional
- Quantização AWQ para vLLM e BitsAndBytes 4-bit para HuggingFace permitem rodar modelos grandes em hardware mais acessível
- Roteamento inteligente entre pipelines — incluindo extração direta de PDFs e diferentes modelos por complexidade — é o que diferencia um sistema de OCR eficiente de um ingênuo

---

## Referências

- [HuggingFace Transformers — Documentação](https://huggingface.co/docs/transformers/index)
- [HuggingFace Inference Endpoints](https://huggingface.co/docs/inference-endpoints/index)
- [Ollama — Documentação e modelos](https://ollama.com/)
- [Ollama — Modelos com suporte a visão](https://ollama.com/blog/vision-models)
- [GLM-OCR via Ollama](https://ollama.com/library/glm-ocr)
- [DeepSeek-OCR via Ollama](https://ollama.com/library/deepseek-ocr)
- [vLLM — Documentação oficial](https://docs.vllm.ai/en/latest/)
- [vLLM — Multimodal inputs](https://docs.vllm.ai/en/latest/usage/multimodal_inputs.html)
- [GLM-OCR — vLLM serving](https://github.com/zai-org/GLM-OCR#vllm)


## ⏭️ Próximo Passo
Próxima aula:**[Aula 06 — Pipeline de OCR em produção — projeto final](../06-final-project)**.

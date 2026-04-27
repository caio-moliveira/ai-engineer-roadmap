# Módulo 4: OCR com modelos locais e VLMs frontier

> **Objetivo:** Rodar os melhores modelos de OCR open source localmente via Ollama e comparar com os VLMs frontier (GPT-5.4 e Claude Opus 4.7) para entender o tradeoff entre custo, privacidade e qualidade.

---

## Objetivos de aprendizado

Ao final desta aula, você será capaz de:

- Rodar GLM-OCR, DeepSeek-OCR e Qwen3-VL localmente via Ollama
- Usar GPT-5.4 e Claude Opus 4.7 para OCR via LangChain
- Comparar os resultados e entender quando cada abordagem faz sentido
- Tomar decisões de arquitetura baseadas em custo, privacidade e qualidade

---

## 1. Os modelos desta aula

### Modelos locais via Ollama (gratuitos, rodam na sua GPU)

**GLM-OCR** (`ollama pull glm-ocr`) — 0.9B parâmetros, especialista em OCR puro. Lançado pela Zhipu AI em 2026, alcança o #1 no OmniDocBench V1.5 com score 94.62 — superando modelos 260x maiores. Toda a arquitetura é otimizada para transcrição e estruturação de texto. Não entende imagens embutidas no documento.

**DeepSeek-OCR** (`ollama pull deepseek-ocr`) — 3B parâmetros, especialista com **Context Optical Compression**: comprime o conteúdo visual de uma página em muito menos tokens sem perder fidelidade. Excelente para pipelines de alta escala onde custo de inferência importa.

**Qwen3-VL 8B** (`ollama pull qwen3-vl:8b`) — 8B parâmetros, VLM generalista da Alibaba. Ao contrário dos dois modelos acima, ele **entende imagens embutidas no documento**: gráficos, fotos, diagramas, logos. Suporte a 32 idiomas e contexto de 256K tokens.

### Modelos frontier via API (pagos, sem GPU necessária)

**GPT-5.4** (OpenAI) — VLM frontier com compreensão visual avançada. Entende documentos complexos com imagens, raciocina sobre o conteúdo e responde perguntas em linguagem natural. Custo por documento é relevante em volume.

**Claude Opus 4.7** (Anthropic) — VLM frontier com forte capacidade de análise de documentos longos e raciocínio estruturado. Excelente para extração de informação em documentos complexos com múltiplas páginas.

---

## 2. Especialistas vs. VLMs: a distinção que importa

### Modelos especializados em OCR (GLM-OCR, DeepSeek-OCR)

**O que fazem muito bem:**
- Alta precisão em texto impresso e estruturado
- Preservação de tabelas, fórmulas e hierarquia de layout
- Rápidos, eficientes e determinísticos
- Rodam em GPU de 4–6 GB VRAM

**O que não fazem:**
- Não entendem gráficos, fotos ou diagramas embutidos
- Não raciocinam sobre o conteúdo
- Não respondem perguntas sobre o documento

### VLMs multimodais (Qwen3-VL, GPT-5.4, Claude Opus 4.7)

**O que fazem além dos especialistas:**
- Lêem texto e entendem imagens no mesmo documento
- Raciocinam sobre o conteúdo e inferem campos ambíguos
- Respondem perguntas em linguagem natural
- Descrevem gráficos e extraem valores de barras

**O que sacrificam:**
- Mais lentos e mais caros por documento
- Menos determinísticos — podem alucinar campos
- Os modelos frontier exigem envio de dados para API externa

---

## 3. Tabela comparativa

| Modelo | Params | Entende imagens | Privacidade | Custo/pág (aprox.) | Melhor para |
|--------|--------|-----------------|-------------|---------------------|-------------|
| GLM-OCR | 0.9B | ✗ | ✓ local | Gratuito | OCR de texto puro, tabelas |
| DeepSeek-OCR | 3B | ✗ | ✓ local | Gratuito | Alta escala, compressão de tokens |
| Qwen3-VL 8B | 8B | ✓ | ✓ local | Gratuito | Docs com imagens, multilíngue |
| GPT-5.4 | — | ✓ | ✗ API | ~US$ 0,01–0,05 | Qualidade máxima, docs complexos |
| Claude Opus 4.7 | — | ✓ | ✗ API | ~US$ 0,01–0,05 | Raciocínio, documentos longos |

---

## 4. Quando usar cada abordagem

**Use GLM-OCR ou DeepSeek-OCR quando:**
- O documento é só texto e tabelas (contratos, recibos, formulários)
- Volume alto e custo de inferência importa
- Privacidade dos dados é obrigatória
- Você tem GPU disponível localmente

**Use Qwen3-VL quando:**
- O documento mistura texto com gráficos ou fotos
- Você quer privacidade local mas com compreensão visual
- Precisão em múltiplos idiomas é necessária

**Use GPT-5.4 ou Claude Opus 4.7 quando:**
- Qualidade máxima é mais importante que custo
- O documento é complexo e exige raciocínio
- Você não tem GPU disponível
- O volume é baixo o suficiente para API ser viável

---

## 5. Exemplos

### Exemplo 01 — OCR com Ollama

Roda GLM-OCR, DeepSeek-OCR e Qwen3-VL no mesmo documento e compara as saídas lado a lado. O objetivo é ver concretamente a diferença entre os especialistas (texto puro) e o VLM (texto + imagens).

```bash
ollama pull glm-ocr
ollama pull qwen3-vl:8b
```

**Arquivo:** `01_ollama.py`

### Exemplo 02 — OCR com LangChain

Usa LangChain para chamar GPT-5.4 (OpenAI) e Claude Opus 4.7 (Anthropic) no mesmo documento do Lab 04-A. A interface LangChain é idêntica para os dois provedores — isso é proposital para mostrar a portabilidade do código.

```bash
uv add langchain-openai langchain-anthropic
export OPENAI_API_KEY="sua-chave"
export ANTHROPIC_API_KEY="sua-chave"
```

**Arquivo:** `02_api_langchain.py`

---

## Resumo

- GLM-OCR e DeepSeek-OCR são os melhores para texto puro — rápidos, gratuitos, privados
- Qwen3-VL 8B é o único modelo local que entende imagens embutidas no documento
- GPT-5.4 e Claude Opus 4.7 oferecem qualidade máxima mas enviam dados para API externa
- Para 95% dos documentos corporativos (texto + tabelas), os modelos locais são suficientes e muito mais baratos
- O único caso onde a API frontier é claramente superior: documentos com muitas imagens e necessidade de raciocínio complexo

---

## Referências

- [GLM-OCR — GitHub](https://github.com/zai-org/GLM-OCR) | [arxiv 2603.10910](https://arxiv.org/abs/2603.10910)
- [DeepSeek-OCR — GitHub](https://github.com/deepseek-ai/DeepSeek-OCR) | [arxiv 2510.18234](https://arxiv.org/abs/2510.18234)
- [Qwen3-VL Technical Report — arxiv 2511.21631](https://arxiv.org/abs/2511.21631)
- [OmniDocBench — GitHub](https://github.com/opendatalab/OmniDocBench)

---

## ⏭️ Próximo Passo

**[Aula 05 — Frameworks de serving: HuggingFace, Ollama e vLLM](../05-serving-frameworks)**

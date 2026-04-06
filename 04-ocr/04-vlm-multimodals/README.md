# 🤗 Módulo 4: Modelos estado-da-arte: VLMs especializados e multimodais

> **Objetivo:** Conhecer e comparar os modelos de OCR mais relevantes de 2025–2026, entender a diferença entre modelos especializados em OCR e VLMs multimodais gerais, e usar benchmarks para tomar decisões embasadas de arquitetura.

---

## Objetivos de aprendizado

Ao final desta aula, você será capaz de:

- Distinguir modelos especializados em OCR de VLMs multimodais gerais
- Conhecer e rodar os principais modelos de 2025–2026 no seu projeto
- Entender por que VLMs multimodais conseguem processar documentos com imagens embutidas
- Decidir qual modelo usar para cada tipo de problema com base em critérios objetivos

---

## 1. A divisão fundamental: especialistas vs. generalistas

Esta é a lição mais importante da aula, e ela molda todas as decisões de arquitetura em OCR em 2026.

### 1.1 Modelos especializados em OCR

São modelos **treinados especificamente para a tarefa de reconhecimento de texto e estrutura de documentos**. Toda a arquitetura é otimizada para essa função. Exemplos: DeepSeek-OCR, Qwen3-VL, GLM-OCR.

**O que fazem muito bem:**
- Alta precisão em texto impresso
- Preservação de estrutura (tabelas, fórmulas, código)
- Alta velocidade e eficiência de tokens
- Saída determinística e consistente

**O que não fazem:**
- Não "entendem" imagens embutidas no documento (gráficos, fotos, diagramas)
- Não raciocinam sobre o conteúdo — apenas transcrevem e estruturam
- Não respondem perguntas em linguagem natural sobre o documento

### 1.2 VLMs multimodais gerais com forte capacidade de OCR

São modelos de linguagem visual de propósito geral que **aprenderam OCR como parte de um treinamento mais amplo**. Exemplos: Qwen2.5-VL, Qwen3-VL, modelos GPT-4o e praticamente todos os modelos mais novos das big techs (gpt-5 +, gemini 2.5 +, etc)

**O que fazem que os especializados não fazem:**
- Processam documentos que contêm imagens, gráficos, diagramas, logos
- Raciocinam sobre o conteúdo — podem inferir campos ausentes ou ambíguos
- Respondem perguntas em linguagem natural sobre o documento
- Entendem contexto semântico além do texto literal

**O que sacrificam:**
- Geralmente mais lentos e mais caros por documento
- Menos determinísticos — podem "alucidar" campos
- Precisam de mais tokens para processar um documento
- Mais difíceis de otimizar para alta vazão

### 1.3 Por que isso importa na prática

Considere um relatório anual de uma empresa. Ele contém: texto corrido, tabelas financeiras, gráficos de desempenho (barras, pizza), fotos dos executivos e logotipos.

- Um **modelo especializado** vai ler o texto e as tabelas excelentemente, mas vai ignorar ou gerar lixo nos gráficos e imagens.
- Um **VLM multimodal** vai ler tudo: vai descrever os gráficos, extrair os valores das barras se for bem promtado, identificar os executivos, e raciocinar sobre as relações entre o texto e as imagens.

A escolha certa depende de **o que você precisa do documento**, não apenas de qual modelo tem o CER mais baixo.

---

## 2. Modelos especializados em OCR

### 2.1 DeepSeek-OCR — compressão óptica de contexto

Lançado em outubro de 2025 pela DeepSeek, o DeepSeek-OCR traz uma inovação arquitetural distinta de todos os outros modelos desta aula: **Context Optical Compression**. Em vez de representar o conteúdo de uma página como centenas de tokens de texto, o modelo comprime visualmente essa informação em muito menos tokens.

**A inovação central:** um token visual pode representar o equivalente a 10 tokens de texto com ~97% de fidelidade. A 20x de compressão, a precisão cai para ~60% — ainda útil para muitos casos de uso. Isso tem implicações profundas para custos de inferência em escala.

**Destaques técnicos:**
- 3B parâmetros com arquitetura MoE (Mixture of Experts)
- DeepEncoder: encoder visual de alta compressão com SAM + CLIP
- Compressão de 10-20x com baixa degradação de qualidade
- 200.000+ páginas de dados de treinamento por dia em um único A100
- Suporte nativo em vLLM desde o lançamento
- Disponível via Ollama (`ollama pull deepseek-ocr`)

**Melhor para:** pipelines de alta escala onde custo de tokens é crítico, geração de dados de treinamento para LLMs.

**Referência:** [arxiv 2510.18234](https://arxiv.org/abs/2510.18234) | [GitHub deepseek-ai/DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR)

---

### 2.2 DeepSeek-OCR 2 — Visual Causal Flow

Lançado em janeiro de 2026, o DeepSeek-OCR 2 sucede o original com a arquitetura **DeepEncoder V2**, que introduz o conceito de **Visual Causal Flow**: o encoder visual processa a imagem na mesma ordem lógica que um humano leria, melhorando significativamente a performance em layouts complexos.

**Novidades em relação ao original:**
- DeepEncoder V2 com processamento visual na ordem de leitura humana
- Melhor performance em layouts multi-coluna e tabelas complexas
- Prompts especializados para diferentes tarefas: conversão para Markdown (`<|grounding|>Convert the document to markdown.`), OCR livre (`Free OCR.`), análise de figuras (`Parse the figure.`)
- 3B parâmetros, compatível com transformers e vLLM

**Melhor para:** documentos com layouts complexos onde a ordem de leitura é crítica para o resultado correto.

**Referência:** [arxiv 2601.20552](https://arxiv.org/abs/2601.20552) | [HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-OCR-2)

---

### 2.3 GLM-OCR — menor modelo, melhor benchmark

Lançado pela Zhipu AI (Z.ai) em fevereiro de 2026, o GLM-OCR é talvez o resultado mais surpreendente desta geração: **0.9B parâmetros que alcançam o #1 no OmniDocBench V1.5 com score 94.62**, superando Gemini 3 Pro (90.33) e Qwen3-VL-235B (89.15) — modelos 260x maiores.

**Por que um modelo tão pequeno consegue isso?** Especialização radical. Ao contrário dos VLMs gerais que fazem tudo, o GLM-OCR foi projetado **exclusivamente** para extração e estruturação de texto de documentos.

**Arquitetura:**
- 0.4B CogViT visual encoder pré-treinado em dados de documentos
- 0.5B GLM language decoder
- Conector cross-modal com downsampling eficiente de tokens
- Pipeline de dois estágios: PP-DocLayout-V3 para análise de layout → reconhecimento paralelo por região

**Multi-Token Prediction (MTP):** em vez de prever um token por vez (autoregressive padrão), o GLM-OCR prevê múltiplos tokens por passo. Resultado: **50% de ganho em throughput de decodificação** — especialmente valioso em OCR, onde a saída é altamente determinística.

**Performance:**
- OmniDocBench V1.5: 94.62 (#1 geral)
- OCRBench (Text): 94.0
- UniMERNet (fórmulas): 96.5
- TEDS_TEST (tabelas): 86.0
- Throughput: 1.86 páginas/segundo (PDF) em hardware único
- Custo via API: US$ 0.03 por milhão de tokens

**Deployment:**
- vLLM, SGLang e Ollama (`ollama run glm-ocr`)
- SDK oficial: `pip install glmocr`
- MIT License — uso comercial livre
- Fine-tuning guide disponível (LLaMA-Factory)
- Roda em GPU com 4GB VRAM

**Onde o GLM-OCR perde:** texto manuscrito (vs. Gemini 3 Pro) e tabelas muito complexas com headers aninhados (vs. PaddleOCR-VL 1.5 em TextEdit). Para OCR puro de documentos impressos estruturados, é o melhor open source disponível em abril de 2026.

**Referência:** [arxiv 2603.10910](https://arxiv.org/abs/2603.10910) | [GitHub zai-org/GLM-OCR](https://github.com/zai-org/GLM-OCR) | [HuggingFace](https://huggingface.co/zai-org/GLM-OCR)

---

## 3. VLMs multimodais com forte capacidade de OCR

### 3.1 A família Qwen-VL: evolução em 3 gerações

A Alibaba lançou três gerações de VLMs focados em documentos em menos de 14 meses — cada uma com melhorias significativas em OCR e compreensão de documentos.

**Qwen2-VL (setembro/2024):** introduziu o conceito de resolução dinâmica, onde o modelo se adapta automaticamente à resolução da imagem sem forçar redimensionamento fixo. Isso foi um salto importante para documentos de alta resolução.

**Qwen2.5-VL (janeiro/2025):** melhorias substanciais em compreensão de documentos e diagramas, suporte a geração de bounding boxes em JSON, capacidade de agir como agente visual (interagir com interfaces). O modelo 7B supera o GPT-4o-mini em vários benchmarks de documentos. O 72B é competitivo com os melhores modelos fechados.

**Qwen3-VL (outubro/2025):** a versão mais recente e mais capaz. Introduz:
- Contexto nativo de 256K tokens (texto + imagens intercalados)
- Variantes densas (2B, 4B, 8B, 32B) e MoE (30B-A3B, 235B-A22B)
- OCR expandido para 32 idiomas (vs. 10 anteriores)
- Robustez a baixa luminosidade, desfoque e inclinação
- **DeepStack:** fusão de features multi-nível do ViT para capturar detalhes finos
- Modo "thinking" para raciocínio mais profundo antes de responder

**Por que a família Qwen-VL importa para OCR:** esses modelos são os melhores **generalistas** — eles lêem o texto, entendem os gráficos, descrevem as imagens e raciocinam sobre o documento como um todo. Para documentos que misturem todos esses elementos, não há alternativa melhor open source.

**Referências:**
- [Qwen2.5-VL Technical Report](https://arxiv.org/abs/2502.13923)
- [Qwen3-VL Technical Report](https://arxiv.org/abs/2511.21631)
- [HuggingFace Qwen3-VL](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct)

---


### 3.2 Mistral OCR — API de alta precisão

Lançado pela Mistral em março de 2025, o Mistral OCR é um serviço de API específico para OCR de documentos. Diferente dos outros modelos desta aula, ele é **fechado** — acessado apenas via API.

**Destaques:**
- Alta precisão especialmente em PDFs de múltiplas páginas
- Preservação de estrutura (tabelas, colunas, fórmulas) em Markdown
- Aceita PDFs diretamente sem rasterização prévia
- Suporte nativo a documentos com imagens embutidas

**Quando faz sentido:** quando privacidade de dados não é uma restrição e você quer qualidade máxima sem gerenciar infraestrutura. O custo por página é relevante para volumes altos.

**Referência:** [Mistral OCR — Anúncio](https://mistral.ai/news/mistral-ocr) | [Documentação](https://docs.mistral.ai/capabilities/document/)

---

## 4. Tabela comparativa de modelos

| Modelo | Params | Tipo | Entende imagens no doc | Open Source | Melhor para |
|--------|--------|------|----------------------|-------------|-------------|
| Tesseract 5 | — | Clássico | ✗ | ✓ | Texto simples, sem GPU |
| EasyOCR | ~100M | DL | ✗ | ✓ | Multilíngue sem GPU |
| DeepSeek-OCR 2 | 3B | Especializado | ✗ | ✓ | Alta compressão, escala |
| GLM-OCR | 0.9B | Especializado | ✗ | ✓ | Melhor CER/tamanho, tabelas |
| Qwen2.5-VL 7B | 7B | VLM | ✓ | ✓ | Docs + imagens, extração |
| Qwen3-VL 8B | 8B | VLM | ✓ | ✓ | Raciocínio, docs complexos |
| Mistral OCR | — | API | ✓ | ✗ | Alta precisão, sem infra |

---

## 5. Benchmarks — como comparar de forma honesta

### 5.1 OmniDocBench — o benchmark mais abrangente em 2026

O OmniDocBench é o benchmark mais completo e atualizado para avaliação de modelos de OCR e Document AI. Avalia:

- Transcrição de texto (normalização de edição)
- Reconhecimento de fórmulas matemáticas
- Reconhecimento de tabelas (TEDS — Tree-Edit-Distance Score)
- Reconhecimento de texto em gráficos
- Análise de layout e ordem de leitura

É o benchmark usado para comparar o GLM-OCR, Qwen3-VL, DeepSeek-OCR 2 e outros modelos lançados em 2025–2026. Reportar resultados no OmniDocBench é o padrão atual da área.

### 5.2 Benchmarks clássicos ainda relevantes

**FUNSD** (200 formulários): avalia extração de entidades em formulários com layout irregular. Métrica principal: F1 de palavras.

**SROIE** (1.000 recibos): avalia extração de campos específicos (empresa, data, endereço, total). Bom para testar extração estruturada.

**DocVQA** (50.000 pares Q&A): avalia compreensão de documentos via perguntas. Métrica: ANLS (Average Normalized Levenshtein Similarity).

**OCRBench:** benchmark específico para avaliação de modelos de OCR em texto impresso e cenas naturais.

### 5.3 Estratégia de avaliação em produção

Benchmarks públicos são necessários mas não suficientes. Um modelo que lidera o FUNSD pode falhar em notas fiscais brasileiras com fontes específicas. A estratégia correta:

1. Use benchmarks públicos para **filtrar candidatos** — elimine modelos claramente inferiores
2. Crie um **benchmark interno** com 50–100 documentos representativos do seu domínio
3. Avalie todos os candidatos finalistas no seu benchmark interno
4. Meça não só CER mas também **latência, custo por documento e taxa de falha** em documentos difíceis
5. Analise qualitativamente os piores casos — eles revelam problemas sistemáticos

---

## 6. O documento com imagens: onde os especialistas falham

Este tópico merece atenção especial porque é um dos mal-entendidos mais comuns na área.

### O problema

Um contrato com um gráfico de evolução financeira. Um relatório com fotos e infográficos. Uma nota técnica com diagramas de arquitetura. Para esses documentos, a questão não é só *"qual é o texto?"* mas *"o que este gráfico mostra?"* e *"como as imagens se relacionam com o texto?"*.

Modelos especializados em OCR (GOT-OCR2, DeepSeek-OCR 2, GLM-OCR) vão ler o texto excelentemente mas serão cegos para o conteúdo visual não-textual. Eles podem até tentar "ler" pixels de uma imagem como se fosse texto — gerando saída inválida.

### A solução: VLMs multimodais

O Qwen3-VL, com contexto de 256K tokens e processamento intercalado de imagens e texto, pode:
- Ler todo o texto do documento
- Descrever os gráficos e infográficos
- Extrair valores de gráficos de barras se promtado corretamente
- Relacionar imagens com o texto ao redor
- Responder perguntas que cruzam informação textual e visual

Isso é o que significa **multimodal** no sentido pleno: não apenas aceitar imagens, mas realmente compreender e integrar múltiplas modalidades de informação.

---

## 7. Estrutura do laboratório

### Lab 04-A — Benchmark comparativo de modelos especializados

Usando o mini-dataset criado na Aula 02 (e o SROIE público), rode pelo menos 3 modelos especializados — sugestão: GLM-OCR, DeepSeek-OCR 2 e Qwen3-VL — nos mesmos documentos. Construa uma tabela comparativa com CER, WER, tempo de execução e uso de memória. Identifique os casos em que cada modelo performa melhor ou pior.

**Arquivo:** `labs/lab_04a_benchmark_especialistas.py`

### Lab 04-B — VLMs multimodais em documentos com imagens

Pegue um documento que contenha texto **e** gráficos ou imagens relevantes. Processe com um modelo especializado (GLM-OCR ou DeepSeek-OCR 2) e com um VLM multimodal (Qwen2.5-VL ou Qwen3-VL). Compare:

- Qualidade do texto extraído
- O que cada modelo faz com as imagens/gráficos
- Capacidade de responder perguntas que cruzam texto e visual

**Arquivo:** `labs/lab_04b_vlm_multimodal.py`

### Lab 04-C — GLM-OCR via Ollama (lab de produção)

Use o GLM-OCR via Ollama localmente. Processe 20 documentos do SROIE, meça throughput real (páginas/segundo), custo de VRAM e compare com o baseline do Tesseract (Aula 01). Observe como o GLM-OCR performa em recibos — que é exatamente o tipo de documento para o qual ele tem bons resultados em benchmarks.

**Arquivo:** `labs/lab_04c_glm_ocr_ollama.py`

### Desafio extra — Mistral OCR vs. GLM-OCR

Se você tiver acesso à API da Mistral, compare os resultados com o GLM-OCR local em 10 documentos complexos. Calcule o custo por documento para o Mistral OCR e projete o custo mensal para diferentes volumes de processamento. Quando o custo da API justifica o custo da infraestrutura local?

---

## Resumo da aula

- Modelos especializados (GLM-OCR, DeepSeek-OCR 2) são os melhores para texto — mas são cegos para imagens embutidas no documento
- VLMs multimodais (Qwen2.5-VL, Qwen3-VL) entendem todo o documento — texto, gráficos, imagens — e raciocinam sobre ele
- GLM-OCR é o modelo open source de melhor performance para OCR puro em abril de 2026: 0.9B parâmetros, #1 no OmniDocBench, 1.86 pág/s
- DeepSeek-OCR 2 introduz compressão óptica que muda o custo de tokens em pipelines de escala
- A família Qwen3-VL representa o melhor VLM generalista com 256K de contexto e suporte a 32 idiomas
- Benchmarks públicos filtram candidatos, mas o benchmark interno com dados do seu domínio é o que determina a decisão final

---

## Referências

- [GLM-OCR — GitHub](https://github.com/zai-org/GLM-OCR) | [artigo arxiv 2603.10910](https://arxiv.org/abs/2603.10910)
- [GLM-OCR — HuggingFace](https://huggingface.co/zai-org/GLM-OCR)
- [DeepSeek-OCR — artigo arxiv 2510.18234](https://arxiv.org/abs/2510.18234)
- [DeepSeek-OCR 2 — artigo arxiv 2601.20552](https://arxiv.org/abs/2601.20552)
- [DeepSeek-OCR — GitHub](https://github.com/deepseek-ai/DeepSeek-OCR)
- [Qwen2.5-VL Technical Report — arxiv 2502.13923](https://arxiv.org/abs/2502.13923)
- [Qwen3-VL Technical Report — arxiv 2511.21631](https://arxiv.org/abs/2511.21631)
- [Qwen3-VL — GitHub](https://github.com/QwenLM/Qwen3-VL)
- [Mistral OCR — Documentação](https://docs.mistral.ai/capabilities/document/)
- [OmniDocBench — GitHub](https://github.com/opendatalab/OmniDocBench)

---
## ⏭️ Próximo Passo
Próxima aula:**[Aula 05 — Frameworks de serving: HuggingFace, Ollama e vLLM](../05-serving-frameworks)**.

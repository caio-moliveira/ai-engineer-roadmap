# 📄 Módulo 1: Fundamentos de OCR

> **Objetivo:** entender o que é OCR, suas fronteiras com tecnologias adjacentes e como escolher a abordagem certa em projetos reais.

---

## Objetivos de aprendizado

Ao final desta aula, você será capaz de:

- Explicar o que é OCR e por que ele importa em projetos reais
- Distinguir OCR de Visão Computacional, Document Intelligence e Modelos Multimodais
- Conhecer os principais modelos atuais de cada categoria
- Escolher a abordagem certa para cada tipo de problema

---

## 1. O que é OCR

OCR (Optical Character Recognition) é a tecnologia que converte texto presente em imagens em texto digital manipulável por computadores. Sua importância está em tornar acessível o conhecimento que permanece em formatos não estruturados — contratos, formulários, recibos e prontuários — viabilizando busca, análise e uso por sistemas de IA.

## 2. Pontos importantes

OCR não é uma tecnologia única, mas uma família de técnicas, indo de algoritmos clássicos como Tesseract até modelos modernos como CRNN, TrOCR e Donut. Tipicamente se divide em duas tarefas: detecção de texto e reconhecimento de texto.

A qualidade da entrada é crítica — resolução, iluminação e ruído impactam diretamente o desempenho. As métricas mais usadas são CER (Character Error Rate) e WER (Word Error Rate), complementadas por métricas de negócio em projetos reais.

OCR é um meio, não um fim. Raramente é suficiente sozinho em ambientes corporativos, o que motivou o surgimento de categorias adjacentes como Document Intelligence.

## 3. Por que distinguir OCR de outras categorias

Existe confusão recorrente entre OCR, Visão Computacional, Document Intelligence e Modelos Multimodais. Essa confusão leva a escolhas técnicas equivocadas, gerando custo desnecessário, latência elevada e resultados aquém do esperado. Compreender o escopo e a saída de cada categoria é essencial para escolher bem.

## 4. OCR como modelo vs. OCR como pipeline

O **pipeline modular** decompõe o problema em etapas independentes (detecção, recorte, reconhecimento, pós-processamento). Oferece flexibilidade, interpretabilidade e debug fácil. Exemplos: PaddleOCR, docTR.

O **end-to-end** usa uma única rede neural da imagem ao texto. Ganha em simplicidade, mas perde em interpretabilidade e exige mais dados de treino. Exemplos: TrOCR, Donut.

A escolha depende de volume de dados, exigência de explicabilidade, customização e latência.

## 5. OCR vs. Visão Computacional

Visão Computacional é o campo amplo que extrai informação de imagens em geral — classificação, detecção de objetos, segmentação. OCR é um subcampo dela, especializado em texto.

**Modelos atuais de Visão Computacional:** RF-DETR, YOLOv12, SAM 3, DINOv2, GroundingDINO.

**Modelos atuais de OCR dedicado:** PaddleOCR-VL, GLM-OCR, DeepSeek-OCR, dots.ocr, Mistral OCR, olmOCR.

Sistemas reais combinam as duas. Em leitura de placas de veículos, por exemplo, a Visão Computacional localiza a placa e o OCR lê o conteúdo.

## 6. OCR vs. Document Intelligence

Document Intelligence vai além da extração de texto, compreendendo estrutura, campos, entidades e layout, e produzindo saída estruturada. A diferença essencial está na saída: OCR entrega texto bruto, Document Intelligence entrega dados estruturados como pares chave-valor, tabelas e entidades.

**Plataformas em nuvem:** Amazon Textract, Google Document AI, Azure AI Document Intelligence, ABBYY FineReader.

**Agêntico e open source:** LlamaParse, Docling (IBM), LayoutLMv3, Donut.

Document Intelligence quase sempre usa OCR internamente, somando modelagem de layout, modelos de linguagem e regras de negócio.

## 7. OCR vs. Modelos Multimodais

Modelos Multimodais (Vision Language Models) processam texto e imagem simultaneamente e respondem em linguagem natural. Realizam OCR como uma de suas capacidades e brilham em cenários complexos que exigem raciocínio sobre o conteúdo.

**Modelos atuais:** Claude Opus, Gemini 3.1 Pro, GPT-5, Qwen3-VL, DeepSeek-VL, InternVL.

Têm desvantagens importantes: custo elevado, maior latência, risco de alucinação e menor auditabilidade. São indicados para baixo volume e alta complexidade semântica, enquanto soluções dedicadas vencem em alto volume e baixa complexidade.

> **Observação:** em benchmarks recentes como o OmniDocBench, modelos especializados menores frequentemente superam generalistas de fronteira em OCR puro. Foco vence generalidade quando o problema é estreito.

## 8. Outras categorias relevantes

- **HTR** (Handwritten Text Recognition) — reconhecimento de texto manuscrito
- **STR** (Scene Text Recognition) — texto em cenas naturais como placas e embalagens
- **KIE** (Key Information Extraction) — extração de campos pré-definidos
- **Document Layout Analysis** — decomposição estrutural do documento

## 9. Síntese comparativa

Em escopo, do mais amplo ao mais restrito: Visão Computacional, OCR (e suas especializações HTR e STR), Document Intelligence (com KIE como sub-especialização). Modelos Multimodais ocupam posição transversal, podendo realizar todas as tarefas.

Em saída: OCR entrega texto, Document Intelligence entrega dados estruturados, Visão Computacional entrega objetos ou regiões e Modelos Multimodais entregam respostas em linguagem natural.

A escolha em projetos reais deve partir da pergunta: **qual saída o sistema a jusante precisa?** E frequentemente envolve combinar mais de uma categoria em um pipeline integrado.

---

## ⏭️ Próximo passo

Próxima aula: **[Aula 02 — Dados, pré-processamento e anotação](../02-ocr-pipelines)**
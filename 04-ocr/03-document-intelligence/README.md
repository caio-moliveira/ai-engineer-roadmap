# 🏭 Módulo 3: Document Intelligence

> **Objetivo:** Evoluir do OCR de caracteres para compreensão de documentos. Dominar PaddleOCR para extração estruturada local, entender o Azure AI Document Intelligence como serviço gerenciado de produção, e aprender a usar o Docling como framework de ingestão de documentos para pipelines de IA.

---

## Objetivos de aprendizado

Ao final desta aula, você será capaz de:

- Explicar a diferença entre OCR clássico e Document Intelligence
- Usar PaddleOCR para detecção e reconhecimento de texto estruturado localmente
- Usar o Azure AI Document Intelligence com modelos prebuilt e entender seus modelos disponíveis
- Usar o Docling para converter documentos complexos em formatos prontos para IA
- Integrar Docling com LangChain e LlamaIndex para pipelines de RAG
- Decidir entre solução local (PaddleOCR + Docling) e gerenciada (Azure) para cada cenário

---

## 1. Da leitura de texto à compreensão de documentos

Até a Aula 02, trabalhamos com a pergunta: *"Qual é o texto nesta imagem?"*

A partir desta aula, a pergunta muda para: *"O que este documento contém e como está organizado?"*

Considere uma nota fiscal. O Tesseract pode ler todos os caracteres corretamente e ainda assim produzir um resultado inútil para extração de dados, porque não sabe que "R$ 1.234,56" é o valor total — não um número qualquer. Não sabe que o CNPJ do emissor está no cabeçalho. Não consegue reconstruir a tabela de itens com colunas corretas. Devolve tudo como texto linear, perdendo qualquer estrutura da página.

Document Intelligence resolve **compreensão de layout e estrutura**. As ferramentas desta aula representam a segunda geração — a ponte entre OCR clássico e os VLMs da Aula 04.

### O espectro de soluções nesta aula

```
Local + Open Source                          Gerenciado + API
─────────────────────────────────────────────────────────────
PaddleOCR          Docling           Azure AI Document Intelligence
(rápido, local,    (ingestão para    (sem infra, prebuilt models,
 detecção precisa)  IA / RAG)         enterprise, pay-per-page)
```

As três ferramentas não são concorrentes — elas se complementam dependendo do cenário.

---

## 2. PaddleOCR — OCR multilíngue de alta performance

O PaddleOCR, desenvolvido pela Baidu, é um dos frameworks de OCR mais usados em produção, especialmente para idiomas não-latinos e documentos com layouts variados. Diferente do Tesseract, ele **separa explicitamente** detecção (onde está o texto?) de reconhecimento (qual é o texto?), usando modelos neurais otimizados para cada etapa.

### 2.1 Arquitetura

**Detecção:** o modelo DB (Differentiable Binarization) detecta regiões de texto como mapas de probabilidade e produz bounding boxes de alta precisão mesmo para texto curvado ou irregular.

**Classificação de ângulo:** modelo adicional que detecta texto rotacionado (180°) e corrige antes do reconhecimento.

**Reconhecimento:** SVTR (Scene Vision Transformer Recognition) ou modelos baseados em atenção reconhecem o texto em cada região detectada.

### 2.2 O que o PaddleOCR faz melhor que o Tesseract

- Detecção muito mais robusta em texto irregular, curvado ou em múltiplas orientações
- Suporte nativo a dezenas de idiomas sem configuração adicional
- Score de confiança por região, não só por palavra
- Melhor performance em documentos com layout misto — texto + tabelas + imagens
- Saída com coordenadas precisas de cada região, útil para extração posicional

### 2.3 Saída e estruturação

A saída do PaddleOCR inclui para cada região: as quatro coordenadas do bounding box, o texto reconhecido e o score de confiança. Ordenando os resultados por posição (y, depois x), é possível reconstruir a ordem de leitura — o que o Tesseract não faz de forma confiável em documentos multicoluna.

### 2.4 Quando usar PaddleOCR

PaddleOCR é a escolha certa quando você precisa de **OCR estruturado com posicionamento preciso** que **rode completamente local**, especialmente em documentos multilíngues ou com texto em múltiplas orientações. Ele não entende semântica, mas entende posição — já é um grande avanço sobre o Tesseract.

---

## 3. Azure AI Document Intelligence

O Azure AI Document Intelligence (anteriormente Azure Form Recognizer) é o serviço gerenciado da Microsoft para extração inteligente de informações de documentos. É uma API de produção que não requer gerenciamento de infraestrutura, GPU ou modelos — você envia o documento, o serviço processa e retorna JSON estruturado.

### 3.1 Por que ele importa no mundo real

Para a maioria das empresas que trabalham com automação de documentos, o Azure AI Document Intelligence é a escolha de produção padrão porque:

- **Zero infraestrutura:** não é necessário gerenciar GPU, containers ou modelos
- **Escalabilidade automática:** processa picos de volume sem configuração adicional
- **Modelos prontos para uso:** faturas, recibos, identidades, contratos, formulários fiscais — sem treinamento
- **SLA enterprise:** garantias de disponibilidade para ambientes corporativos
- **Conformidade e segurança:** ISO 27001, SOC 2, GDPR, processamento regional de dados

O trade-off: custo por página e dependência de conectividade com a nuvem Azure.


### 3.2 Preços e tier gratuito

O Azure AI Document Intelligence tem um **tier gratuito (F0)** com 500 páginas por mês sem custo — suficiente para desenvolvimento e testes. Os preços do tier pago (S0):

| Modelo | Custo aproximado |
|--------|-----------------|
| Read e Layout | US$ 1,50 por 1.000 páginas |
| Modelos prebuilt (invoice, receipt, ID...) | US$ 10,00 por 1.000 páginas |
| Custom model — análise | US$ 10,00 por 1.000 páginas |
| Custom model — treinamento | US$ 0,50 por hora de compute |

Para volumes acima de 1 milhão de páginas/mês, descontos são aplicados automaticamente.

### 3.3 Quando usar Azure vs. soluções locais

| Critério | Azure AI Doc. Intelligence | PaddleOCR + Docling |
|----------|---------------------------|---------------------|
| Infraestrutura necessária | Zero | GPU recomendada |
| Custo fixo | Nenhum | Hardware/cloud |
| Custo por volume alto | Alto (por página) | Baixo (marginal) |
| Privacidade de dados | Dados vão para nuvem MS | 100% local |
| Tabelas complexas | Excelente | Bom (Docling) |
| Setup inicial | 15 minutos | Horas |
| Manutenção de modelos | Zero | Atualizações periódicas |
| Documentos tipificados (NF, recibo, ID) | Excelente (modelos prebuilt) | Requer customização |

**Regra prática:** ambiente Azure + volume variável + documentos tipificados + sem restrição de privacidade → Azure AI Document Intelligence. Volume alto e previsível + restrições de dados + customização profunda → PaddleOCR + Docling.

---

## 4. Docling — o framework para documentos prontos para IA

O Docling é o framework mais completo desta aula. Desenvolvido pelo time de IA do IBM Research Zurich e atualmente hospedado na LF AI & Data Foundation, ele foi criado para resolver um problema específico: **transformar documentos complexos em formatos que modelos de linguagem consigam consumir com fidelidade**.

A proposta do Docling vai além do OCR. Ele é um **conversor de documentos** que entende estrutura, preserva hierarquia e exporta em formatos otimizados para IA.

### 4.1 O que o Docling resolve que OCR simples não resolve

Quando você extrai texto de um PDF com PyMuPDF ou roda OCR com Tesseract, você obtém texto plano. Mas documentos têm estrutura: cabeçalhos com hierarquia, tabelas com linhas e colunas e headers aninhados, figuras com legendas associadas, código com formatação preservada, fórmulas matemáticas, e ordem de leitura correta em layouts multicoluna.

O Docling preserva toda essa estrutura em um formato unificado chamado **DoclingDocument**, exportável para Markdown, JSON, HTML e DocTags.

### 4.2 Formatos de entrada suportados

PDF (scaneado e born-digital), DOCX, PPTX, XLSX, HTML, imagens (PNG, TIFF, JPEG), LaTeX, XML (patentes USPTO, artigos JATS, relatórios XBRL), e áudio (WAV, MP3) via ASR integrado.

### 4.3 Modelos internos

**DocLayNet:** análise de layout — identifica regiões da página (texto, tabela, figura, código, fórmula, cabeçalho).

**TableFormer:** reconstrução de estrutura de tabelas, incluindo headers aninhados e células mescladas. É notavelmente melhor que qualquer abordagem genérica para tabelas.

**Granite-Docling (258M):** VLM compacto da IBM que pode substituir múltiplos modelos especializados em uma passagem única. Usa o formato **DocTags** — linguagem de marcação criada para representar documentos de forma compacta e estruturada para LLMs.

**Motor de OCR configurável:** EasyOCR, Tesseract ou outros — substituível sem mudar o restante da pipeline.

### 4.4 DocTags e Granite-Docling

DocTags é o formato interno que codifica texto, estrutura e posição em um único formato com tags explícitas para cada tipo de elemento (`<section>`, `<table>`, `<figure>`, `<formula>`, `<code>`) junto com coordenadas de bounding box.

O **Granite-Docling-258M** gera DocTags diretamente, consolidando layout, OCR, tabelas, fórmulas e código em uma única passagem, com qualidade comparável a modelos muito maiores para document parsing. Open source sob Apache 2.0.

### 4.5 Integração com ecossistema de IA

- **LangChain** — `DoclingLoader` como document loader direto
- **LlamaIndex** — `DoclingReader` e `DoclingNodeParser` para chunking estruturado por seção
- **Crew AI** e **Haystack**
- Bases vetoriais (ChromaDB, Weaviate, Qdrant) via exportação JSON

### 4.6 Por que Docling melhora o RAG vs. texto plano

Texto plano extraído por OCR simples degrada a qualidade do RAG porque: tabelas chegam como texto desordenado, seções são cortadas arbitrariamente por limite de tokens, a hierarquia de headings desaparece, e legendas se separam das figuras. Com Docling, todos esses problemas são resolvidos antes do documento chegar ao embedding.

### 4.7 Quando usar cada ferramenta desta aula

| Critério | PaddleOCR | Azure AI Doc. Intel. | Docling |
|----------|-----------|---------------------|---------|
| Texto simples posicionado | ✓ | ✓ | ✓ |
| Tabelas estruturadas | Limitado | Excelente | Excelente |
| Hierarquia de seções | — | ✓ | ✓ |
| Destino: RAG / LLM | — | Parcial | ✓ (nativo) |
| Documentos tipificados (NF, ID, recibo) | — | ✓ (prebuilt) | — |
| Sem dependência de API | ✓ | — | ✓ |
| Setup em 15 minutos | — | ✓ | — |
| Múltiplos formatos de entrada | Imagem | PDF + Imagem + Office | Tudo |

---

## 5. Quando usar VLMs em vez de Document Intelligence

Use frameworks de Document Intelligence (PaddleOCR, Docling, Azure) quando o documento tem estrutura previsível, você precisa de bounding boxes para extração posicional, ou privacidade exige execução local.

Use VLMs (Aula 04) quando o documento contém imagens, gráficos ou diagramas relevantes para extração; o conteúdo é ambíguo e requer raciocínio; você precisa de Q&A em linguagem natural; ou a variedade de tipos de documento é alta demais para regras explícitas.

A combinação mais poderosa: **Azure AI Document Intelligence para documentos tipificados + Docling para ingestão RAG + VLM para documentos com conteúdo visual ou semântica complexa**.

---

## 6. Estrutura do laboratório

### Lab 03-A — PaddleOCR com visualização estruturada

Processe os documentos da Aula 01 com o PaddleOCR. Compare os bounding boxes detectados com os erros do Tesseract. Foque especialmente em documentos multicoluna ou com texto em ângulo.

**Arquivo:** `labs/lab_03a_paddleocr.py`

### Lab 03-B — Azure AI Document Intelligence com modelos prebuilt

Configure um recurso no portal Azure (tier gratuito F0 é suficiente para o lab). Processe um conjunto de documentos com pelo menos três modelos: `prebuilt-read`, `prebuilt-layout` e `prebuilt-invoice`. Para cada modelo, inspecione o JSON de saída completo e compare a qualidade de extração de tabelas com os resultados anteriores de Tesseract e EasyOCR.

**Arquivo:** `labs/lab_03b_azure_document_intelligence.py`

### Lab 03-C — Azure Query Fields e campos personalizados

Use o `prebuilt-layout` com query fields em português para extrair campos específicos de documentos sem modelo prebuilt dedicado. Defina campos como "Razão social do emitente", "Data de vencimento" e "Valor líquido". Avalie a precisão da extração via IA generativa do Azure vs. extração por regex do pós-processamento.

**Arquivo:** `labs/lab_03c_azure_query_fields.py`

### Lab 03-D — Docling end-to-end com RAG (lab principal)

1. Converter um PDF complexo com o Docling (relatório com tabelas, imagens e múltiplas seções)
2. Exportar para Markdown e JSON e inspecionar a estrutura preservada
3. Comparar com a extração via Azure `prebuilt-layout` do mesmo documento
4. Usar o `DoclingLoader` do LangChain para criar um pipeline de Q&A com Ollama
5. Fazer 3 perguntas ao pipeline e avaliar a qualidade das respostas

**Arquivo:** `labs/lab_03d_docling_rag.py`

### Desafio extra — pipeline híbrido com roteamento

Construa um roteador que classifica o tipo de documento e escolhe a ferramenta:
- Nota fiscal / recibo → Azure `prebuilt-invoice` ou `prebuilt-receipt`
- Documento genérico para RAG → Docling + ChromaDB + Q&A
- Imagem simples com texto → PaddleOCR

---

## Resumo da aula

- PaddleOCR separa detecção e reconhecimento com modelos neurais — ideal para solução local com layout variado
- Azure AI Document Intelligence é o serviço gerenciado de referência para produção — modelos prebuilt para documentos tipificados, zero infra, pay-per-page, com output em Markdown para RAG
- O modelo `prebuilt-layout` com saída em Markdown preserva estrutura de tabelas e hierarquia — direto para ingestão em RAG
- Query fields permitem extração de campos em linguagem natural sem treinar modelos customizados
- Docling é o framework mais completo para ingestão de documentos em pipelines de IA — TableFormer, DocLayNet e Granite-Docling resolvem o que OCR simples não consegue
- Azure e Docling se complementam: Azure para documentos tipificados, Docling para conteúdo livre em RAG

---

## Referências

- [Azure AI Document Intelligence — Documentação oficial](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [Azure AI Document Intelligence — What's New](https://learn.microsoft.com/azure/ai-services/document-intelligence/whats-new)
- [Azure AI Document Intelligence — Preços](https://azure.microsoft.com/pricing/details/ai-document-intelligence/)
- [Azure AI Document Intelligence Studio](https://documentintelligence.ai.azure.com/studio)
- [azure-ai-documentintelligence — PyPI](https://pypi.org/project/azure-ai-documentintelligence/)
- [Docling — Documentação oficial](https://docling-project.github.io/docling/)
- [Docling — GitHub](https://github.com/docling-project/docling)
- [Granite-Docling-258M — HuggingFace](https://huggingface.co/ibm-granite/granite-docling-258M)
- [IBM — Granite-Docling announcement](https://www.ibm.com/new/announcements/granite-docling-end-to-end-document-conversion)
- [Docling Technical Report (arxiv 2408.09869)](https://arxiv.org/abs/2408.09869)
- [LangChain — DoclingLoader](https://python.langchain.com/docs/integrations/document_loaders/docling/)
- [PaddleOCR — Documentação](https://paddlepaddle.github.io/PaddleOCR/latest/en/index.html)

---
Próxima aula:**[Aula 04 — VLMs especializados e multimodais](../04-vlm-multimodals)**

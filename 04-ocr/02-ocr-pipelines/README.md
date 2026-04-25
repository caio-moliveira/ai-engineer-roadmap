# 🏭 Módulo 2: Pipelines de OCR no Mundo Real

> **Goal:** Evoluir da teoria das ferramentas para a construção de uma esteira robusta de processamento ("Fábrica de Documentos"), resolvendo os problemas feios do mundo real.  
> **Status:** Mão na massa.

## 1. O Problema Bilionário: A Prisão do Papel
Apesar de toda a transformação digital, setores chave como **Judiciário, Saúde e Setor Público** ainda estão afogados em dados não estruturados.
- **Saúde:** Prontuários escritos à mão, relatórios laboratoriais confusos e guias médicas (TISS) preenchidas incorretamente.
- **Judiciário:** Processos físicos gigantescos escaneados sem indexação, páginas faltando ou de cabeça para baixo, carimbos ilegíveis mascarando textos críticos.
- **Setor Público e Backoffice:** Diários oficiais mal formatados, certidões e Notas Fiscais com variação infinita de layout.

### A Revolução do OCR (Document Intelligence)
Fazer OCR não é apenas extrair texto bruto de imagens (`Text = Tesseract(Image)`). A verdadeira revolução é a evolução do OCR para **Document Intelligence** — onde não apenas extraímos a string "João da Silva", mas compreendemos que "João da Silva" é a entidade `nome_paciente`, estruturamos isso num formato JSON/Pydantic e injetamos em um banco de dados ou alimentamos uma pipeline de RAG.

## 2. A Realidade das Trincheiras
Quando seu código encontrar o mundo exterior, as APIs vão quebrar e os algoritmos ficarão confusos se você não tratar os "gremlins" dos documentos físicos:
*   **Skewness (Desalinhamento):** O estagiário ou o cartorário colocou o papel torto no scanner. O OCR lerá linhas misturadas.
*   **Ruído / Qualidade Baixa:** DPI < 150, marcas de carimbo por cima de assinaturas, manchas de café.
*   **Tipologia Híbrida:** Uma página contendo texto impresso longo (fácil), tabela sem borda definida (difícil) e caligrafia manual (pesadelo).
*   **Formatos Mentirosos:** PDFs que se dizem pesquisáveis ("searchable PDF"), mas a camada de texto embarcada tem pss!ma qu@!idade (encode quebrado).

## 3. Anatomia de uma Pipeline Completa (O Padrão Ouro)
Tratar a extração como um pipeline ETL (Extract, Transform, Load) garante escalabilidade e economia. Nunca passe todos os seus pdfs tortos num modelo caríssimo como o GPT-4o Vision às cegas.

### Passo 1: Ingestão e Triage (Routing)
A pipeline precisa decidir qual é o tipo de monstro que ela vai processar:
- Arquivo é inteiramente texto digital nativo? (Pule o OCR e use `pypdf`/`fitz` para custo zero).
- É imagem/pdf escaneado? Avalie a densidade e legibilidade.

### Passo 2: Pré-Processamento (A Mágica Antes da Extração)
Melhor que insistir num OCR potente, é limpar a imagem primeiro:
- **Binarização e Limpeza:** Ferramentas baseadas em OpenCV para remover fundo cinza e aumentar o contraste das letras.
- **Deskewing:** Rotacionar programaticamente a imagem para alinhar os eixos de texto ($0^{\circ}$).
- **Crop / Layout Parser:** Usar modelos (YOLO ou frameworks como Unstructured) para separar tabelas de blocos de texto.

### Passo 3: Roteamento de Modelos (Economizando Milhões)
1.  **Texto Base:** Use OCRs mais simples (ex: Tesseract ou AWS Textract) para os blocos brutos de texto onde o resultado costuma ser previsível e o custo é baixo ou zero.
2.  **Tabelas e Alta Definição:** Direcione os "crops" (imagens recortadas) de gráficos e tabelas para VLMs (ex: GPT-4o Vision, Claude 3.5 Sonnet) para convertê-las em formato base estruturado como Markdown.

### Passo 4: Extração Guiada (Structured Output)
Não entregue um string puro. A saída do texto deve ser passada por um processamento (LLM estruturado) para garantir que saia como objeto de dados limpo, usando schemas do Pydantic (ex: `{ "cpf": "000.000.000-00", "status_deferimento": true }`).

### Passo 5: Pós-Processamento e Validação
- **Regras Regex** para validar formatos padrão (CPFs, Códigos CID, números de processo).
- Emprego de **SLMs ou corretores LLM** focado apenas em correção gramatical decorrente de falha de *confidence score* do modelo OCR (ex: OCR trocou `0` por `O`, `1` por `l`, `S` por `5`).

## 4. Estratégia de Armazenamento Inteligente
- Guarde o **Raw Text:** para busca lexical puramente *full-text search*.
- Guarde o **Structured JSON:** para banco relacionais e analytics de negócio (Dashboards).
- Guarde o **Markdown:** para indexação semântica em Vector DB, permitindo um excelente RAG e chunking.

---

## 🛠️ Hands-On: A Missão Prática
Nesta aula, a parte prática irá englobar a construção técnica deste roteador:
1. Usaremos um **PDF propositalmente "sujo"** (simulando um relatório de saúde híbrido).
2. Faremos a triagem pelo `Unstructured.io`.
3. Direcionaremos o texto básico para o `Tesseract` em rodada local.
4. Usaremos a API da OpenAI/Anthropic (`GPT-4o` ou `Claude 3.5 Sonnet`) para extrair os dados tabulares perfeitamente para Markdown.

## ⏭️ Próximo Passo
Depois de extrair perfeitamente o seu primeiro batch de prontuários difíceis, como usar esses dados como agentes de busca eficientes?
Vá para **[Módulo 3: Document Intelligence em Produção](../03-document-intelligence)**.

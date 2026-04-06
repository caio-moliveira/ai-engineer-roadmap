# 🏭 Módulo 3: Document Intelligence

> **Objetivo:** Dar o salto definitivo saindo da extração cega de pixels (OCR convencional) rumo ao entendimento estrutural e contextual de documentos corporativos complexos, ancorados por dois titãs do mercado: a solução em nuvem da Microsoft (Azure) e a esteira open-source especializada da IBM Research (Docling).
> **Status:** A ponte técnica entre os documentos crus e a extração rica para Bancos de Dados ou Agentes RAG.

---

## Objetivos de aprendizado

Ao final desta aula, você será capaz de:

- Explicar a diferença entre OCR clássico e Document Intelligence
- Usar o Azure AI Document Intelligence com modelos prebuilt e entender seus modelos disponíveis
- Usar o Docling para converter documentos complexos em formatos prontos para IA
- Integrar Docling com LangChain e LlamaIndex para pipelines de RAG
- Decidir entre solução local (Docling) e gerenciada (Azure) para cada cenário


## 1. OCR Convencional vs. Document Intelligence

Até a última etapa, nossa busca se baseava em uma pergunta simplista: *"Quais letras estão escritas nesta imagem?"*
A partir de agora, a grande missão muda para: *"O que este documento significa e como suas informações se relacionam geometricamente?"*

- **O Limite do OCR Convencional (ex: Tesseract/EasyOCR):** Ele extrai texto de força bruta num bloco linear contínuo. Se você passar um boleto bancário, o OCR vai cuspir na tela uma dezenas de números avulsos. Ele não faz ideia de que o "R$ 450,00" lido no canto esquerdo pertence ao campo "Valor do Recibo" que estava impresso duas linhas acima. Informações tubulares, colunas duplas e caixas de seleção são ignorados.
- **A Revolução do Document Intelligence:** Aqui nós adicionamos *Semântica e Estrutura Lógica* à visão computacional. Um modelo de *Doc Intelligence* destrói e remonta a arquitetura da página. Ele constrói matrizes perfeitas para Tabelas complexas (mesmo sem bordas), respeita hierarquia entre Títulos (`<h1>`) e blocos de texto nativos, entende o que é rodapé, isola imagens soltas no centro da página e busca pares chave-valor (Key-Values). Ou seja: você deixa de ter um "parágrafo gigante solto" e passa a ter de fato um documento inteligente que a máquina compreende.

### Nossas Ferramentas: Especialistas Modernos
Com o crescimento absurdo de extrações de documentos na vida corporativa, substituiremos bibliotecas pesadas e problemáticas de manter (como o extinto PaddleOCR) por dois focos profissionais onde os *AI Engineers* atuais gastam 90% do seu tempo:
1. **Azure AI Document Intelligence**: A solução *Cloud-Native* e infalível, entregando tudo já mastigado em larga escala mediante pagamento sob uso nas nuvens da Microsoft.
2. **Docling**: O ápice do ecossistema Open-Source atual (mantido debaixo da estrutura da IBM), focadíssimo em transformar seus PDFs confusos em dados formatados puramente para ensinar IA (*Large Language Models*).

---

## 2. Azure AI Document Intelligence (A Solução Analítica)

Originalmente referenciado pela comunidade dev como *Azure Form Recognizer*, a Microsoft unificou recentemente suas dezenas de modelagens de visão e texto em apenas um único produto fortíssimo na nuvem, sendo o padrão ouro moderno para o meio enterprise.

### O Poder da Extração Total
Diferente das bibliotecas locais, aqui você simplesmente remete o PDF inteiro na rota da API e a magia pesada de GPU roda na central da nuvem, de onde recebemos de volta a estrutura meticulosamente dissecada.

- **Modelos pre-treinados (*Prebuilt Models*):** A verdadeira maravilha em termos de ganho de tempo de desenvolvimento. Por estar na vanguarda do mercado corporativo global, a Microsoft deixou modelos em fase final de produção super preparados. Você precisa extrair informações cruciais de um **IRPJ / Documento de Imposto**, ou os valores de um **Receipt (Recibinho do mercado)**, Notas de Serviços Fiscais, RGs ou Passaportes? Basta chamar a rota específica para este fim e a API fará mapeamento nativo retornando o JSON já nomeado (ex: `{ "BusinessName": "Auto Center Zeca", "Subtotal": 120.00 }`).
- **Recorte Base de Layout:** Para extrair faturas que o `prebuilt` não engoliu. Seu layout base reconstrói fielmente checkboxes marcados, tabelas com campos nulos escondidos ou blocos flutuantes, gerando uma marcação precisa da tela até para furos de grampeador nas folhas.
- **Campos customizados na ponta do dedo (*Query Fields*):** O principal atrativo unificando Inteligência Generativa (LLMs) ao layout extractor. Imagine escanear a página da escritura de um imóvel que tem padrões visuais caóticos. Com os Query Fields, passamos propriedades dizendo exatamete: *"Quero saber quem é o Locatário"*, e a IA visual infere na hora dentro do documento qual espaço se refere cognitivamente àquele alvo, fazendo o "clipping" da área exata daquela resposta sem nenhuma linha complexa de Regex.

🔗 **[Acesso a documentação e tutoriais oficiais (Azure AI Doc Intelligence)](https://learn.microsoft.com/azure/ai-services/document-intelligence)**

---

## 3. Docling — A Ingestão Definitiva (Trator para RAGs)

Se o Azure busca te entregar um banco de dados estruturado, a estrela Open source atual do mercado [Docling GitHub Repo](https://github.com/DS4SD/docling) tem apenas um foco: **Comida para IA.**
Este ecossistema foi pensado pela IBM Research durante a febre dos modelos LLM para resolver o maior terror do AI Engineer: Como extrair a página inteira de tal modo que o *"ChatGPT não fique confuso na hora de re-ler ela"*?

### Transformando Monstrinhos em Markdown
Esqueça saídas em JSON cheias de coordenadas cartesianas (X, Y) complicadas. A mágica do Docling é a padronização baseada em marcações semânticas legíveis, com foco total de exportar os arquivos em arquivos **Markdown (`.md`)** perfeitos. E não à toa: Llama-3, Claude e o ecossistema GPT-X foram incansavelmente alimentados compreendendo muito mais o "Markdown Geométrico do Github" do que qualquer outro modelo lexical. 

### Pilares Relevantes do Docling
- **TableFormer:** reconstrução de estrutura de tabelas, incluindo headers aninhados e células mescladas. É notavelmente melhor que qualquer abordagem genérica para tabelas.

-  **Conversor Universal em Pipeline única:** Enquanto você precisaria de `python-docx` para Word, `PyPPTX` para Microsoft apresentações ou `py-pdf` para PDF (cada uma soltando a extração com tags diferentes)... o Docling atua como um canivete-suíço Ingestor Universal. Seja um arquivo puramente escaneado, seja a capa de uma patente com símbolos matemáticos `LaTeX`, HTML antigo ou Relatório Médico no Word: a ingestão lê o miolo geométrico de todos eles e formata-os para um output universal Markdown super amigável aos modelos nativos das instâncias LLM.

🔗 **[Documentação e Início Rápido Oficial para Cientistas (Docling)](https://ds4sd.github.io/docling/)**

---


## Quando usar Azure vs. soluções locais

| Critério | Azure AI Doc. Intelligence | Docling |
|----------|---------------------------|---------------------|
| Infraestrutura necessária | Zero | GPU recomendada |
| Custo fixo | Nenhum | Hardware/cloud |
| Custo por volume alto | Alto (por página) | Baixo (marginal) |
| Privacidade de dados | Dados vão para nuvem MS | 100% local |
| Tabelas complexas | Excelente | Bom (Docling) |
| Setup inicial | 15 minutos | Horas |
| Manutenção de modelos | Zero | Atualizações periódicas |
| Documentos tipificados (NF, recibo, ID) | Excelente (modelos prebuilt) | Requer customização |

## 4. Estrutura dos Laboratórios Práticos

Para você sentir um gostinho sem se emaranhar em centenas de scripts, desenhamos esse módulo perfeitamente fechadinho em `2` arquivos unificados que farão todo o seu coração vibrar.

### Lab 01 — Azure AI Document Intelligence (Mágica Oculta e Rápida)
**Arquivo:** `01_azure.py` *(Sendo implementado...)*
O contato nativo final. Utilizaremos o SDK para chamarmos sem esforço as rotas de *Prebuilt Invoices*, testaremos o esqueleto de Layout puro com tabelas enjoadas em PDFs caóticos, e por último, daremos vida explícita à modelagem pedindo os campos extraídos por inferência de Prompt com o fabuoso `Query Fields`.

### Lab 02 — Docling (A base pura para RAG Frameworks)
**Arquivo:** `02_docling.py` *(Sendo implementado...)*
Na prática! Utilizaremos essa biblioteca fenomenal instalando localmente no seu computador. Daremos a ele um arquivo rico complexo e assistiremos em tempo real ele varrer o documento extraíndo tabelas de fundos irregulares, empacotando e exportando na tela a sua formatação crua universal via `Markdown Document`, onde validaremos que as sessões e títulos não foram misturados uns sobre os outros!

### Extra — Docling via API Server (Docker)
O Docling não precisa rodar apenas embutido num script Python. Você pode subir ele como um microserviço puramente focado em receber documentos via API Rest. 
Para rodar o servidor oficial via Docker localmente e expor sua porta, use o comando:
```bash
docker run -d -p 5001:5001 --name docling-serve ghcr.io/docling-project/docling-serve:latest
```
Com o servidor rodando, você pode testar o envio de PDFs pelo Swagger entrando em `http://localhost:5001/docs`.

---

## Referências

- [Azure AI Document Intelligence — Documentação oficial](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [Azure AI Document Intelligence — Preços](https://azure.microsoft.com/pricing/details/ai-document-intelligence/)
- [Azure AI Document Intelligence Studio](https://documentintelligence.ai.azure.com/studio)
- [azure-ai-documentintelligence — PyPI](https://pypi.org/project/azure-ai-documentintelligence/)
- [Docling — Documentação oficial](https://docling-project.github.io/docling/)
- [Docling - Reference](https://docling-project.github.io/docling/reference/document_converter/)
- [Docling — GitHub](https://github.com/docling-project/docling)
- [LangChain — DoclingLoader](https://python.langchain.com/docs/integrations/document_loaders/docling/)



## ⏭️ Próximo Passo
Dominando essas extrações robustas, os seus dados não estruturados já foram transformados em estruturas úteis. 
Siga para a mágica puramente visual avançada: **[Aula 04 — VLMs (Modelos Visuais de Padrão Aberto) Multimodais](../04-vlm-multimodals)**.

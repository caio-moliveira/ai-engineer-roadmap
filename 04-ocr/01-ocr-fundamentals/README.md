# 📄 Módulo 1: Fundamentos de OCR (A Realidade)

> **Goal:** Transformar pixels em conhecimento.  
> **Status:** A parte mais frustrante da IA.

---

## Objetivos de aprendizado

Ao final desta aula, você será capaz de:

- Explicar o que é OCR e onde ele é aplicado em projetos reais
- Descrever o pipeline clássico de OCR etapa por etapa
- Identificar quando cada ferramenta é a escolha certa
- Reconhecer as limitações do OCR clássico — que motivam todo o restante do módulo

---

## 1. O que é OCR e por que importa

OCR (Optical Character Recognition) é a tarefa de converter imagens que contêm texto em texto legível por máquina. O problema parece simples mas esconde enorme complexidade: o mesmo caractere pode ter centenas de aparências diferentes dependendo da fonte, tamanho, qualidade do papel, iluminação, ângulo da câmera e dezenas de outros fatores.

### Onde OCR é usado hoje

OCR está em todo lugar. Na automação fiscal, ele lê notas fiscais e recibos. No KYC (Know Your Customer) de bancos e fintechs, extrai dados de RG, CNH e passaporte. Em arquivos públicos e cartórios, digitaliza documentos históricos. Na logística, lê etiquetas e manifestos. Na saúde, processa receitas e prontuários. Em acessibilidade, converte documentos em texto para leitores de tela.

A diferença entre um produto de OCR que funciona e um que frustra o usuário quase sempre está nas decisões de engenharia em torno do modelo — não no modelo em si.

### Breve história

| Período | Marco |
|---------|-------|
| 1914 | Emanuel Goldberg cria máquina que lê e converte caracteres em código telegráfico |
| 1950s | IBM desenvolve leitura óptica para cheques bancários |
| 1974 | Ray Kurzweil cria o primeiro OCR omni-fonte |
| 1985–2006 | Tesseract nasce na HP Labs e é adotado pelo Google |
| 2012 | Deep learning começa a superar métodos clássicos |
| 2017–2021 | Transformers chegam ao OCR; TrOCR é publicado pela Microsoft |
| 2024–2026 | VLMs redefinem o estado da arte — OCR vira compreensão de documentos |

---

## 2. O pipeline clássico de OCR

Entender cada etapa do pipeline clássico é fundamental. Os problemas que aparecem nos sistemas modernos frequentemente têm raiz exatamente aqui.

### 2.1 Aquisição e pré-processamento da imagem

Antes de qualquer reconhecimento, a imagem precisa ser preparada. Esta etapa responde: *a imagem está boa o suficiente para ser lida?*

**Conversão para escala de cinza:** a maioria dos algoritmos de OCR trabalha em tons de cinza. Cores adicionam complexidade sem acrescentar informação para o reconhecimento de texto.

**Redimensionamento e DPI:** OCR funciona melhor com imagens em alta resolução. O mínimo recomendado é 300 DPI. Imagens muito pequenas perdem detalhes nos caracteres, tornando-os irreconhecíveis.

**Binarização:** converter a imagem para preto e branco puro. O algoritmo de Otsu encontra o limiar ideal automaticamente para iluminação uniforme. Para iluminação irregular — o caso mais comum em fotos de celular — a binarização adaptativa é mais robusta.

**Sauvola:** variante da binarização adaptativa especialmente eficaz em documentos com fundo não uniforme. Vale conhecer como alternativa para documentos degradados.

### 2.2 Correção de inclinação (deskewing)

Documentos raramente ficam perfeitamente alinhados no scanner. Uma inclinação de apenas 2° já reduz significativamente a precisão do OCR porque a segmentação de linhas assume horizontalidade. A técnica mais comum usa a transformada de Hough ou a análise de componentes conectados para estimar o ângulo de rotação.

### 2.3 Segmentação de layout

O motor de OCR precisa saber **onde** está o texto na imagem antes de tentar lê-lo. A segmentação identifica regiões de texto, imagens, tabelas e espaços em branco.

**Análise de componentes conectados:** identifica grupos de pixels escuros que potencialmente formam letras ou palavras.

**Projeção de histograma:** técnica clássica que analisa a distribuição de pixels pretos por linha e coluna para separar linhas de texto.

**PSM — Page Segmentation Mode:** parâmetro crítico do Tesseract que define como ele interpreta o layout. Escolher o PSM errado é a causa mais comum de resultados ruins com o Tesseract.

### 2.4 Extração de features e classificação

Com cada caractere segmentado, o sistema extrai características para identificá-lo. No OCR clássico isso envolvia descritores geométricos como momentos de Hu e histogramas de gradiente orientado (HOG). O Tesseract 4+ substituiu isso por uma LSTM — rede neural recorrente que considera o contexto da sequência, não apenas cada caractere isoladamente.

### 2.5 Pós-processamento

O texto reconhecido passa por um verificador que usa dicionário e modelo de linguagem para corrigir erros contextuais. "0rdem" pode ser corrigido para "Ordem" quando o contexto indica que é a palavra correta.

---

## 3. Tesseract — o motor OCR open source mais consolidado

O Tesseract é o motor de OCR open source mais usado no mundo, mantido pelo Google desde 2006. Apesar de ter sido lançado nos anos 80, sua versão 5.x usa uma LSTM e tem performance competitiva para casos simples.

### Por que ainda importa em 2026

O Tesseract não compete com os modelos modernos em documentos complexos. Ele importa porque:

- É gratuito, open source e roda em qualquer hardware sem GPU
- É extremamente rápido para texto simples e bem formatado
- É a referência histórica contra a qual todos os outros modelos são comparados
- Entender suas limitações é entender *por que* os modelos modernos existem

### Configurações críticas

**OEM — OCR Engine Mode:** controla qual motor de reconhecimento usar. OEM 3 (LSTM + Legacy combinados) é o padrão recomendado.

**PSM — Page Segmentation Mode:** controla como o Tesseract interpreta o layout da página. Os mais usados são PSM 3 (automático, padrão), PSM 6 (bloco uniforme de texto) e PSM 11 (texto disperso sem ordem específica).

**Idioma:** o Tesseract tem modelos de linguagem separados por idioma. Para português, o pacote `por` deve ser instalado e especificado explicitamente.

### Saída estruturada

O Tesseract pode devolver não apenas o texto, mas também bounding boxes, níveis de confiança por palavra e dados de layout. Isso permite construir visualizações de mapa de confiança — regiões com baixa confiança são exatamente onde os problemas de qualidade de imagem estão concentrados.

### Limitações do Tesseract

- Muito sensível à qualidade da imagem — degradação visual impacta diretamente o CER
- Sem consciência de layout: não sabe que colunas são colunas ou que tabelas são tabelas
- Não entende contexto semântico — não sabe que "R$ 1.234,56" é um valor monetário
- Performance limitada em fontes não latinas, manuscritos e documentos degradados
- Incapaz de processar imagens embutidas no documento ou entender relações entre elementos visuais

---

## 4. EasyOCR — OCR baseado em deep learning, simples de usar

O EasyOCR, desenvolvido pela JaidedAI, é uma biblioteca Python que aplica deep learning ao OCR com uma API deliberadamente simples. Ao contrário do Tesseract, que usa abordagem clássica de pipeline, o EasyOCR usa redes neurais em toda a cadeia.

### Arquitetura

O EasyOCR usa uma arquitetura de duas etapas:

**Detecção:** usa CRAFT (Character Region Awareness For Text detection) para localizar regiões de texto na imagem. O CRAFT funciona detectando probabilidades de caractere e a afinidade entre caracteres adjacentes, o que o torna robusto a texto em múltiplas orientações.

**Reconhecimento:** usa uma rede CRNN (Convolutional Recurrent Neural Network) com atenção para reconhecer o texto nas regiões detectadas. Diferente do Tesseract, considera o contexto visual da sequência inteira.

### Vantagens sobre o Tesseract

- Suporte nativo a 80+ idiomas sem configuração adicional
- Melhor performance em imagens com qualidade moderada sem pré-processamento
- Robusto a texto em múltiplas orientações (texto vertical, rotacionado)
- API mais simples — menos parâmetros para configurar
- Desempenho consideravelmente melhor em cenas naturais (fotos, placas, formulários manuscritos simples)

### Limitações do EasyOCR

- Mais lento que o Tesseract para grandes volumes sem GPU
- Usa mais memória — carrega modelos neurais
- Assim como o Tesseract, não entende layout ou semântica do documento
- Não extrai estrutura — tabelas são devolvidas como texto plano

### Quando usar Tesseract vs. EasyOCR

| Situação | Tesseract | EasyOCR |
|----------|-----------|---------|
| Documentos digitalizados com qualidade alta | ✓ | ✓ |
| Fotos de celular com iluminação irregular | — | ✓ |
| Texto em múltiplas orientações | — | ✓ |
| Idiomas não latinos | Limitado | ✓ |
| Volume alto sem GPU | ✓ | — |
| Integração em ambientes restritos | ✓ | — |
| Simplicidade de configuração | — | ✓ |

A resposta curta: **Tesseract para documentos limpos e alto volume sem GPU; EasyOCR para qualidade variável e múltiplos idiomas**.

---

## 5. Métricas de avaliação

### CER — Character Error Rate

Porcentagem de caracteres incorretos em relação ao total do ground truth. É a métrica mais granular e a mais usada para comparar sistemas de OCR.

```
CER = (substituições + inserções + deleções) / total de caracteres no ground truth
```

Um CER de 5% significa que 1 em cada 20 caracteres está errado. Para leitura de CPF ou valores monetários, esse nível já é inaceitável. Para compreensão geral de texto, é aceitável.

### WER — Word Error Rate

Mesma lógica do CER, mas no nível de palavras. Mais tolerante a pequenos erros de caractere — um erro de digitação em uma palavra conta como um erro de palavra inteira.

### Quando usar cada métrica

Prefira **CER** quando erros em caracteres individuais são críticos: extração de CNPJ, CPF, datas, valores. Prefira **WER** quando o objetivo é compreensão geral do texto. Em benchmarks competitivos, ambos são reportados.

---

## 6. Por que o OCR clássico não resolve tudo

Esta seção é a ponte para o restante do módulo.

| Limitação | Impacto prático |
|-----------|----------------|
| Sem compreensão de layout | Múltiplas colunas viram texto misturado |
| Sem semântica | Não sabe que "Valor Total" é diferente de "Valor Unitário" |
| Sem suporte a imagens no documento | Gráficos, fotos e diagramas são ignorados ou geram ruído |
| Sensível a qualidade de imagem | Foto de celular mal iluminada → CER acima de 30% |
| Sem extração estruturada | Tabelas são devolvidas como texto plano ilegível |
| Sem raciocínio | Não pode inferir campos ausentes ou ambíguos |

O ponto mais importante: **tanto Tesseract quanto EasyOCR são cegos para o conteúdo visual não-textual do documento**. Um contrato com gráficos, uma fatura com o logo da empresa, um relatório com tabelas complexas — essas ferramentas só enxergam o texto.

Os modelos das Aulas 03 e 04 existem para resolver exatamente esses problemas.

---

## 7. Estrutura do laboratório

### OCR básico com Tesseract

O lab percorre a aplicação do Tesseract em diferentes tipos de documentos: um documento limpo digitalizado, uma foto tirada com celular e um formulário com múltiplos campos. Para cada tipo, você vai:

1. Rodar o Tesseract com configuração padrão
2. Medir o CER contra um ground truth anotado
3. Observar onde os erros se concentram
4. Ajustar os parâmetros PSM e OEM e medir o impacto

**Arquivo:** `fund_tesseract.py`

### EasyOCR e comparação

O lab replica os mesmos documentos do Lab 01-A com EasyOCR e constrói uma tabela comparativa de CER, WER e tempo de execução. O objetivo é desenvolver intuição sobre qual ferramenta performa melhor em cada tipo de documento.

**Arquivo:** `fund_easyocr.py`

### Desafio extra

Use o Tesseract e o EasyOCR em uma nota fiscal ou recibo real (foto tirada com celular). Documente quais campos foram reconhecidos corretamente e quais falharam. Guarde esse documento — ele será usado nas Aulas 03 e 04 para comparar com os modelos modernos.

---

## Resumo da aula

- OCR clássico funciona como pipeline: pré-processamento → segmentação → extração de features → classificação → pós-processamento
- Tesseract é o motor mais consolidado — rápido, gratuito, sem GPU — mas sensível à qualidade da imagem e sem consciência de layout
- EasyOCR usa deep learning (CRAFT + CRNN) — mais robusto em condições variadas e múltiplos idiomas, mais lento sem GPU
- CER e WER são as métricas padrão — a escolha entre elas depende do nível de precisão exigido
- Ambas as ferramentas são cegas para o significado e estrutura dos documentos — isso motiva toda a progressão do módulo

---


## ⏭️ Próximo Passo
Quais ferramentas usar?
Próxima aula: **[Aula 02 — Dados, pré-processamento e anotação](../02-ocr-pipelines)**.

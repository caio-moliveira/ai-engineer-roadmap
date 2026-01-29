# 🔍 Módulo 07: RAG (Retrieval‑Augmented Generation)

> **Goal:** O “Hello World” da IA moderna. Conectar o LLM aos seus dados com **engenharia**, não com mágica.
>
> **RAG** é o padrão dominante para IA corporativa porque permite **atualizar conhecimento sem re‑treinar modelos**, com rastreabilidade, controle e custo previsível.

---

## 🧠 0) Mental model correto

**LLMs não têm memória persistente.**
Eles só conseguem “ver” o que está no **context window** naquele momento.

RAG é a técnica de:

1. **Buscar** informação relevante em uma base externa (seus dados)
2. **Injetar** essa informação no prompt
3. **Gerar** uma resposta fundamentada nesse contexto

> **RAG = Retrieval (busca) + Augmentation (contexto) + Generation (resposta)**

O AI Engineer trabalha para maximizar:

* **Recall** (trazer tudo que importa)
* **Precision** (não trazer lixo)
* **Faithfulness / Grounding** (não inventar)
* **Latency e custo** (ser rápido e sustentável)

---

# 1) Por que RAG?

## 1.1 Fine‑tuning vs RAG (decisão de engenheiro)

**Fine‑tuning**:

* caro
* lento para atualizar
* difícil de auditar
* pode “memorizar” padrões indesejados

**RAG**:

* atualiza conhecimento na ingestão
* mantém o modelo genérico
* adiciona rastreabilidade (citações)
* reduz risco de alucinação (se bem feito)

**Regra prática:**

* Se o conhecimento muda com frequência → RAG
* Se o objetivo é estilo/forma muito repetitiva → possivelmente fine‑tuning

---

# 2) O Pipeline de RAG (Etapas Críticas)

RAG em produção é um pipeline com **duas fases**:

1. **Offline (Indexing / Ingestion)** — preparar e indexar conteúdo
2. **Online (Retrieval + Generation)** — atender consultas em tempo real

A maioria dos problemas de RAG não está no LLM.
Está em:

* ingestão ruim
* chunking ruim
* recuperação ruim
* ranking ruim
* contexto mal montado

---

## 2.1 Ingestion (Indexing) — “Transformar dados em conhecimento recuperável”

**Ingestion** é o processo de pegar dados brutos (PDFs, páginas, bancos, e‑mails, Notion, etc.) e convertê‑los em uma base consultável.

### O que a ingestão realmente inclui

1. **Aquisição (connectors)**

   * PDF / DOCX / HTML / Notion / Confluence / SharePoint / SQL
   * Escolha dos conectores e permissões

2. **Extração de texto e estrutura**

   * PDFs podem ser:

     * *digitais* (texto extraível)
     * *escaneados* (precisam de OCR)
   * Preservar estrutura importa: títulos, seções, tabelas, páginas

3. **Limpeza e normalização**

   * remover headers/footers repetidos
   * corrigir hifenização de PDF
   * padronizar whitespace
   * remover lixo (sumários duplicados, páginas vazias)

4. **Enriquecimento (metadata)**

   * Este é um dos maiores diferenciais de RAG bom.
   * Exemplos de metadados úteis:

     * `source` (sistema/arquivo)
     * `doc_id`
     * `title`
     * `section`
     * `page`
     * `created_at`
     * `jurisdiction` / `tema` / `categoria`
     * `access_level` (controle de acesso)

5. **Deduplicação e versionamento**

   * mesma norma em 5 PDFs diferentes
   * versões de documento
   * hash de conteúdo para detectar alterações

6. **Chunking (quebra em unidades recuperáveis)**

7. **Embedding + Upsert** no vector DB

> Em produção, “ingestion” é um pipeline de dados de verdade.

### Erros comuns na ingestão

* Indexar documento inteiro como 1 chunk
* Não guardar metadados (perde filtro e rastreio)
* Não tratar OCR (texto ruim = embedding ruim)
* Não versionar documentos (respostas inconsistentes)

---

## 2.2 Chunking — “A unidade fundamental de recuperação”

**Chunking** é a decisão mais importante do RAG.

> O retriever só consegue recuperar o que você quebrou.

Se o chunk é:

* pequeno demais → perde contexto, aumenta ruído, aumenta custo
* grande demais → mistura assuntos, piora precisão, estoura contexto

### Tamanho (e por que tokens importam)

Chunk size deve ser pensado em **tokens**, não caracteres.

Regra prática inicial (texto):

* **300–800 tokens** por chunk
* **overlap 10–20%** (ou 50–150 tokens)

Mas isso varia por:

* domínio (jurídico tende a precisar mais contexto)
* estilo do texto (tabelas, leis, manuais)
* estratégia de síntese do LLM

---

### Overlap (por que existe)

Overlap evita que uma ideia “corte no meio” e fique incompleta.

Exemplo:

* parágrafo termina no chunk 1
* continuação no chunk 2

Com overlap, chunk 2 começa um pouco antes, preservando continuidade.

---

## 2.3 Embeddings — “O espaço semântico”

**Embedding** é transformar texto (ou imagem) em um vetor numérico.

Esse vetor captura similaridade semântica:

* textos sobre o mesmo assunto ficam próximos
* termos diferentes com mesmo significado ficam próximos

### Conceitos essenciais

* **Dimensão**: tamanho do vetor (ex.: 768, 1024, 1536, 3072)
* **Distância / Similaridade**:

  * cosine similarity (muito comum)
  * dot product
  * L2

### Escolha do embedding model (critério de engenharia)

1. **Domínio**: jurídico ≠ suporte técnico ≠ código
2. **Idioma**: modelos que funcionam bem em PT‑BR
3. **Custo e latência**: embedding é chamado em lote na ingestão
4. **Recall vs precisão**: alguns modelos são melhores para recuperação

### Erros comuns

* Embedding de texto sujo (OCR ruim)
* Misturar estilos (tabelas + texto corrido) sem estratégia
* Re‑embed sem versionamento → incoerência

---

## 2.4 Retrieval — “Encontrar o que importa”

Retrieval é a etapa online que escolhe quais chunks serão enviados ao LLM.

### Tipos de retrieval

1. **Dense retrieval (vector search)**

   * consulta vira vetor
   * retorna chunks mais próximos

2. **Sparse retrieval (keyword / BM25)**

   * baseado em termos exatos
   * ótimo para números, códigos, nomes próprios

3. **Hybrid retrieval**

   * combina dense + sparse
   * é o padrão em muitos cenários corporativos

> A busca perfeita quase sempre é híbrida.

---

### k (top‑k) e o trade‑off

* k pequeno → pode perder contexto (low recall)
* k grande → envia muito lixo (low precision), aumenta custo

Regra inicial:

* `k = 4–10` para muitos casos
* depois ajustar com avaliação

---

### Metadata filtering (por que SQL + metadata salva sistemas)

Filtros estruturados reduzem ruído:

* período
* tipo de documento
* status
* categoria
* município
* órgão

Em produção, retrieval sem filtro vira:

* custo alto
* resposta inconsistente
* baixa precisão

---

## 2.5 Ranking e Re‑ranking — “Não basta recuperar, tem que ordenar”

Vector search retorna candidatos.
Mas ordem inicial pode ser fraca.

**Re‑ranking** melhora a qualidade final:

* Cross‑encoder rerankers
* LLM‑as‑reranker

Fluxo:

1. recuperar top‑k grande (ex.: 30)
2. rerankar e reduzir (ex.: 8)

Isso aumenta precisão sem perder recall.

---

## 2.6 Synthesis / Generation — “Montar contexto e responder”

Aqui o LLM entra.

Mas a chave não é “responder bonito”.

É:

* **responder com base apenas no contexto**
* citar fontes
* declarar desconhecimento

A montagem do contexto importa:

* ordenar chunks por relevância e/ou estrutura
* remover duplicados
* limitar tamanho
* incluir metadados (título, seção, página)

---

# 3) Chunking Strategies (com profundidade)

Chunking é onde a maioria dos RAGs falha.

A seguir, estratégias relevantes e quando usar.

---

## 3.1 Fixed Size (baseline)

**Como funciona:** corta a cada N caracteres/tokens.

✅ prós:

* simples
* rápido

❌ contras:

* quebra ideias no meio
* mistura seções
* ruim para documentos estruturados

Use apenas como baseline.

---

## 3.2 Recursive / Text Splitters (prático e sólido)

**Como funciona:** tenta dividir respeitando separadores:

* \n\n
* \n
* frases
* palavras

É o padrão de muitos frameworks.

✅ bom para:

* textos corridos
* docs semi‑estruturados

❌ ainda falha em:

* tabelas
* PDFs com estrutura quebrada

---

## 3.3 Markdown / Header‑based chunking (muito bom para docs estruturados)

**Como funciona:** quebra por:

* títulos
* headers
* seções

✅ excelente para:

* documentação técnica
* wikis
* Notion/Confluence

Porque preserva o “mapa mental” do texto.

---

## 3.4 Semantic chunking (state of the art, mas exige cuidado)

**Como funciona:** detecta mudança de assunto usando embeddings ou heurísticas semânticas.

✅ prós:

* chunks mais coerentes
* melhor grounding

❌ contras:

* mais caro
* mais lento
* depende de texto bem extraído

Ótimo para:

* documentos longos
* textos com tópicos bem definidos

---

## 3.5 Sliding window + overlap (padrão robusto)

Combina:

* chunk size em tokens
* overlap calculado

É um dos melhores pontos de equilíbrio para iniciar.

---

## 3.6 Domain‑aware chunking (nível expert)

Em domínios como jurídico, você pode chunkar por:

* artigo
* inciso
* parágrafo
* ementa

Isso aumenta rastreabilidade e precisão.

Exige:

* parsing
* estrutura confiável

Mas o ganho é enorme.

---

# 4) Grounding — Como reduzir alucinação

RAG só funciona bem com **grounding**.

### Técnicas essenciais

1. **Instrução explícita**

   * “Se não estiver no contexto, diga que não sabe.”

2. **Citações e rastreabilidade**

   * cada afirmação deve apontar para um chunk

3. **Context delimiters**

   * separar claramente o que é contexto vs conversa

4. **Answerability checks**

   * classificar se a pergunta é respondível

5. **Self‑consistency / verification**

   * validar resposta contra o contexto

> Empresas não têm medo de IA.
> Elas têm medo de respostas inventadas.

---

# 5) Failure modes (onde RAG quebra)

* **Bad ingestion** → texto incompleto, OCR ruim
* **Bad chunking** → contexto quebrado
* **Bad embeddings** → espaço semântico fraco
* **Bad retrieval** → top‑k errado
* **No reranking** → ruído alto
* **No filtering** → custo explode
* **No grounding** → alucinação

---

# 6) Checklist mínimo de um RAG de produção

* [ ] Pipeline de ingestão versionado
* [ ] Metadados ricos e filtráveis
* [ ] Chunk size em tokens + overlap
* [ ] Hybrid search quando necessário
* [ ] Reranking (ao menos em casos críticos)
* [ ] Prompt com grounding e citações
* [ ] Métricas e avaliação (módulo 09)

---

## ⏭️ Próximo passo

RAG sem avaliação é fé.

Vá para **[Módulo 09: Observabilidade & Avaliação de IA](../09-observability)**.

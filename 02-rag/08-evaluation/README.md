# 08 - Evaluation de RAG com RAGAS

## O que é Avaliação de RAG?

Avaliar um sistema RAG (Retrieval-Augmented Generation) é crucial para garantir que ele não apenas recupere os documentos certos, mas também gere respostas precisas e úteis baseadas neles.

Diferente de tarefas tradicionais de NLP, no RAG precisamos avaliar dois componentes principais independentente e em conjunto:

1.  **Componente de Recuperação (Retriever):** "Eu encontrei os documentos certos?"
2.  **Componente de Geração (Generator/LLM):** "Eu respondi a pergunta corretamente usando os documentos encontrados?"

Para isso, utilizamos frameworks como o **RAGAS** (RAG Assessment), que oferece métricas padronizadas para quantificar a qualidade do seu pipeline.

## Principais Métricas do RAGAS

O [RAGAS](https://docs.ragas.io/en/stable/tutorials/rag/) propõe métricas que cobrem diferentes aspectos do RAG. As quatro principais são:

### 1. Faithfulness (Fidelidade)
*   **O que mede:** Se a resposta gerada pode ser inferida **apenas** a partir do contexto recuperado.
*   **Por que importa:** Evita alucinações. Garante que o modelo não está inventando informações que não estão nos documentos.
*   **Pergunta chave:** "A resposta 'respeita' o contexto fornecido?"

### 2. Answer Relevance (Relevância da Resposta)
*   **O que mede:** O quão relevante a resposta gerada é para a **pergunta original** (prompt).
*   **Por que importa:** Garante que o modelo não está tangenciando ou ignorando a pergunta do usuário.
*   **Pergunta chave:** "A resposta ataca diretamente a dúvida do usuário?"

### 3. Context Precision (Precisão do Contexto)
*   **O que mede:** A proporção de chunks **relevantes** dentre os chunks recuperados.
*   **Por que importa:** (Avaliação do Retriever) Mede se estamos trazendo muito lixo junto com a informação útil.
*   **Pergunta chave:** "Quanto do que eu recuperei é realmente útil?"

### 4. Context Recall (Revocação do Contexto)
*   **O que mede:** Se o contexto recuperado contém **toda** a informação necessária para responder a uma "Ground Truth" (resposta ideal esperada).
*   **Por que importa:** (Avaliação do Retriever) Mede se deixamos passar alguma informação importante.
*   **Nota:** Exige um dataset com `ground_truth` (respostas corretas esperadas).

---

## 🔍 Observabilidade com Langfuse

Para garantir o bom funcionamento do nosso sistema RAG em ambiente produtivo, dependemos fortemente de práticas de **observabilidade**. A observabilidade nos permite medir, rastrear e depurar o comportamento de agentes e LLMs de forma escalável. Neste módulo, utilizamos o **[Langfuse](https://langfuse.com/docs)**, uma plataforma de engenharia de LLM open-source.

O Langfuse nos oferece uma visão completa sobre todas as etapas do nosso pipeline, desde a ingestão de metadados dos documentos no banco vetorial até as chamadas de ferramentas (*tool calling*) feitas pelo modelo.

Abaixo explicamos como ele foi integrado em nosso projeto:

### 1. Ingestão e Indexação (`utils.py`)
No estágio de preparação do banco vetorial, utilizamos o cliente nativo do Langfuse para rastrear detalhadamente o passo a passo através de identificadores chamados de `spans`:

*   **Traces Hierárquicos:** Iniciamos uma observação raiz (`start_as_current_observation`) para englobar toda a execução da função `load_and_index_pdf`.
*   **Detalhamento de Etapas (Spans):** Criamos *spans* filhos para monitorar os tempos de execução e o status das sub-tarefas: `check_collection`, `load_pdf`, `chunking`, `qdrant_prepare` e `qdrant_upsert`.
*   **Enriquecimento de Dados:** Usamos `propagate_attributes` para injetar tags e metadados relevantes à ingestão (como tamanho dos *chunks* configurado, `PDF_PATH` e parâmetros do Qdrant) nas observações geradas, facilitando a busca no painel do Langfuse. Também registramos os *outputs* durante a execução de cada *span* usando `update_current_span()`.

### 2. Geração e Agente (`01_rag_agent_eval.py`)
Na etapa de execução da lógica do RAG (Agentic RAG), aproveitamos a [integração nativa do Langfuse com o LangChain](https://langfuse.com/docs/integrations/langchain) para simplificar a coleta de informações (*traces*):

*   **Callback Handler:** Instanciamos o `CallbackHandler` específico através do módulo `langfuse.langchain`.
*   **Rastreamento Automático:** Passando este *handler* no parâmetro de configuração (`config={"callbacks": [langfuse_handler]}`) durante a invocação do nosso agente (`agent_executor.stream`), o Langfuse automaticamente captura e desenha uma árvore completa da execução.
*   **Visibilidade de Ferramentas:** Sempre que a ferramenta customizada `retrieve_context` ou o fallback para busca online (`DuckDuckGoSearchRun`) é acionado pelo provedor do LLM, os fluxos de entrada (*query*) e saída (quais documentos foram recuperados do vector store), assim como métricas de precisão e latência, são gravados automaticamente e enviados para o servidor de observabilidade.

Para configurar o Langfuse no seu projeto, lembre-se de configurar as suas credenciais de autenticação (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, e `LANGFUSE_HOST`) criadas na plataforma e incluí-las no seu arquivo `.env` na raiz do projeto.

---

## Como Executar

### Pré-requisitos

Certifique-se de ter as dependências instaladas:

```bash
uv add ragas datasets langchain-openai langchain-qdrant qdrant-client
```

### Script de Avaliação

O script `01_ragas_evaluation.py` demonstra como criar um dataset simples de perguntas e respostas geradas pelo nosso RAG e avaliá-las usando as métricas acima.

**Nota:** O script reutiliza a função `load_and_index_pdf` do módulo `06-rag-agent` para subir o banco vetorial.

```bash
python 01_ragas_evaluation.py
```

Isso irá:
1.  Carregar o PDF e indexar no Qdrant (se necessário).
2.  Executar um mini-pipeline de RAG para 3 perguntas de exemplo sobre o documento.
3.  Coletar: `question`, `answer`, `contexts`.
4.  Executar a avaliação do RAGAS e exibir os scores.

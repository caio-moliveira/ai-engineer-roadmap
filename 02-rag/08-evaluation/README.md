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

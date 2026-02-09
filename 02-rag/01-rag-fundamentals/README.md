# 🏗️ Módulo 1: Fundamentos de RAG & Modelos Mentais

> **Goal:** Entender por que não apenas "Fine-Tunamos" tudo.  
> **Status:** Arquitetura 101.

## 1. O que é RAG? (Realmente)
RAG é uma **Prova com Consulta** para IA.
- **Fine-Tuning:** Estudar para a prova e tentar decorar o livro (Livro Fechado).
- **RAG:** Levar o livro para a prova e consultar a resposta (Livro Aberto).

### Por que LLMs sozinhos falham
LLMs são **Motores de Raciocínio**, não Bancos de Dados de Conhecimento.
- Eles têm um "Knowledge Cutoff" (data de corte).
- Eles alucinam fatos obscuros.
- Eles não têm acesso aos dados privados da sua empresa (SQL/Notion/Slack).

## 2. RAG vs Fine-Tuning
Este é o tópico #1 de confusão.

| Feature | RAG | Fine-Tuning |
|:---|:---|:---|
| **Objetivo** | Adicionar conhecimento novo. | Mudar comportamento/estilo. |
| **Acurácia** | Alta (fundamentada em docs). | Variável (risco de alucinação). |
| **Velocidade de Update** | Instantânea (add doc no DB). | Lenta (re-treinar modelo). |
| **Rastreabilidade** | Perfeita (cita fontes). | Zero (caixa preta). |
| **Custo** | Baixo (Vector DB). | Alto (GPU compute). |

> **Regra:** Sempre tente RAG primeiro. Fine-tune apenas se precisar que o modelo fale uma linguagem muito específica (ex: Alemão Médico) ou gere um formato complexo (SQL) consistentemente.

## 3. A Evolução do RAG
Estamos atualmente na Geração 3.

### Gen 1: Naive RAG (2023)
- Processo: PDF -> Dividir a cada 500 chars -> Embed -> Retornar top 4 -> Jogar no Prompt.
- Resultado: "Não sei" ou respostas erradas porque o contexto foi perdido.

### Gen 2: Advanced RAG (2024)
- **Hybrid Search:** Keywords + Vetores.
- **Reranking:** Usar um Cross-Encoder para filtrar resultados ruins.
- **Re-writing:** Transformar "Quanto custa?" em "Quanto custa o iPhone 15 Pro?".

### Gen 3: Agentic RAG (2025)
- **Tool Use:** O LLM decide *se* precisa pesquisar.
- **Multi-Step:** Pesquisa -> Lê -> Pesquisa de novo.
- **Raciocínio:** "Achei X, mas contradiz Y. Preciso checar Z."

## 4. Arquitetura Moderna (O Stack Padrão)
1.  **Ingestion Service:** Dados não estruturados -> Limpeza -> Armazenamento.
2.  **Vector Store (Qdrant):** Memória de longo prazo.
3.  **Retriever:** A lógica que encontra dados (Bm25 + Dense).
4.  **Generator:** O LLM que sintetiza a resposta.

## 🧠 Mental Model: "O Bibliotecário"
Imagine um Bibliotecário (O Retriever) e um Professor (O LLM).
- Você faz uma pergunta ao Professor.
- O Professor pede ao Bibliotecário para achar os livros.
- O Bibliotecário traz 5 páginas.
- O Professor lê e te responde.

**Se o Bibliotecário trouxer as páginas erradas, o Professor não consegue responder.**
**Falha no RAG é quase sempre falha de Retrieval.**

## ⏭️ Próximo Passo
Vamos ver como organizar os livros.
Vá para **[Módulo 2: Ingestão de Dados e Pipelines](../02-ingestion-pipeline)**.

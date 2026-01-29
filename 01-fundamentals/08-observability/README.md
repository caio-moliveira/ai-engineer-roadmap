# 🔭 Módulo 08: Observabilidade & Avaliação de IA

> **Goal:** "Você não pode melhorar o que não pode medir."
>
> Este módulo define o que separa **demos de IA** de **sistemas de IA confiáveis em produção**.

Observabilidade não é opcional em IA.
Ela é **infraestrutura crítica**.

---

## 🧠 Mental model correto

Em software tradicional:

* erro → exception
* stack trace → causa raiz

Em sistemas com LLMs:

* a resposta pode estar **errada, incoerente ou inventada**
* e ainda assim retornar **HTTP 200 OK**

Isso cria um novo tipo de falha:

> ❗ **Silent Failure** — o sistema funciona tecnicamente, mas falha semanticamente.

Sem observabilidade, você nunca saberá:

* por que a resposta ficou ruim
* quando o sistema começou a degradar
* qual mudança piorou o comportamento

AI Engineers não depuram apenas código.
Eles depuram **comportamento probabilístico**.

---

# 1️⃣ O que significa observabilidade em IA

Observabilidade em IA responde a perguntas como:

* Qual prompt foi usado?
* Qual versão do prompt?
* Qual modelo?
* Quantos tokens?
* Qual custo?
* Qual contexto foi recuperado?
* Quais documentos influenciaram a resposta?
* Onde a latência aconteceu?

Logs tradicionais não conseguem responder isso.

Precisamos de **observabilidade semântica**.

---

# 2️⃣ Os três pilares da observabilidade em IA

Todo sistema de IA bem observado mede:

1. **Tracing** — o caminho da execução
2. **Metrics** — custo, latência, volume
3. **Evaluation** — qualidade semântica

Esses três pilares se complementam.

---

# 3️⃣ Tracing — o raio-X do sistema

Tracing permite visualizar toda a execução de uma requisição:

```
User Query
   ↓
Prompt Construction
   ↓
Retrieval
   ↓
Reranking
   ↓
LLM Call
   ↓
Post-processing
```

Cada etapa gera:

* tempo
* inputs
* outputs
* tokens
* erros

Isso é essencial para depurar chains, graphs e agentes.

---

## 3.1 Por que logs tradicionais não funcionam

Logs são lineares.

IA é:

* paralela
* condicional
* não determinística

Um agente pode:

* chamar ferramentas
* decidir caminhos
* repetir etapas

Sem tracing estruturado, você fica cego.

---

# 4️⃣ Ferramentas foco do módulo

Neste roadmap, focamos em **três ferramentas fundamentais**, amplamente utilizadas em produção:

* **MLflow** — tracking, versionamento e avaliação
* **LangSmith** — tracing e avaliação nativa para LangChain/LangGraph
* **Langfuse** — observabilidade completa independente de framework

Cada uma cobre uma camada diferente do problema.

---

# 5️⃣ MLflow — o backbone de experimentação e versionamento

## O que é MLflow

MLflow nasceu no mundo de ML tradicional, mas evoluiu para suportar **GenAI workflows**.

Ele atua como:

* sistema de tracking
* repositório de experimentos
* versionador de artefatos

Em IA moderna, MLflow é usado para:

* versionar prompts
* versionar datasets
* versionar embeddings
* registrar métricas de avaliação

---

## O que MLflow resolve bem

* Comparar versões de prompts
* Comparar estratégias de RAG
* Armazenar datasets de avaliação
* Registrar métricas automaticamente

MLflow traz **disciplina científica** para sistemas probabilísticos.

---

## Limitações do MLflow

* Não é ótimo para tracing de chains complexas
* Não é focado em runtime observability

Por isso, ele costuma ser combinado com LangSmith ou Langfuse.

---

# 6️⃣ LangSmith — observabilidade nativa para LangChain

## O que é LangSmith

LangSmith é a ferramenta oficial de observabilidade do ecossistema LangChain.

Ele oferece:

* tracing automático
* visualização de chains e graphs
* inspeção de prompts
* logs de retrieval
* análise de tokens

É extremamente poderoso quando você usa:

* LangChain
* LangGraph

---

## O que o LangSmith permite ver

Para cada request:

* prompt final enviado ao modelo
* documentos recuperados
* ordem dos passos
* latência por nó
* custo aproximado

Isso transforma debugging de IA em algo possível.

---

## Avaliações no LangSmith

LangSmith permite:

* datasets de avaliação
* execuções automáticas
* LLM-as-a-Judge

Você pode comparar:

* versão A vs versão B
* prompt antigo vs novo
* estratégia de retrieval

Tudo com histórico.

---

## Limitações do LangSmith

* Fortemente acoplado ao LangChain
* Menos flexível fora desse ecossistema

---

# 7️⃣ Langfuse — observabilidade independente de framework

## O que é Langfuse

Langfuse é uma plataforma de **observabilidade e avaliação vendor-agnostic**.

Ela funciona com:

* LangChain
* LangGraph
* LlamaIndex
* APIs próprias
* chamadas diretas a LLMs

Isso a torna ideal para ambientes corporativos.

---

## Principais capacidades

* tracing distribuído
* versionamento de prompts
* métricas de custo
* feedback humano
* avaliação automática
* dashboards operacionais

Langfuse trata IA como um sistema vivo.

---

## Conceito importante: Prompt como artefato

Em Langfuse:

* prompts são versionados
* mudanças são rastreadas
* impactos são medidos

Isso é essencial para governança.

---

# 8️⃣ Avaliação de IA — o coração da melhoria contínua

Sem avaliação, você não evolui.

Mas IA não permite asserts tradicionais.

---

## 8.1 Golden Dataset

Um **Golden Dataset** contém:

* pergunta
* contexto esperado
* resposta esperada (ou diretrizes)

Ele representa casos reais do negócio.

Esse dataset deve ser:

* pequeno
* curado
* representativo

---

## 8.2 LLM-as-a-Judge

Em vez de comparar texto exato, usamos um modelo forte para avaliar:

* correção
* completude
* fidelidade
* utilidade

O avaliador não é o mesmo modelo do sistema.

Isso reduz viés.

---

## 8.3 Métricas comuns

* Answer relevance
* Faithfulness
* Groundedness
* Context utilization
* Helpfulness

Essas métricas permitem comparação estatística entre versões.

---

# 9️⃣ Métricas específicas de RAG

RAG adiciona uma camada crítica: retrieval.

Principais métricas:

* **Context Precision** — quanto do contexto é realmente útil
* **Context Recall** — o que deveria ter sido recuperado
* **Answer Faithfulness** — se a resposta usa apenas o contexto
* **Answer Relevance** — se responde a pergunta

Sem medir retrieval, você nunca sabe se o problema está no LLM ou na busca.

---

# 🔟 Observabilidade como sistema nervoso

Observabilidade não é dashboard bonito.

Ela é o **sistema nervoso central** do sistema de IA.

Ela permite:

* detectar degradação
* medir impacto de mudanças
* controlar custos
* justificar decisões técnicas

Sem isso, IA vira superstição.

---

# ✅ Checklist mínimo de produção

* [ ] tracing ativo
* [ ] prompts versionados
* [ ] tokens monitorados
* [ ] custo por request conhecido
* [ ] datasets de avaliação
* [ ] LLM-as-a-judge
* [ ] comparação entre versões

---

## ⏭️ Próximo passo

Seu sistema funciona.
Agora ele precisa rodar para milhões de usuários.

Vá para **[Módulo 10: Deploy, Infra e Produção](../10-deploy-production)**.

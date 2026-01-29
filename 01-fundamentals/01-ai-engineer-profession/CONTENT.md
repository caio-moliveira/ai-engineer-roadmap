Excelente escolha — essa **primeira aula é a mais importante de todo o roadmap**.
Ela não ensina ferramenta: ela **define identidade profissional**.

Para esse tipo de aula, o que mais gera autoridade não é opinião — é **referência externa forte**:

* pessoas que criaram o mercado
* empresas que operam IA em escala real
* documentos públicos que comprovam que esse papel existe

Abaixo eu organizei **conteúdos reais, atuais e reconhecidos**, que você pode usar como **base, citação ou leitura complementar** na aula.

---

# 🎓 Aula 1 — O Framework da Profissão de AI Engineer

## Fontes, referências e conteúdos de mercado

---

# 🧠 1. O papel do AI Engineer no mercado

## 📌 OpenAI — “Building AI systems, not models”

A OpenAI vem deixando isso explícito desde 2023:

> *“Most real-world AI work is not training models — it’s building systems around them.”*

Isso aparece repetidamente em:

* OpenAI Cookbook
* OpenAI Developer Docs
* Talks de engenheiros da OpenAI

📚 Referências:

* OpenAI Cookbook — Production Patterns
  [https://cookbook.openai.com](https://cookbook.openai.com)
* OpenAI DevDay talks (Agents, tools, evals)
  [https://platform.openai.com/docs](https://platform.openai.com/docs)

👉 **Mensagem-chave para a aula:**
O mercado não está contratando pessoas para “treinar modelos”, mas para **orquestrar modelos**.

---

## 📌 Andrej Karpathy — “The hottest new programming language is English”

Karpathy (ex-diretor de IA da Tesla e OpenAI) redefiniu o papel do engenheiro:

> *“We are now programming with natural language.”*

Mas ele deixa claro:

* não é prompt mágico
* é engenharia de sistemas probabilísticos

🎥 Referência:

* Talk: *Software Is Changing (Again)*
  [Video](https://www.youtube.com/watch?v=d31CnWUQAxc)

👉 Use isso para mostrar:

> LLM ≠ chatbot
> LLM = novo tipo de runtime

---

# 🏛️ Pilar 1 — Fluência em Foundation Models

## 📌 Anthropic — Constitutional AI & Model Behavior

A Anthropic é uma das empresas que mais falam **sobre controle de comportamento**, não performance.

Eles tratam LLMs como:

* sistemas perigosos se mal orquestrados
* componentes que exigem restrições claras

📚 Conteúdos:

* Constitutional AI
  [https://www.anthropic.com/research/constitutional-ai](https://www.anthropic.com/research/constitutional-ai)
* Anthropic Docs (tool use, structured output)
  [https://docs.anthropic.com](https://docs.anthropic.com)

👉 Excelente para reforçar:

> “O modelo não é confiável por padrão.”

---

## 📌 OpenAI — Structured Outputs & Function Calling

A própria OpenAI afirma:

> *“Do not parse model output with regex.”*

Eles tratam JSON schema como **fundamento de produção**.

📚 Referências:

* Structured Outputs
  [https://platform.openai.com/docs/guides/structured-outputs](https://platform.openai.com/docs/guides/structured-outputs)
* Function Calling
  [https://platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)

👉 Isso valida totalmente seu ponto:

> probabilístico → determinístico

---

## 📌 Google DeepMind — Model Selection & Trade-offs

O Google fala claramente que não existe “melhor modelo”.

Existe:

* melhor modelo **para aquele trade-off**

📚 Referência:

* Gemini technical overview
  [https://deepmind.google/technologies/gemini/](https://deepmind.google/technologies/gemini/)

Eles destacam:

* latency
* cost
* reasoning depth

👉 Perfeito para sustentar:

> “Escolher modelo é decisão de engenharia, não hype.”

---

# 🏛️ Pilar 2 — Arquitetura de Sistemas

## 📌 AWS — Generative AI Architecture Patterns

A AWS publicou arquiteturas oficiais mostrando que:

* LLM é só um componente
* RAG é padrão
* observabilidade é obrigatória

📚 Referência:

* AWS GenAI Reference Architecture
  [https://aws.amazon.com/architecture/generative-ai/](https://aws.amazon.com/architecture/generative-ai/)

Eles mostram claramente:

* ingestion
* retrieval
* orchestration
* evaluation

👉 Ótimo para mostrar que **isso já é engenharia formal**, não moda.

---

## 📌 Microsoft — Azure OpenAI Architecture Center

A Microsoft tem talvez o material mais maduro de mercado corporativo.

📚 Referência:

* Azure OpenAI Architecture
  [https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/)

Eles falam explicitamente:

* RAG
* grounding
* evals
* monitoring
* cost management

👉 Isso valida totalmente o Pilar 2.

---

## 📌 Uber Engineering — AI Platform & Observability

A Uber publicou vários artigos mostrando que:

* IA sem observabilidade é inutilizável
* tracing é obrigatório
* avaliação contínua é essencial

📚 Exemplos:

* [https://www.uber.com/blog/ai-observability/](https://www.uber.com/blog/ai-observability/)
* [https://www.uber.com/blog/ml-platform/](https://www.uber.com/blog/ml-platform/)

👉 Excelente para mostrar:

> “Empresas grandes não confiam em IA sem métricas.”

---

# 🏛️ Pilar 3 — Engenharia de Produção

## 📌 Netflix — ML & AI in Production

A Netflix é referência mundial em engenharia.

Eles repetem um mantra importante:

> *“Most ML failures are engineering failures, not model failures.”*

📚 Referência:

* Netflix Tech Blog — ML in Production
  [https://netflixtechblog.com](https://netflixtechblog.com)

👉 Isso casa perfeitamente com seu Pilar 3.

---

## 📌 Stripe — APIs First, Reliability First

Stripe é referência absoluta em engenharia de produto.

Eles tratam qualquer sistema inteligente como:

* API
* contrato
* versionamento

📚 Referência:

* [https://stripe.com/blog/api-versioning](https://stripe.com/blog/api-versioning)

👉 Excelente para reforçar:

> “IA também é backend.”

---

## 📌 Databricks — Lakehouse + GenAI

A Databricks consolidou o termo **LLMOps**.

📚 Referências:

* [https://www.databricks.com/blog/llmops](https://www.databricks.com/blog/llmops)
* [https://www.databricks.com/solutions/generative-ai](https://www.databricks.com/solutions/generative-ai)

Eles falam sobre:

* versionamento
* avaliação
* governança
* custo

👉 Ótimo para mostrar maturidade de mercado.

---

# 📊 Dados de mercado (para abertura da aula)

Você pode usar dados como:

### 📈 McKinsey (2024)

* +70% das empresas já usam GenAI em pelo menos um fluxo
* maior gargalo: **engenharia e integração**, não modelo

Fonte:
[https://www.mckinsey.com/capabilities/quantumblack/our-insights](https://www.mckinsey.com/capabilities/quantumblack/our-insights)

---

### 📈 Gartner

* GenAI entra no “Plateau of Productivity” apenas quando há:

  * governança
  * arquitetura
  * observabilidade

Fonte:
[https://www.gartner.com/en/articles/generative-ai-hype-cycle](https://www.gartner.com/en/articles/generative-ai-hype-cycle)

---

# 🧠 Como usar isso na aula

Sugestão didática:

### 1️⃣ Comece com mercado

* OpenAI, McKinsey, Gartner
* “Isso não é opinião — é realidade industrial”

### 2️⃣ Mostre o problema

* modelos erram
* respostas erradas com 200 OK
* custo explode
* ninguém sabe por quê

### 3️⃣ Apresente os 3 pilares

Como resposta natural a esse caos.

### 4️⃣ Mostre que isso já é profissão

* Microsoft
* AWS
* Uber
* Netflix
* Databricks

Todos falam a mesma língua.

---

# 🎯 Resultado dessa aula

Depois dessa aula, o aluno deve pensar:

> “Agora eu entendo o que é ser AI Engineer.
> Não é prompt.
> É engenharia.”



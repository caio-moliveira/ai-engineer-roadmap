# 🤖 Módulo 02: Fundamentos de LLMs & GenAI

> **Objetivo:** Compreender a "física" dos Large Language Models. Não apenas como usar, mas como funcionam, seus limites e como orquestrá-los em engenharia de software robusta.
> 
> **Leitura Obrigatória para:** Quem quer parar de "chutar prompts" e começar a construir sistemas determinísticos.

---

## 📚 1. O que é um LLM? (Além do Hype)

Um **Large Language Model (LLM)** é, em sua essência, um **modelador estatístico de distribuição de tokens** treinado em uma quantidade massiva de texto. A arquitetura predominante hoje é o **Transformer** (apresentado pelo Google em 2017).

### O Conceito de "Autoregressive"
O modelo não "pensa". Ele calcula a probabilidade do próximo *token* dado o histórico anterior.
$$ P(w_t | w_{t-1}, w_{t-2}, ..., w_1) $$

Isso significa que o modelo é **determinístico** na sua distribuição de probabilidades, mas **estocástico** na sua geração (dependendo da temperatura).

> **Referência Clássica:** [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762) - O paper que criou a arquitetura Transformer.

---

## 🔠 2. Tokenização: A Unidade Atômica

LLMs não leem "palavras". Eles leem **Tokens**.
A maioria dos modelos modernos usa **BPE (Byte Pair Encoding)**.

*   **Inglês:** 1 palavra $\approx$ 1.3 tokens.
*   **Português/Outros:** Pode ser menos eficiente (mais tokens por palavra).
*   **Números:** `9.11` pode ser quebrado em `9`, `.`, `11` ou `9`, `.`, `1`, `1`. Isso explica por que LLMs erram matemática simples sem ferramentas.

### Por que importa?
1.  **Custo:** Você paga por token (Input/Output).
2.  **Context Window:** O limite de "memória" do modelo é em tokens.
3.  **Performance:** "A strawberry tem quantos Rs?" O modelo vê tokens, não letras. Se "strawberry" for um token único `[STRAWBERRY]`, ele não "vê" os Rs internos sem quebrar a palavra.

> **Tool:** [OpenAI Tokenizer](https://platform.openai.com/tokenizer) - Visualize como seu texto vira números.

---

## 🧠 3. Context Window & "Attention"

A **Context Window** é a memória de curto prazo. Tudo que não está na janela de contexto **não existe** para o modelo naquele momento.

Sim, modelos como Gemini 1.5 Pro suportam 1M+ tokens. Mas cuidado com o fenômeno **"Lost in the Middle"**: a performance de recuperação (recall) tende a ser melhor no início e no fim do prompt, e pior no meio.

> **Referência:** [Lost in the Middle: How Language Models Use Long Contexts (Liu et al., 2023)](https://arxiv.org/abs/2307.03172)

---

## 🎛️ 4. Hiperparâmetros de Geração

Você controla a "criatividade" do modelo ajustando como ele escolhe o próximo token dessa distribuição probabilística.

### Temperature (0.0 a 2.0)
*   **Baixa (0.0 - 0.3):** Escolhe sempre os tokens mais prováveis. Mais determinístico, focado, bom para código e JSON.
*   **Alta (0.7 - 1.5):** Nivela as probabilidades, permitindo que tokens menos óbvios sejam escolhidos. Mais criativo, mas propenso a alucinações.

### Top-P (Nucleus Sampling)
Cortamos a cauda da distribuição.
*   **Top-P = 0.9:** O modelo considera apenas os top tokens que somam 90% da probabilidade cumulativa. Elimina opções absurdas.

> **Regra de Ouro:** Altere *Temperature* OU *Top-P*, geralmente não os dois simultaneamente.

---

## 🗣️ 5. Prompt Engineering (A Ciência, não a Arte)

Engenharia de Prompt não é sobre "pedir com educação". É sobre **condicionar a distribuição probabilística** para o resultado desejado.

### 5.1 Zero-Shot vs Few-Shot
*   **Zero-Shot:** Pedir sem exemplos. "Classifique este texto."
*   **Few-Shot:** Dar exemplos input/output. É a técnica mais poderosa para melhorar performance sem treinar o modelo.
    > "Language Models are Few-Shot Learners" (GPT-3 Paper).

### 5.2 Chain-of-Thought (CoT)
Pedir para o modelo "pensar passo a passo". Isso força o modelo a gerar tokens de raciocínio *antes* da resposta final, aumentando a precisão em tarefas lógicas/matemáticas.
> **Referência:** [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (Wei et al., 2022)](https://arxiv.org/abs/2201.11903)
> **Referência:** [Prompt Engineering Guide](https://www.promptingguide.ai/)

### 5.3 System Prompts
A "constituição" do seu agente. Define persona, limites e formato de resposta. Sempre separe instruções do sistema (persistentes) da entrada do usuário (variável).

---

## 🤖 6. Tool Calling & Agentes

LLMs são cérebros "presos em uma caixa". Eles não têm relógio, não acessam a internet e não rodam código.
**Tool Calling (Function Calling)** resolve isso.

1.  Você descreve uma função (ex: `get_weather(city)`) em JSON Schema.
2.  O LLM, se precisar, retorna um JSON pedindo para executar essa função.
3.  Seu backend executa a função e devolve o resultado para o LLM.
4.  O LLM formula a resposta final.

Isso é a base dos **Agentes**: LLMs que podem *agir* no mundo.
> **Referência:** [ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2023)](https://arxiv.org/abs/2210.03629)

---

## 🛠️ 7. RAG vs Fine-Tuning

A dúvida clássica.

| Feature | **RAG (Retrieval-Augmented Generation)** | **Fine-Tuning** |
| :--- | :--- | :--- |
| **Conhecimento** | Externo, dinâmico (banco vetorial). | Interno, estático (pesos do modelo). |
| **Atualização** | Imediata (basta inserir no DB). | Lenta (precisa re-treinar). |
| **Alucinação** | Baixa (ancorado em documentos). | Média/Alta (se não souber, inventa). |
| **Uso Principal** | Dar acesso a dados privados/recentes. | Ensinar um *formato*, *estilo* ou *linguagem* nova. |

> **Veredito:** 90% dos casos de uso de "dados da minha empresa" são resolvidos com RAG, não Fine-Tuning.

---

## 🔗 Referências Essenciais

*   [OpenAI Deep Learning (Andrej Karpathy)](https://www.youtube.com/watch?v=zjkBMFhNj_g) - Intro técnica obrigatória.
*   [Anthropic's Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) - Um dos melhores guias práticos.
*   [Lilian Weng Blog (OpenAI)](https://lilianweng.github.io/) - Artigos profundos sobre Agentes e LLMs.

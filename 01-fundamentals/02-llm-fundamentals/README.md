# 🤖 Módulo 06: Fundamentos de LLMs & GenAI

> **Goal:** Entender profundamente a matéria‑prima da nova computação.
>
> Este módulo não ensina a *usar ferramentas*. Ele ensina a **pensar como um AI Engineer que trabalha com LLMs em produção**.

---

## 📌 O que são LLMs, de verdade

Large Language Models (LLMs) são **modelos probabilísticos autoregressivos** treinados para prever o próximo token com base em um histórico de tokens.

Isso significa algo extremamente importante:

> ❗ O modelo **não pensa, não raciocina e não entende**.
>
> Ele calcula probabilidades condicionais extremamente bem.

Tudo o que parece “inteligência” emerge de escala:

* bilhões de parâmetros
* trilhões de tokens
* arquiteturas Transformer

O papel do AI Engineer não é treinar isso.
É **domar, controlar e orquestrar esse comportamento probabilístico**.

---

## 🧠 A arquitetura mental correta

Antes de qualquer conceito técnico, guarde isto:

> Um LLM é um *motor estatístico de linguagem com memória temporária limitada*.

Ele:

* não possui estado persistente
* não lembra de interações passadas
* não sabe o que é verdade
* não acessa bancos
* não executa código

Tudo isso **precisa ser construído ao redor dele**.

Essa é a diferença entre:

* *prompt engineer* ❌
* *AI engineer* ✅

---

# 1️⃣ Tokenização — A Unidade Atômica

LLMs não trabalham com palavras.
Eles trabalham com **tokens**.

### O que é um token?

Um token é um fragmento estatístico de texto.
Pode ser:

* uma palavra
* parte de uma palavra
* um número
* um símbolo

Exemplos:

* "inteligência" → pode virar 3 ou 4 tokens
* "9.11" pode gerar mais tokens que "9.9"

Isso acontece porque o tokenizer aprende padrões estatísticos, não semânticos.

---

### Por que isso importa?

Porque **tudo em LLM é limitado por tokens**:

* Context window
* Custo
* Latência
* Performance

Um modelo com contexto de 128k tokens **não pensa melhor**.
Ele apenas consegue **ver mais texto ao mesmo tempo**.

---

### Input vs Output tokens

Isso é fundamental em produção:

* **Input tokens** → geralmente baratos
* **Output tokens** → geralmente caros

Por isso:

* prompts longos custam
* respostas longas custam muito mais

AI Engineer bom otimiza:

* contexto
* tamanho de chunk
* quantidade de documentos
* verbosity da resposta

---

# 2️⃣ Context Window — A Memória Temporária

LLMs possuem apenas **memória de curto prazo**.

Essa memória é o *context window*.

Tudo fora disso:

* não existe
* não é lembrado
* não influencia a resposta

Por isso:

* conversas longas degradam
* RAG existe
* agentes precisam resumir

O modelo não “lembra”.
Você precisa **reenviar o que importa**.

---

# 3️⃣ O Ciclo de Vida do Prompt

Prompt engineering não é escrever texto bonito.

É **engenharia de contexto**.

Um prompt completo possui três camadas:

---

## 3.1 System Prompt

O system prompt define:

* papel do modelo
* comportamento
* limites
* regras

Ele atua como uma **camada constitucional**.

Exemplo conceitual:

* você é um auditor
* responda apenas com base no contexto
* nunca invente informações

Em produção, esse prompt deve ser:

* versionado
* testado
* tratado como código

---

## 3.2 Few‑Shot Learning

Modelos aprendem melhor por exemplo do que por instrução.

Few‑shot é quando você mostra:

> "Quando a entrada for assim, a saída esperada é assim."

Isso é extremamente poderoso para:

* formatos
* classificação
* padronização
* tomada de decisão

LLMs copiam padrões estatísticos.
Few‑shot explora isso diretamente.

---

## 3.3 User Prompt

É a parte dinâmica.

Nunca deve conter regras críticas.
Nunca deve definir comportamento.

Tudo que é importante deve estar no system prompt.

---

# 4️⃣ Temperatura, Top‑P e Amostragem

Esses parâmetros controlam **aleatoriedade**.

* Temperature baixa → respostas determinísticas
* Temperature alta → criatividade

Em produção:

* temperatura costuma ser baixa (0–0.3)
* previsibilidade é mais importante que criatividade

LLM corporativo ≠ chatbot criativo.

---

# 5️⃣ Structured Outputs — Probabilístico → Determinístico

LLMs são probabilísticos.
Produção exige determinismo.

A solução é **Structured Output**.

Nunca confie em:

* markdown
* regex
* parsing textual

Sempre use:

* JSON Schema
* response_format
* tool calling

Isso transforma o LLM em um **gerador de objetos válidos**.

Esse é um dos pilares mais importantes da engenharia moderna com LLMs.

---

# 6️⃣ Tool Calling (Function Calling)

Aqui ocorre a virada de chave.

O LLM não executa ações.

Mas ele pode:

* decidir qual ação executar
* estruturar os argumentos
* delegar execução

Fluxo real:

1. Usuário pergunta algo
2. LLM decide chamar uma função
3. Retorna JSON estruturado
4. Seu código executa
5. Resultado volta ao LLM

Isso cria **agentes reais**.

---

### O LLM não age. Ele orquestra.

Quem executa é:

* Python
* APIs
* bancos
* serviços

O LLM apenas escolhe.

Esse princípio é crítico.

---

# 7️⃣ LLM ≠ Agente

Um erro comum:

> "Estou usando agentes porque uso LLM."

Errado.

Um agente possui:

* objetivo
* ferramentas
* estado
* loop de decisão

O LLM é apenas o cérebro probabilístico.

Frameworks como:

* LangGraph
* CrewAI
* AutoGen

existem para construir o **loop de controle**.

---

# 8️⃣ Multimodalidade

LLMs modernos operam com:

* texto
* imagem
* áudio
* vídeo

Tudo vira embedding.

Isso permite:

* análise de documentos escaneados
* interpretação de imagens
* agentes visuais
* pipelines multimodais

Pensar só em texto hoje é limitar brutalmente o potencial do sistema.

---

# 9️⃣ Fine‑Tuning vs RAG vs Prompt

Essa decisão separa amadores de engenheiros.

### Prompt Engineering

* rápido
* barato
* flexível

Ideal quando:

* regras mudam
* contexto é pequeno

---

### RAG

* injeta conhecimento externo
* mantém modelo genérico
* altamente escalável

Ideal quando:

* dados são privados
* documentos mudam
* auditoria é necessária

---

### Fine‑Tuning

* caro
* rígido
* difícil de versionar

Só vale quando:

* padrão é extremamente repetitivo
* latência precisa ser mínima
* prompt não resolve

AI Engineer experiente evita fine‑tuning prematuro.

---

# 🔟 Alucinação — Não é bug, é característica

O modelo sempre tenta responder.

Se não sabe, ele:

* completa estatisticamente

Isso gera hallucination.

Soluções reais:

* grounding
* RAG
* citações
* validação
* confiança mínima

Nunca confie apenas no modelo.

---

# 🧠 O papel real do AI Engineer

O trabalho não é fazer o modelo falar.

É:

* controlar contexto
* limitar comportamento
* estruturar respostas
* validar saídas
* medir qualidade
* reduzir custo
* garantir confiabilidade

O LLM é só um componente.

O sistema é o produto.

---

# ✅ Conclusão

LLMs são a nova CPU.

Mas uma CPU sozinha não resolve nada.

O verdadeiro poder está em:

* arquitetura
* dados
* controle
* engenharia

Dominar esses fundamentos é o que separa:

* quem faz demo
* de quem constrói sistemas de IA reais

---

⏭️ **Próximo passo:**
Sem memória externa, o LLM continua cego.

Vá para **Módulo 08 — RAG (Retrieval‑Augmented Generation)**.

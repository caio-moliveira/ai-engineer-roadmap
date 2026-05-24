# 🎯 Aula 1: Fundamentos de Fine-Tuning

> **Objetivo:** Construir o modelo mental correto antes de escrever uma linha de código.
> **Pergunta-chave:** O que está acontecendo no nível dos parâmetros quando você fine-tuna?

Antes de discutir quando usar fine-tuning, você precisa entender o que está acontecendo nos pesos do modelo. Esta aula constrói a base conceitual: pré-treino, instruction tuning e as três famílias de fine-tuning (Full, LoRA, QLoRA) — com a matemática que justifica cada uma.

---

## 1. As três fases de um LLM

Um LLM moderno passa por **três fases distintas** antes de chegar nas suas mãos. Cada uma tem propósito, custo e dataset diferentes — e cada uma tem cerca de 3 ordens de magnitude menos dados que a anterior.

| Fase | O que faz | Dataset | Custo |
|------|-----------|---------|-------|
| **1. Pré-treino** | Predição next-token em texto bruto | TB de texto da web | Milhões de USD |
| **2. Instruction Tuning** | SFT + RLHF/DPO para aprender a "conversar" | Milhões de pares (instrução, resposta) | Centenas de milhares |
| **3. Fine-Tuning (você)** | SFT em tarefa específica | Centenas a milhares de exemplos do **seu** domínio | USD a centenas |

O modelo que você baixa do Hugging Face (`Qwen2.5-Coder-1.5B-Instruct`, por exemplo) **já passou pelas fases 1 e 2**. Você está adicionando uma quarta camada, muito fina, em cima.

> *"We propose a method called instruction tuning, which we define as supervised fine-tuning on a collection of NLP datasets described via natural language instructions."*
> — Wei et al., 2021 ([FLAN](https://arxiv.org/abs/2109.01652))

---

## 2. O que fine-tuning **realmente** faz

**Definição operacional:** fine-tuning é continuar o treino supervisionado de um modelo já treinado em um dataset menor e mais específico, com *learning rates muito baixos*, para que ele incorpore padrões da sua tarefa sem destruir o conhecimento geral.

### O que ele faz bem
- **Formato.** Output sempre em JSON específico, sempre em markdown estruturado, sempre com determinada assinatura.
- **Estilo.** Tom de voz, vocabulário, registro (formal, técnico, conversacional).
- **Convenções de domínio.** Padrões idiossincráticos: "número da lei sempre sem ponto", "inciso sempre em romano maiúsculo".
- **Comportamento condicional.** "Se a entrada não tiver lei nenhuma, devolva lista vazia" (negativos).

### O que ele **não** faz
- **Não injeta conhecimento factual atualizado.** Você não fine-tuna para o modelo "saber" da decisão do STF de ontem.
- **Não ensina raciocínio que o modelo base não tem.** Se Qwen 1.5B não sabe resolver derivadas, treinar em 500 exemplos não vai criar essa capacidade do nada.
- **Não substitui RAG.** Conhecimento que muda com frequência continua em RAG, mesmo em pipeline fine-tunado.

> ⚠️ **A confusão clássica:** "Fine-tunei meu modelo nos meus PDFs internos e ele continua errando os fatos." É esperado. FT ensina **formato e padrão**, não fatos. Para fatos use RAG. A Aula 2 desenrola isso em detalhe.

---

## 3. As três famílias: Full FT, LoRA, QLoRA

Quando você fine-tuna, está atualizando matrizes de pesos. Há três estratégias dependendo de **quais** e **como** você atualiza essas matrizes.

### Full Fine-Tuning
Atualiza **todos** os parâmetros do modelo. Custo de memória brutal: cada parâmetro precisa de ~12 bytes (peso fp16 + gradiente fp16 + estados Adam fp32). Para um modelo de 7B isso significa **~84 GB de VRAM mínimo**. Uma RTX 3060 tem 12 GB. Você simplesmente não treina full FT em GPU consumer.

### LoRA — Low-Rank Adaptation
Insight de [Hu et al., 2021](https://arxiv.org/abs/2106.09685): quando você fine-tuna um modelo grande, a matriz de atualização `ΔW` tem rank intrínseco baixo. Logo, é representável com muito menos parâmetros que a matriz original.

```
ΔW ≈ A × B     onde   A ∈ ℝ^(d×r),  B ∈ ℝ^(r×d),  r << d

# d = 1024  (dimensão latente do modelo)
# r = 16    (rank escolhido — tipicamente 4 a 64)

# Parâmetros originais: d × d  = 1.048.576
# Parâmetros LoRA:    2 × d × r =    32.768  (3% do original)
```

O modelo base fica **congelado**. Você só treina A e B. O resultado é um "adapter" de ~70 MB que você anexa ao modelo base na inferência.

### QLoRA — LoRA + quantização 4-bit
[Dettmers et al., 2023](https://arxiv.org/abs/2305.14314) levou ao extremo: carregar o modelo base em **4-bit** (NF4, distribuição calibrada para pesos de redes neurais) e treinar adapters em cima. Permite fine-tunar modelos de 65B em uma única GPU de 48 GB.

### Comparativo

| Critério | Full FT | LoRA | QLoRA |
|----------|---------|------|-------|
| **Parâmetros treinados** | 100% | 0.1% – 3% | 0.1% – 3% |
| **VRAM (modelo 7B)** | ~84 GB | ~16 GB | ~6 GB |
| **Qualidade final** | Teto | ~95-99% do Full | ~95-99% do Full |
| **Catastrophic forgetting** | Alto risco | Baixo (base congelado) | Baixo (base congelado) |
| **Quando usar** | Mudança radical de domínio + GPU sobrando | **Default moderno** para tarefa específica | Modelo grande + GPU limitada |

No nosso projeto (Qwen 1.5B em RTX 3060 de 12 GB), **bf16 já cabia**, então usamos LoRA puro sem necessidade de QLoRA.

---

## 4. Catastrophic forgetting e por que LoRA é seguro

**Catastrophic forgetting** (McCloskey & Cohen, 1989) é o fenômeno onde uma rede neural, ao aprender uma nova tarefa, "esquece" o que aprendeu antes. Em LLMs aparece como: você fine-tuna em JSON jurídico e o modelo passa a responder em JSON até para "olá, tudo bem?".

LoRA mitiga isso por construção: **os pesos originais ficam congelados**. Você adiciona uma "perturbação" em cima, e pode até desligá-la em runtime — basta não carregar o adapter que o modelo volta a ser ele mesmo.

> 💡 **Mental model útil:** pense no modelo base como um **profissional generalista**. Fine-tuning com LoRA é dar a ele um **caderno de notas específico** ("nessa empresa fazemos assim, nesse formato"). Ele consulta o caderno quando o adapter está ativo, mas não desaprende a profissão.

---

## 5. As 5 perguntas antes de uma linha de código

Antes de instalar PyTorch, você deve ter **respostas claras** para cinco perguntas. Se qualquer uma estiver vaga, pare e refine — vai te poupar dias de retrabalho.

1. **Que tarefa?** Bem definida, input e output claros. "Melhorar respostas" não é tarefa. "Extrair citações de leis brasileiras em JSON estrito a partir de parágrafos jurídicos em pt-BR" é.
2. **Que modelo base?** Pequeno o suficiente para sua GPU, grande o suficiente para a tarefa, com características relevantes (suporte ao idioma, variante "Coder" se output é estruturado).
3. **Que dataset?** Quantos exemplos, de onde vêm, como validar qualidade. Tem que ser concreto antes de gastar com geração ou anotação.
4. **Que hardware?** Define método (LoRA vs QLoRA), precisão (bf16 vs fp16), batch size, e até o modelo viável.
5. **Que critério de sucesso?** Métricas mensuráveis com thresholds aceitáveis, *definidos antes do treino*. A Aula 3 mostra como isso vira o PRD.

---

## 📚 Referências da aula

- **Wei et al. (2021).** *Finetuned Language Models Are Zero-Shot Learners*. — [arxiv.org/abs/2109.01652](https://arxiv.org/abs/2109.01652)
- **Ouyang et al. (2022).** *Training language models to follow instructions with human feedback* (InstructGPT). — [arxiv.org/abs/2203.02155](https://arxiv.org/abs/2203.02155)
- **Hu et al. (2021).** *LoRA: Low-Rank Adaptation of Large Language Models*. — [arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)
- **Dettmers et al. (2023).** *QLoRA: Efficient Finetuning of Quantized LLMs*. — [arxiv.org/abs/2305.14314](https://arxiv.org/abs/2305.14314)
- **Houlsby et al. (2019).** *Parameter-Efficient Transfer Learning for NLP* (paper original de adapters). — [arxiv.org/abs/1902.00751](https://arxiv.org/abs/1902.00751)
- **Hoffmann et al. (2022).** *Training Compute-Optimal Large Language Models* (Chinchilla scaling laws). — [arxiv.org/abs/2203.15556](https://arxiv.org/abs/2203.15556)
- **Hugging Face PEFT** — biblioteca usada no curso. [github.com/huggingface/peft](https://github.com/huggingface/peft)

---

## ⏭️ Próximo passo

Sabendo o que FT é, quando comparar com RAG e prompting?
Vá para **[Aula 2: Raio-X — Prompt vs RAG vs Fine-Tuning](../02-x-ray-fine-tunning)**.

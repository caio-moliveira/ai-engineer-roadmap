# 🔹 Bloco 5: Fine-Tuning e Melhora de Modelo

> **Objetivo:** Saber quando treinar — e principalmente quando NÃO treinar.  
> **Status:** A última milha da especialização.

## 🛑 Pare. Leia isto.
Fine-Tuning não resolve alucinação.
Fine-Tuning não adiciona conhecimento factual novo de forma confiável.
Fine-Tuning não é mágica.

Se você está aqui porque "o RAG não funcionou", volte para o Bloco 2.
Fine-Tuning é para **Forma**, **Estilo**, **Comportamento** e **Eficiência**, não para fatos.

Este bloco vai te ensinar a responsabilidade de "tocar nos pesos" do modelo.

---

## 📚 Ementa do Módulo

### [Módulo 1: O que é Fine-Tuning (Realmente)](./01-finetuning-concepts)
- **Realidade:** Adaptação de pesos vs Injeção de Conhecimento.
- **Mito:** "Vou treinar o modelo nos meus PDFs para ele saber sobre minha empresa." (Spoiler: Não vai funcionar).
- **Fato:** Fine-Tuning ensina o modelo a FALAR como um médico, não a SER um médico.

### [Módulo 2: Fine-Tuning vs RAG vs Prompting](./02-rag-vs-finetuning)
- **Matriz de Decisão:** O framework definitivo para escolher a abordagem.
- **RAG:** Para fatos novos e dinâmicos.
- **Fine-Tuning:** Para estilo consistente e redução de latência/custo.
- **Prompting:** Onde você deve gastar 90% do seu tempo inicial.

### [Módulo 3: Tipos de Adaptação](./03-adaptation-types)
- **Full Fine-Tuning:** Por que você quase nunca vai fazer isso.
- **PEFT / LoRA:** Como treinar modelos gigantes com pouco VRAM.
- **Instruction Tuning:** Ensinando o modelo a seguir ordens.
- **Likelihood Training (DPO/ORPO):** Ensinando o modelo o que você prefere.

### [Módulo 4: Dados são o Modelo](./04-data-prep)
- **A Verdade:** O modelo é apenas um espelho dos seus dados.
- **Qualidade > Quantidade:** 100 exemplos perfeitos valem mais que 10.000 exemplos ruins.
- **Instruction Datasets:** Como formatar seus dados corretamente.

### [Módulo 5: Avaliação antes do Treino](./05-evaluation)
- **Regra:** Se você não consegue medir, não treine.
- **Baselines:** Como saber se o treino piorou o modelo (Catastrophic Forgetting).
- **LLM-as-a-Judge:** Usando GPT-4 para dar nota no seu Llama-3 finetunado.

### [Módulo 6: Unsloth (Prático)](./06-unsloth)
- **A Ferramenta:** Por que Unsloth é o padrão ouro hoje.
- **Eficiência:** Treinando 2x mais rápido com 70% menos memória.
- **Workflow:** Do notebook para o GGUF/LoRA Adapter.

### [Módulo 7: Infra de Treino & Custo Real](./07-training-ops)
- **Hardware:** Quanto de VRAM você realmente precisa.
- **Spot Instances:** Economizando 70% na AWS/RunPod.
- **Custo Oculto:** O tempo de engenharia para limpar dados vs o custo de GPU.

### [Módulo 8: Deploy & Inferência Pós-Treino](./08-deploy-adapters)
- **Adapters:** Como carregar LoRA adapters no vLLM sem duplicar o modelo base.
- **Merge:** Quando fundir os pesos (Mergekit) e quando carregar dinamicamente.
- **Drift:** Monitorando se o modelo "desaprendeu" coisas importantes.

### [Módulo 9: Riscos & Manutenção](./09-risks-maintenance)
- **Catastrophic Forgetting:** O modelo ficou ótimo em SQL, mas esqueceu como falar inglês.
- **Manutenção:** Modelo treinado é modelo "congelado". Como atualizar?

### [Módulo 10: Enterprise & Gov](./10-enterprise-gov)
- **Compliance:** Quando o Fine-Tuning é obrigatório por lei (On-premise total).
- **Privacidade:** Garantindo que dados sensíveis não vazem.

---

## 🛠️ Stack de Treino (Padrão 2025)

| Componente | Escolha | Por quê? |
|:---|:---|:---|
| **Framework** | Unsloth | Velocidade e eficiência de memória imbatíveis. |
| **Técnica** | QLoRA (4-bit) | Permite treinar 70B em GPUs "baratas" (A6000/A100). |
| **Eval** | Ragas / LLM-as-Judge | Avaliação escalável antes de deploy. |
| **Dataset** | Hugging Face Datasets | Gerenciamento e versionamento de dados. |

## 🧠 Mudanças Mentais Necessárias
- **Menos é Mais:** Comece com 50 exemplos. Teste. Se melhorar, adicione mais.
- **Dados são Código:** Trate seu dataset com o mesmo rigor que trata seu código (versionamento, code review, linting).
- **Você provavelmente não precisa de Fine-Tuning:** Sério. RAG + Few-Shot Prompting resolve 95% dos casos.

## 🚀 Como começar
Vá para **[Módulo 1: O que é Fine-Tuning (Realmente)](./01-finetuning-concepts)**.


### 6. Inference optimization

Text generation is a costly process that requires expensive hardware. In addition to quantization, various techniques have been proposed to maximize throughput and reduce inference costs.

* **Flash Attention**: Optimization of the attention mechanism to transform its complexity from quadratic to linear, speeding up both training and inference.
* **Key-value cache**: Understand the key-value cache and the improvements introduced in [Multi-Query Attention](https://arxiv.org/abs/1911.02150) (MQA) and [Grouped-Query Attention](https://arxiv.org/abs/2305.13245) (GQA).
* **Speculative decoding**: Use a small model to produce drafts that are then reviewed by a larger model to speed up text generation. EAGLE-3 is a particularly popular solution.

📚 **References**:
* [GPU Inference](https://huggingface.co/docs/transformers/main/en/perf_infer_gpu_one) by Hugging Face: Explain how to optimize inference on GPUs.
* [LLM Inference](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices) by Databricks: Best practices for how to optimize LLM inference in production.
* [Optimizing LLMs for Speed and Memory](https://huggingface.co/docs/transformers/main/en/llm_tutorial_optimization) by Hugging Face: Explain three main techniques to optimize speed and memory, namely quantization, Flash Attention, and architectural innovations.
* [Assisted Generation](https://huggingface.co/blog/assisted-generation) by Hugging Face: HF's version of speculative decoding. It's an interesting blog post about how it works with code to implement it.
* [EAGLE-3 paper](https://arxiv.org/abs/2503.01840?utm_source=chatgpt.com): Introduces EAGLE-3 and reports speedups up to 6.5×.
* [Speculators](https://github.com/vllm-project/speculators): Library made by vLLM for building, evaluating, and storing speculative decoding algorithms (e.g., EAGLE-3) for LLM inference.
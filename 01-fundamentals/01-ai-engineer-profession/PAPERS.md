## 📚 10 *Papers* que todo AI Engineer deve ler (com links)

1. **Attention Is All You Need** (Vaswani et al., 2017)
   Arquitetura *Transformer*, base de todos os LLMs modernos. ([Wikipedia][2])
   📄 [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)

2. **Language Models are Few-Shot Learners** (Brown et al., 2020)
   GPT-3 — mostra a capacidade de *in-context learning* e *few-shot learning*. ([Medium][1])
   📄 [https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)

3. **Training Language Models to Follow Instructions with Human Feedback** (InstructGPT / RLHF)
   Introduz *Reinforcement Learning from Human Feedback* para alinhamento de LLMs. ([LinkedIn][3])
   📄 [https://arxiv.org/abs/2203.02155](https://arxiv.org/abs/2203.02155)

4. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** (RAG)
   Combina *retrieval* e *generation* para respostas mais precisas e atualizadas. ([robertodiasduarte.com.br][4])
   📄 [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

5. **LoRA: Low-Rank Adaptation of Large Language Models**
   Técnica para *fine-tuning* eficiente e barato de LLMs. ([LinkedIn][5])
   📄 [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)

6. **Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity**
   Mostra como escalar LLMs com *Mixture of Experts* (MoE). ([LinkedIn][6])
   📄 [https://arxiv.org/abs/2101.03961](https://arxiv.org/abs/2101.03961)

7. **LLM.int8(): 8-Bit Matrix Multiplication for Transformers at Scale**
   Quantização eficiente para rodar LLMs com menor custo de memória/computação. ([LinkedIn][6])
   📄 [https://arxiv.org/abs/2309.04643](https://arxiv.org/abs/2309.04643)

8. **DistilBERT: A Distilled Version of BERT** (Sanh et al., 2019)
   Demonstrou *distillation* como forma de criar modelos menores e rápidos. ([LinkedIn][6])
   📄 [https://arxiv.org/abs/1910.01108](https://arxiv.org/abs/1910.01108)

9. **Chain of Thought Prompting** (Wei et al., 2022)
   Explora como decompor lógica do modelo para melhor raciocínio. ([LinkedIn][5])
   📄 [https://arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)

10. **Scaling Laws for Neural Language Models** (Kaplan et al., 2020)
    Mostra relações previsíveis de performance com tamanho de modelo e dados. ([LinkedIn][5])
    📄 [https://arxiv.org/abs/2001.08361](https://arxiv.org/abs/2001.08361)

---

## 💡 Como usar essa lista na sua documentação

### 🎯 Para cada paper:

```markdown
### 1. Attention Is All You Need
**Resumo:** Introduziu a arquitetura Transformer que revolucionou NLP e tornou viáveis modelos de linguagem em grande escala.  
**Por que ler:** Base para entender como LLMs funcionam por dentro.  
**Link:** https://arxiv.org/abs/1706.03762
```

### 📌 Sugerido para capítulos:

| Tópico curricular                       | Papers recomendados                                                   |
| --------------------------------------- | --------------------------------------------------------------------- |
| **Fundamentos de LLMs**                 | *Attention Is All You Need*, *Language Models are Few-Shot Learners*  |
| **Alinhamento e comportamento**         | *Training Language Models to Follow Instructions with Human Feedback* |
| **RAG e sistemas conectados à memória** | *Retrieval-Augmented Generation*                                      |
| **Eficiência & produção**               | *LoRA*, *LLM.int8()*, *DistilBERT*, *Scaling Laws*                    |
| **Raciocínio & prompting avançado**     | *Chain of Thought Prompting*                                          |
| **Escala& arquitetura**                 | *Switch Transformers*                                                 |

---

## 🧠 Por que este conjunto importa para um AI Engineer

Esses papers **não são apenas teoria** — eles explicam:

* **Como os modelos são construídos (Transformers).**
* **Como eles aprendem com pouco contexto (GPT-3).**
* **Como alinhá-los a intenções humanas (RLHF).**
* **Como conectá-los a conhecimentos externos (RAG).**
* **Como otimizar e operar modelos em produção (LoRA, quantização).**
* **Como decompor tarefas complexas (Chain of Thought).**

Juntos, eles formam uma base sólida para quem quer trabalhar **com sistemas de IA em produção**, não apenas treinar modelos em notebooks.


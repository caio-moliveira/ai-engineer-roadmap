# ⚖️ Módulo 2: Fine-Tuning vs RAG vs Prompting

> **Goal:** O Framework de Decisão.  
> **Status:** Imprima e cole na parede.

## 1. A Hierarquia de Soluções
Resolva problemas nesta ordem estrita:

1.  **Prompt Engineering:**
    - "Você é um especialista em SQL. Responda apenas o código."
    - Custo: Zero. Tempo: Minutos.
2.  **RAG (Retrieval Augmented Generation):**
    - "Use este schema do banco para gerar SQL."
    - Custo: Médio (Vector DB). Tempo: Dias.
3.  **Fine-Tuning:**
    - "O modelo erra a sintaxe do meu dialeto SQL proprietário mesmo com exemplos no prompt."
    - Custo: Alto (GPU + Dados). Tempo: Semanas.

## 2. A Comparação Brutal

| Critério | Prompting | RAG | Fine-Tuning |
|:---|:---|:---|:---|
| **Conhecimento Novo** | Baixo (Janela de Contexto) | Alto (Vector DB ilimitado) | Médio/Baixo (Difícil injetar) |
| **Mudança de Estilo** | Médio | Baixo | Alto (Imita perfeitamente) |
| **Latência** | Alta (Prompts longos) | Alta (Retrieval + Prompt) | Baixa (Prompt curto) |
| **Custo Inicial** | $0 | $$ | $$$$ |
| **Custo Manutenção** | $ | $$ | $$$$$ |

## 3. Checklist: "NÃO FAÇA FINE-TUNING SE..."
- [ ] Você tem menos de 100 exemplos de alta qualidade.
- [ ] O conhecimento muda toda semana (ex: notícias, estoque).
- [ ] Você ainda não tentou Few-Shot Prompting (dar 5 exemplos no prompt).
- [ ] Você não tem uma pipeline de avaliação automatizada.

## 🧠 Mental Model: "A Curva de Retorno"
- Prompting dá 80% do resultado com 1% do esforço.
- RAG dá +15% com 20% do esforço.
- Fine-Tuning dá os últimos +5% com 200% do esforço.

## ⏭️ Próximo Passo
Se você REALMENTE precisa treinar, qual método usar?
Vá para **[Módulo 3: Tipos de Adaptação](../03-adaptation-types)**.

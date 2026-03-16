# 📊 Módulo 4: Dados são o Modelo

> **Goal:** Garbage In, Garbage Out muito rápido.  
> **Status:** Onde você vai gastar 80% do tempo.

## 1. O Paradoxo da Quantidade
Para treinar um LLM do zero: Precisa de Trilhões de tokens.
Para fazer Fine-Tuning: Precisa de **Centenas** de exemplos de *Extrema Qualidade*.

> Um dataset com 100 exemplos perfeitos (Quality > Quantity) supera um dataset com 10.000 exemplos sujos.

## 2. O Formato de Instrução
O modelo não aprende com texto solto. Ele aprende com pares.

```json
{
  "instruction": "Traduza para SQL do BigQuery.",
  "input": "Quantos usuários ativos ontem?",
  "output": "SELECT count(*) FROM `users` WHERE last_active = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)"
}
```

## 3. Negative Examples (Não faça isso)
Se você quer que o modelo pare de ser verboso, não corte apenas os exemplos verbosos.
Mostre exemplos onde ele *seria* verboso, e ensine a resposta curta.
Ou use DPO (Direct Preference Optimization) onde você explicitamente diz "Esta resposta curta vence esta resposta longa".

## 4. Onde conseguir dados?
1.  **Logs de Produção:** O melhor dataset são as perguntas reais dos seus usuários.
2.  **LLM Synthetic Data:** Use o GPT-4o para gerar exemplos de treino para o Llama-3-8B. (Destilação de Modelo).
3.  **Human Review:** Pague humanos para corrigir os dados sintéticos.

## 🧠 Mental Model: "Livro Didático"
Prepare seu dataset como se estivesse escrevendo um livro didático para uma criança.
Exemplos claros. Sem ambiguidade. Formato consistente.

## ⏭️ Próximo Passo
Como saber se o dataset é bom *antes* de gastar dinheiro com GPU?
Vá para **[Módulo 5: Avaliação antes do Treino](../05-evaluation)**.

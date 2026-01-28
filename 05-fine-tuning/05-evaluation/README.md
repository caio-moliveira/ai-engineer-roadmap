# 📉 Módulo 5: Avaliação antes do Treino (Obrigatório)

> **Goal:** Evitar o "Vibe Check".  
> **Status:** A diferença entre Ciência e Alquimia.

## 1. O Perigo do "Olhômetro"
Você treinou. Você abre o chat. Você pergunta "Oi". O modelo responde "Olá".
Você conclui: "O modelo está ótimo!"
Narrador: "O modelo não estava ótimo. Ele esqueceu como somar 2+2."

## 2. Crie o "Golden Set" (Conjunto Ouro)
Antes de sequer pensar em ligar a GPU:
1.  Separe 50 perguntas difíceis que representam seu problema real.
2.  Escreva (você mesmo, humano) as respostas perfeitas para elas.
3.  Essas 50 perguntas **NUNCA** entram no treino. Elas são o Test Set.

## 3. Métricas Automáticas
Não use BLEU ou ROUGE (métricas de tradução). Elas são inúteis para a maioria dos casos de LLM.
Use **LLM-as-a-Judge**:
- Peça para o GPT-4 comparar a resposta do seu Modelo Finetunado com a resposta do Golden Set.
- Dê uma nota de 1 a 5.

## 4. Regressão (Não piore o modelo)
Execute benchmarks gerais (MMLU, GSM8K) antes e depois.
Se o seu modelo treinado para SQL perdeu 20% de performance em Lógica, você teve **Catastrophic Forgetting**.
Você precisa diminuir o Learning Rate ou adicionar dados de "replay" (dados gerais misturados com dados específicos).

## 🧠 Mental Model: "Unit Tests para o Cérebro"
Você não faz deploy de código sem testes.
Não faça deploy de pesos sem evals.

## ⏭️ Próximo Passo
Mão na massa. Vamos usar Unsloth.
Vá para **[Módulo 6: Unsloth](../06-unsloth)**.

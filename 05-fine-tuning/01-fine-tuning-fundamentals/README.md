# 🎯 Módulo 1: O que é Fine-Tuning (Realmente)

> **Goal:** Desfazer a lavagem cerebral do marketing.  
> **Status:** O conceito mais mal compreendido da IA.

## 1. O que muda no modelo?
Imagine que o LLM é um recém-graduado em Medicina (Base Model).
Ele sabe tudo sobre anatomia, doenças e tratamentos (Conhecimento Geral).

- **Fine-Tuning NÃO É:** Fazer ele decorar os prontuários dos *seus* pacientes específicos. (Isso é RAG).
- **Fine-Tuning É:** Ensinar ele a preencher o formulário específico do seu hospital, usando as siglas que seu hospital usa. (Isso é Adaptação de Comportamento).

> **Regra:** Fine-Tuning muda a **FORMA** como o modelo fala, não o que ele **SABE**.

## 2. Parameter Adaptation vs Knowledge Injection
- **Parameter Adaptation (Fine-Tuning):** Ajusta os pesos para alterar a distribuição de probabilidade das próximas palavras.
    - Ex: "Após 'Paciente', sempre diga 'Idade:'".
- **Knowledge Injection (RAG):** Fornece dados no contexto.
    - Ex: "Paciente: João, Idade: 45".

## 3. Mitos Comuns
- **"Vou fazer fine-tuning para ele parar de alucinar."**
    - **FALSO.** Se o conhecimento não está nos pesos do pré-treino, o FT só vai fazer ele alucinar com mais confiança no formato desejado.
- **"Vou fazer fine-tuning para ele aprender a lei brasileira de 2024."**
    - **RISCO.** Ele pode decorar alguns exemplos, mas terá dificuldade em generalizar. Use RAG para leis.

## 🧠 Mental Model: "O Ator de Método"
O modelo é um ator.
- **Pre-Training:** A escola de teatro. Ele sabe atuar.
- **RAG:** O roteiro que você entrega na hora.
- **Fine-Tuning:** O ensaio exaustivo para ele pegar o sotaque e os tiques do personagem.

## ⏭️ Próximo Passo
Tenho certeza que preciso treinar?
Vá para **[Módulo 2: Fine-Tuning vs RAG vs Prompting](../02-rag-vs-finetuning)**.

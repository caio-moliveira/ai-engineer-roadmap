<div align="center">
    <img src="../assets/jornada.png" alt="Jornada de Dados" width="200"/>

# 🔹Bloco 6: Modelos de Decisão (System One Models)

> Modelos que não geram texto: recebem um estado e perguntas tipadas e devolvem decisões com probabilidade.

<p align="center">
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  </a>
  <a href="https://docs.typesafe.ai/">
    <img alt="Jev" src="https://img.shields.io/badge/TypeSafe-Jev-111111?style=for-the-badge" />
  </a>
  <a href="https://huggingface.co/convaiinnovations/laya-multilingual">
    <img alt="Laya" src="https://img.shields.io/badge/Laya-Apache%202.0-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000000" />
  </a>
  <a href="https://langchain-ai.github.io/langgraph/">
    <img alt="LangGraph" src="https://img.shields.io/badge/LangGraph-Agente%20h%C3%ADbrido-1C3C3C?style=for-the-badge" />
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img alt="uv" src="https://img.shields.io/badge/uv-Python%20Package%20Manager-111111?style=for-the-badge&logo=astral&logoColor=white" />
  </a>
</p>

<div align="center">

### Tecnologias e padrões utilizados ao longo do módulo

Jev • Laya • Choice • Noul • Score • guardrail • roteamento • verificação de saída • agente híbrido em LangGraph

</div>
</div>

## Por que este bloco existe

Os blocos anteriores usam LLMs para tudo, inclusive para decidir: rotear um ticket, escolher uma tool, barrar uma mensagem, conferir uma resposta. Cada uma dessas decisões vira um prompt, um JSON gerado token a token e alguns segundos de espera.

Um modelo de decisão faz essas perguntas sem gerar texto. Devolve a probabilidade de cada resposta, em milissegundos e sem tokens de saída. O bloco mostra o que é isso, como usar os três tipos de pergunta e onde ele substitui o LLM num sistema real. Em todos os scripts, você vê os tokens e a latência de cada chamada.

## 📚 Ementa do Módulo

### [Aula 1: Fundamentos de modelos de decisão](./01-decision-fundamentals)
- **Pergunta-chave:** por que gerar texto para responder uma pergunta de múltipla escolha?
- O que é um modelo de decisão e o Jev; a mesma decisão no Jev, no GPT-5.6 Luna e no Claude Sonnet 5.5.

### [Aula 2: Choice](./02-choice)
- **Pergunta-chave:** quantas vezes o seu agente lê a descrição de todas as tools só para escolher uma?
- Roteamento de tickets com limiar de confiança e escolha de tool.

### [Aula 3: Noul](./03-noul)
- **Pergunta-chave:** "esta mensagem é perigosa?" é uma pergunta ou três?
- Perguntas de sim ou não e um guardrail com vários Nouls numa chamada.

### [Aula 4: Score](./04-score)
- **Pergunta-chave:** como transformar "quão urgente é isto?" num número que ordena uma fila?
- Urgência numa rubrica ordenada e rerank de trechos de RAG.

### [Aula 5: Quando usar o Jev](./05-when-to-use-jev)
- **Pergunta-chave:** quantas das chamadas de LLM do seu sistema geram texto que alguém vai ler?
- Decidir antes de gerar, verificar depois de gerar e o Laya, a alternativa open source.

### [Aula 6: Projeto final](./06-final-project)
- **Pergunta-chave:** quantas das chamadas do seu agente precisam mesmo de um LLM?
- Agente de atendimento em LangGraph: guardrail, triagem e verificação no Jev, resposta no LLM.

---

## Os modelos

| Modelo | Origem | Como o bloco acessa | Aulas |
|---|---|---|---|
| **Jev** | TypeSafe AI, API | `typesafe-sdk` | todas |
| **GPT-5.6 Luna** e **Claude Sonnet 5.5** | OpenAI e Anthropic | `init_chat_model` do LangChain | 1, 5 e 6 |
| **Laya** (`convaiinnovations/laya-multilingual`) | Convai Innovations, Apache 2.0 | local, mesma API do Jev | 5 e 6 |

## Glossário

- **Modelo de decisão (System One Model):** modelo que devolve decisões tipadas com probabilidade, sem gerar texto.
- **Estado:** o contexto da decisão (um ticket, uma mensagem, uma resposta a conferir).
- **Choice:** escolhe uma opção de uma lista. Devolve a opção, a confiança e a probabilidade de cada opção.
- **Noul:** a probabilidade de uma afirmação ser verdadeira.
- **Score:** um nível numa rubrica ordenada. Devolve a probabilidade de cada nível e o valor esperado.
- **Limiar:** o valor de confiança a partir do qual o código age sozinho.

## Como rodar

Configure o `.env` da raiz (veja o `.env.example`):

| Variável | Para quê |
|---|---|
| `TYPESAFE_API_KEY` | chamar o Jev (todas as aulas) |
| `ANTHROPIC_API_KEY` | Claude Sonnet 5.5 (aulas 1, 5 e 6) |
| `OPENAI_API_KEY` | GPT-5.6 Luna (aula 1; nas aulas 5 e 6, com `LLM_MODEL=openai:gpt-5.6-luna`) |
| `LAYA_BASE_URL` | onde o Laya responde (padrão `http://127.0.0.1:8001`) |

```bash
uv sync                                                        # da raiz do repositório
python 06-decision-models/01-decision-fundamentals/01_first_decision.py
docker compose --profile decision up -d laya                   # o Laya, para a Aula 5
```

Cada script é independente: abra, leia de cima para baixo e rode.

## Referências

- [TypeSafe: documentação](https://docs.typesafe.ai/), [SDK Python](https://docs.typesafe.ai/sdk/python/) e [primitivos](https://docs.typesafe.ai/primitives/choice)
- [Laya: documentação](https://nandhakishorm.github.io/laya/), [model card multilíngue](https://huggingface.co/convaiinnovations/laya-multilingual) e [GitHub](https://github.com/NandhaKishorM/laya)
- [Kahneman (2011). Rápido e Devagar: Duas Formas de Pensar](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow)
- [awesome-decision-models](https://github.com/sfmqrb/awesome-decision-models): lista comunitária de modelos de decisão

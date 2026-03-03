# 🧠 Módulo 5: Sistemas de Memória

> **Goal:** Dar aos agentes a capacidade de lembrar do passado.  
> **Status:** Crucial para chatbots e fluxos assíncronos.

Sem memória, cada interação com um LLM é como o filme "Como se Fosse a Primeira Vez". A revolução dos assistentes ocorreu quando percebemos que poderíamos injetar o histórico da conversa no prompt de cada nova requisição.

Neste módulo, demonstramos como implementar sistemas de memória usando ferramentas modernas focadas em **LangGraph** e **LangChain**, além de introduzir a recepção de inputs multimodais.

---

## 📚 Índice de Scripts Práticos

Todos os códigos rodam nativamente. Para executá-los, acesse a pasta e garanta ter o `.env` devidamente preenchido.

1. **[Conceitos Básicos de Memória](#1-conceitos-básicos-de-memória)** -> `python/01_memory_basics.py`
2. **[Mensagens Multimodais (Texto, Imagem, Áudio)](#2-mensagens-multimodais)** -> `python/02_multimodal_messages.py`

---

## 1. Conceitos Básicos de Memória

No script `python/01_memory_basics.py`, nós ilustramos a diferença brutal entre um agente ingênuo e um agente persistente.

### O Agente Amnésico
Quando instanciamos um agente puramente reativo, ele responde apenas à mensagem atual na lista. Informações ditas há dois minutos são perdidas.

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(model, tools=[])

# O agente não lembrará desta mensagem na próxima rodada
agent.invoke({"messages": [{"role": "user", "content": "Meu nome é Caio."}]})
```

### O Agente Memorável (LangGraph Checkpointers)
Para dotar o agente com memória de curto/longo prazo de maneira stateful, englobamos o uso de `checkpointers` providos pelo ecossistema LangGraph (ex: `InMemorySaver`, `SqliteSaver`, `PostgresSaver`).

E é vital compreender o conceito do `thread_id`. Ele funciona como o ID do chat!

```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

# Adiciona-se o checkpointer ao agente
agent = create_react_agent(model, tools=[], checkpointer=memory)

# É OBRIGATÓRIO invocar atrelando a um ID de Thread para salvar/pesquisar
config = {"configurable": {"thread_id": "usuario_caio_sessao_01"}}

# O checkpointer intercepta essa call, guarda e sempre resgata no futuro
agent.invoke({"messages": [mensagem_do_usuario]}, config)
```

---

## 2. Mensagens Multimodais

Com o surgimento de modelos Vision e Áudio nativos como o `GPT-4o`, LLMs não se limitam mais a Strings. No script `python/02_multimodal_messages.py` abordamos o envio de dicionários complexos contendo o campo `type`.

### Input de Imagem (`image_url`)
Para enviarmos imagens locais num script backend (`.py`), abrimos em bytes e convertemos para `Base64`.

```python
import base64
from langchain_core.messages import HumanMessage

# Leitura raw
with open("grafico.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# Injeção multimodal via dict content
msg = HumanMessage(content=[
    {"type": "text", "text": "Analise esta imagem:"},
    {
        "type": "image_url", 
        "image_url": {"url": f"data:image/png;base64,{img_b64}"}
    }
])

agent.invoke({"messages": [msg]})
```

### Input de Áudio (`input_audio`)
*(Específico para modelos capacitados como `gpt-4o-audio-preview`)*

De maneira análoga à imagem, encodamos o buffer gravado ou salvo localmente.

```python
# Requer Base64 do .Wav
msg = HumanMessage(content=[
    {"type": "text", "text": "Transcreva este áudio:"},
    {
        "type": "input_audio", 
        "input_audio": {"data": aud_b64, "format": "wav"}
    }
])
```

## 🧠 Mental Model

- Memorizar é puramente **"Anexar Histórico antigo para processar na próxima Call"**. Frameworks como LangGraph `checkpointers` automatizam esse estresse cuidando dos bancos SQL ou memória Cache nos bastidores e separando isso por ID de clientes (`thread_id`).
- Inputs multimodais exigem empacotamento. Em vez de uma `string` pura, envia-se uma `lista de blocos` tipados.

## ⏭️ Próximo Passo
Com Agentes inteligentes e memórias funcionais... É hora de dar "Mãos e Pernas" para eles trabalharem no mundo real.
Vá para **[Módulo 6: Tools & MCP](../05-tools-mcp)**.

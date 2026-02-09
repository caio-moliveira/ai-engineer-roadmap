# Integrações com LLMs em Python

Este diretório contém exemplos práticos de como integrar aplicações Python com Grandes Modelos de Linguagem (LLMs) utilizando três das principais bibliotecas do ecossistema de IA: **OpenAI SDK**, **LangChain** e **LlamaIndex**.

Abaixo explicamos cada um dos exemplos criados.

---

## 1. Integração Direta com OpenAI SDK (`openai_demo.py`)

O arquivo `openai_demo.py` demonstra como interagir diretamente com a API da OpenAI. Esta é a forma mais "crua" e flexível de acessar os modelos GPT.

### Estrutura do Código

O código utiliza o cliente `OpenAI` oficial. O fluxo básico consiste em:

1.  **Instanciação do Cliente**: `client = OpenAI(...)` carrega a chave de API (geralmente via variável de ambiente `OPENAI_API_KEY`).
2.  **Chamada de Chat Completion**: Utiliza `client.chat.completions.create` para enviar mensagens ao modelo.
3.  **Chat Format**: As mensagens são estruturadas como uma lista de dicionários com roles (`system`, `user`, `developer`, `assistant`).

```python
# Exemplo de chamada (simplificado)
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "developer", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Olá!"}
    ]
)
```

> **Nota**: O exemplo inclui também uma referência a métodos mais recentes/experimentais (`client.responses.create`), mas a API de `ChatCompletion` é o padrão da indústria atualmente.

### Documentação Oficial
- [OpenAI Python Library](https://github.com/openai/openai-python)
- [API Reference](https://platform.openai.com/docs/api-reference/chat)

---

## 2. Orquestração com LangChain (`langchain_demo.py`)

O arquivo `langchain_demo.py` introduz o **LangChain**, um framework poderoso para construir aplicações complexas com LLMs.

### Estrutura do Código

O exemplo utiliza a **LCEL (LangChain Expression Language)**, uma sintaxe declarativa para compor cadeias (chains).

1.  **ChatOpenAI**: Abstração do modelo de chat.
2.  **ChatPromptTemplate**: Templates reutilizáveis para prompts, permitindo injeção de variáveis (ex: `{topic}`).
3.  **StrOutputParser**: Parser que converte a resposta bruta do modelo (objeto AIMessage) para uma string simples.
4.  **Chain (|)**: O operador pipe `|` conecta os componentes: `Prompt -> Model -> Output`.

```python
# O fluxo de dados é definido de forma linear
chain = prompt | model | output_parser
```

Isso facilita a troca de modelos, adição de memória ou ferramentas sem reescrever toda a lógica.

### Documentação Oficial
- [LangChain Introduction](https://python.langchain.com/docs/get_started/introduction)
- [LCEL Documentation](https://python.langchain.com/docs/expression_language/)

---

## 3. Integração Direta com LlamaIndex (`llamaindex_demo.py`)

O arquivo `llamaindex_demo.py` demonstra que o **LlamaIndex** também pode ser usado apenas como uma abstração de LLM, sem necessariamente usar a parte de indexação e RAG.

### Estrutura do Código

1.  **OpenAI (LLM)**: Importado de `llama_index.llms.openai`. É a classe que encapsula a comunicação com o modelo.
2.  **llm.complete()**: Método simples para enviar um prompt e receber o texto de resposta.

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o-mini")
response = llm.complete("Hello World")
print(response)
```

Embora o foco principal do LlamaIndex seja conectar dados (Data Framework), ele possui abstrações robustas de LLM que podem ser usadas de forma "standalone".

### Documentação Oficial
- [LlamaIndex LLMs](https://docs.llamaindex.ai/en/stable/module_guides/models/llms/)
- [OpenAI in LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/llm/openai/)

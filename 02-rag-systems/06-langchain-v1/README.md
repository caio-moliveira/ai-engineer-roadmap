# 🦜🔗 Módulo 6: LangChain v1 (LCEL)

> **Goal:** Pare de usar "Chains". Comece a usar "Runnables".  
> **Status:** O protocolo padrão para composição.

## 1. Por que v1? (O Pivô)
O LangChain antigo (2023) era uma bagunça de wrappers (`RecallQAChain`, `LLMChain`). Escondia muita lógica.
LangChain v1 introduz **LCEL (LangChain Expression Language)**.
É uma forma **Declarativa** de encadear dados.

- **Antigo:** `Chain(llm, prompt)` (Caixa Preta).
- **Novo:** `Prompt | LLM | Parser` (Estilo Unix Pipe).

## 2. O Protocolo Runnable
Tudo no LangChain v1 é um `Runnable`.
Isso significa que todos implementam:
- `.invoke(input)`: Chamada síncrona.
- `.ainvoke(input)`: Chamada assíncrona.
- `.stream(input)`: Streaming de chunks.
- `.batch(input)`: Execução paralela.

## 3. Sintaxe LCEL
Chain RAG padrão:

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Definir Retriever
retriever = vectorstore.as_retriever()

# 2. Definir Chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | prompt 
    | llm 
    | StrOutputParser()
)

# 3. Rodar
rag_chain.invoke("Onde está o manual do usuário?")
```

## 4. Retrievers Customizados
Não dependa dos defaults. Construa sua lógica.

```python
from langchain_core.retrievers import BaseRetriever

class MyHybridRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str):
        # 1. Keyword Search
        bm25_docs = search_elastic(query)
        # 2. Vector Search
        vector_docs = search_qdrant(query)
        # 3. Rerank
        return rerank(bm25_docs + vector_docs)
```

## 🧠 Mental Model: "Unix Pipes para IA"
Se você conhece Linux, conhece `cat file.txt | grep "error" | wc -l`.
LCEL é exatamente isso.
`Input | Retrieve | Format | Generate | Parse`.

## ⚠️ Erros Comuns
- **Usar `ConversationalRetrievalChain`:** É legado/deprecado. Use `create_history_aware_retriever` ou LangGraph.
- **Não usar `.ainvoke`:** Em FastAPI, sempre use as versões async.

## ⏭️ Próximo Passo
Chains são DAGs (uma via). E se quisermos loops?
Vá para **[Módulo 7: LangGraph](../07-langgraph)**.

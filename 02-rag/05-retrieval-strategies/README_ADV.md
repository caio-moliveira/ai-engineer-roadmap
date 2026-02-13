### 4. Advanced RAG

Real-life applications can require complex pipelines, including SQL or graph databases, as well as automatically selecting relevant tools and APIs. These advanced techniques can improve a baseline solution and provide additional features.

* **Query construction**: Structured data stored in traditional databases requires a specific query language like SQL, Cypher, metadata, etc. We can directly translate the user instruction into a query to access the data with query construction.
* **Tools**: Agents augment LLMs by automatically selecting the most relevant tools to provide an answer. These tools can be as simple as using Google or Wikipedia, or more complex, like a Python interpreter or Jira. 
* **Post-processing**: Final step that processes the inputs that are fed to the LLM. It enhances the relevance and diversity of documents retrieved with re-ranking, [RAG-fusion](https://github.com/Raudaschl/rag-fusion), and classification.
* **Program LLMs**: Frameworks like [DSPy](https://github.com/stanfordnlp/dspy) allow you to optimize prompts and weights based on automated evaluations in a programmatic way.

📚 **References**:
* [LangChain - Query Construction](https://blog.langchain.dev/query-construction/): Blog post about different types of query construction.
* [LangChain - SQL](https://python.langchain.com/docs/tutorials/sql_qa/): Tutorial on how to interact with SQL databases with LLMs, involving Text-to-SQL and an optional SQL agent.
* [Pinecone - LLM agents](https://www.pinecone.io/learn/series/langchain/langchain-agents/): Introduction to agents and tools with different types.
* [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) by Lilian Weng: A more theoretical article about LLM agents.
* [LangChain - OpenAI's RAG](https://blog.langchain.dev/applying-openai-rag/): Overview of the RAG strategies employed by OpenAI, including post-processing.
* [DSPy in 8 Steps](https://dspy-docs.vercel.app/docs/building-blocks/solving_your_task): General-purpose guide to DSPy introducing modules, signatures, and optimizers.
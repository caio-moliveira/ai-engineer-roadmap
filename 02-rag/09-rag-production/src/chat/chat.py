import asyncio
from typing import List, AsyncIterator, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated

from src.chat.llm_models import gpt_4_1_mini, embedding
from src.chat.qdrant import aclient
from src.customlogger import setup_logger
from langfuse.langchain import CallbackHandler

logger = setup_logger(__name__)

# --- State Definition ---
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str
    file_context: Optional[str]
    collection_name: str

# --- Nodes ---

async def retrieve(state: ChatState, config: RunnableConfig):
    """Retrieve documents from Qdrant based on the last message."""
    messages = state["messages"]
    last_message = messages[-1]
    query = last_message.content
    
    logger.info(f"Retrieving context for query: {query}")

    # Generate embedding for the query
    query_vector = await embedding.aembed_query(query)
    
    # Perform search using query_points
    collection_name = state.get("collection_name", "unknown")
    search_result = await aclient.query_points(
        collection_name=collection_name,
        query=query_vector,
        using="text-dense",
        limit=5
    )
    
    # Extract content from payload
    # query_points returns a QueryResponse which has points
    docs_content = []
    
    # Check if search_result has 'points' attribute or is a list
    points = search_result.points if hasattr(search_result, 'points') else search_result
    
    logger.info(f"Retriever found {len(points)} documents.")
    
    for i, point in enumerate(points):
        # Try standard keys, fallback to JSON dump of payload
        payload = point.payload or {}
        logger.info(f"Payload keys for doc {i+1}: {list(payload.keys())}")
        if 'metadata' in payload:
             logger.info(f"Metadata content: {payload['metadata']}")

        text = payload.get("page_content") or payload.get("text") or payload.get("content")
        
        # Extract metadata for citation
        meta = payload.get("metadata", {})
        source = meta.get("nome_arquivo") or "Unknown File"
        page = meta.get("pagina") or ""
        score = point.score if hasattr(point, 'score') else "N/A"
        
        logger.info(f"Doc {i+1} (Score: {score}): {str(text)[:200]}...")
        
        if not text:
            text = str(payload)
            
        # Format context with XML-like tags or Markdown for clear separation and citation
        # giving each chunk an ID or Source reference
        formatted_chunk = (
            f"<document index='{i+1}'>\n"
            f"  <source>{source}</source>\n"
            f"  <page>{page}</page>\n"
            f"  <content>{text}</content>\n"
            f"</document>"
        )
        docs_content.append(formatted_chunk)
        

    context = "\n\n".join(docs_content)
    
    # Append file context if available
    file_context = state.get("file_context")
    if file_context:
        context += f"\n\n<FILE_CONTEXT>\n{file_context}\n</FILE_CONTEXT>"

    logger.debug(f"Full Context Retrieved: {context}")
    
    return {"context": context}

async def generate(state: ChatState, config: RunnableConfig):
    """Generate a response using the LLM and retrieved context."""
    messages = state["messages"]
    context = state.get("context", "")
    
    system_prompt = (
        "Você é um assistente de chat. "
        "Sua tarefa é responder às perguntas do usuário com base EXCLUSIVAMENTE no contexto fornecido.\n\n"
        "Regras para Resposta:\n"
        "1. Use o contexto abaixo para responder.\n"
        "2. Se a resposta não estiver no contexto, diga que não sabe, mas tente ser útil com o que tiver.\n"
        "3. **Citações**: Ao usar uma informação do contexto, cite a fonte. Use o formato: [Fonte: nome_arquivo, pagina].\n"
        "4. Seja claro, objetivo e profissional.\n"
        "5. **Análise de Arquivos**: Se o usuário enviar um arquivo (indicado por <FILE_CONTEXT>) e pedir uma análise geral (ex: 'analise este arquivo'), "
        "faça um resumo dos pontos principais (Objeto, Prazos, Valores, Exigências) e cruze com as regras do TCE presentes no contexto para identificar possíveis inconsistências.\n\n"
        "Contexto Recuperado:\n"
        "{context}"
    )
    
    formatted_system_prompt = system_prompt.format(context=context)
    
    filtered_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
    prompt_messages = [SystemMessage(content=formatted_system_prompt)] + filtered_messages
    
    response = await gpt_4_1_mini.ainvoke(prompt_messages, config=config)
    
    return {"messages": [response]}

# --- Graph Construction ---
workflow = StateGraph(ChatState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile()

# --- Service Class ---
class ChatService:
    def __init__(self):
        self.workflow = app_graph

    async def gerar_resposta(
        self, 
        consulta: str, 
        collection_name: str,
        chat_history: List[BaseMessage] = None,
        file_content: str = None,
        config: RunnableConfig = None,
    ) -> BaseMessage:
        """
        Generates a response for the given query and history.
        """
        # Configurar Langfuse para esta requisição específica
        langfuse_handler = CallbackHandler()
        config = {"callbacks": [langfuse_handler]}
        
        if chat_history is None:
            chat_history = []
            
        current_messages = list(chat_history)
        current_messages.append(HumanMessage(content=consulta))
        
        initial_state = {
            "messages": current_messages, 
            "context": "",
            "file_context": file_content,
            "collection_name": collection_name
        }
        
        final_state = await self.workflow.ainvoke(initial_state, config=config)
        
        return final_state["messages"][-1]

    async def astream_resposta(
        self, 
        consulta: str, 
        collection_name: str,
        chat_history: List[BaseMessage] = None,
        config: RunnableConfig = None,
    ) -> AsyncIterator[BaseMessage]:
        """
        Streams the response.
        """
        # Configurar Langfuse para esta requisição específica
        langfuse_handler = CallbackHandler()
        config = {"callbacks": [langfuse_handler]}
        
        if chat_history is None:
            chat_history = []
        
        current_messages = list(chat_history)
        current_messages.append(HumanMessage(content=consulta))
        
        initial_state = {
            "messages": current_messages, 
            "context": "",
            "collection_name": collection_name
        }

        async for event in self.workflow.astream_events(initial_state, config=config, version="v1"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content

# Singleton instance
chat = ChatService()

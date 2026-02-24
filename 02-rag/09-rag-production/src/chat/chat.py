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

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

# --- State Definition ---
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    file_context: Optional[str]

# --- Tools ---

@tool
async def retrieve_documents(query: str, config: RunnableConfig):
    """Retrieve documents from the database based on the query. Use this tool FIRST for any questions about documents."""
    logger.info(f"Retrieving context for query: {query}")

    # Generate embedding for the query
    query_vector = await embedding.aembed_query(query)
    
    # Extrair collection_name do config (injetado no momento da invocacao)
    collection_name = config.get("configurable", {}).get("collection_name", "unknown")
    
    search_result = await aclient.query_points(
        collection_name=collection_name,
        query=query_vector,
        using="text-dense",
        limit=5
    )
    
    docs_content = []
    points = search_result.points if hasattr(search_result, 'points') else search_result
    
    logger.info(f"Retriever found {len(points)} documents.")
    
    for i, point in enumerate(points):
        payload = point.payload or {}
        text = payload.get("page_content") or payload.get("text") or payload.get("content")
        
        meta = payload.get("metadata", {})
        source = meta.get("nome_arquivo") or "Unknown File"
        page = meta.get("pagina") or ""
        score = point.score if hasattr(point, 'score') else "N/A"
        
        if not text:
            text = str(payload)
            
        formatted_chunk = (
            f"<document index='{i+1}'>\n"
            f"  <source>{source}</source>\n"
            f"  <page>{page}</page>\n"
            f"  <content>{text}</content>\n"
            f"</document>"
        )
        docs_content.append(formatted_chunk)

    return "\n\n".join(docs_content)

# Define tools list
tools = [retrieve_documents]
tool_node = ToolNode(tools)

# Bind tools to the LLM
llm_with_tools = gpt_4_1_mini.bind_tools(tools)

# --- Nodes ---

async def agent(state: ChatState, config: RunnableConfig):
    """Agent node that decides whether to use a tool or answer directly."""
    messages = state["messages"]
    
    system_prompt = (
        "Você é um assistente de chat. "
        "Você tem à disposição a ferramenta 'retrieve_documents' para analisar o acervo da base de conhecimento atual.\n\n"
        "Regras para Resposta:\n"
        "1. Para saudações ou bate-papo inicial (ex: 'Oi', 'Tudo bem?'), responda DIRETAMENTE e sem usar ferramentas.\n"
        "2. Para perguntas sobre leis, editais, arquivos enviados ou contexto de negócios, USE A FERRAMENTA 'retrieve_documents'.\n"
        "3. **Citações**: Ao usar uma informação devolvida pela ferramenta de contexto, cite a fonte. Use o formato: [Fonte: nome_arquivo, pagina].\n"
        "4. Seja claro, objetivo e profissional.\n"
        "5. **Análise de Arquivos**: Se o usuário enviou um arquivo adicional (indicado por <FILE_CONTEXT>), "
        "faça a análise cruzando o conteúdo desse arquivo com as regras consultadas da ferramenta caso solicitado."
    )
    
    file_context = state.get("file_context")
    if file_context:
        system_prompt += f"\n\n<FILE_CONTEXT>\n{file_context}\n</FILE_CONTEXT>"
    
    prompt_messages = [SystemMessage(content=system_prompt)] + messages
    
    response = await llm_with_tools.ainvoke(prompt_messages, config=config)
    
    return {"messages": [response]}

# --- Graph Construction ---
workflow = StateGraph(ChatState)
workflow.add_node("agent", agent)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition,
)
workflow.add_edge("tools", "agent")

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
        
        config["configurable"] = {"collection_name": collection_name}
        
        if chat_history is None:
            chat_history = []
            
        current_messages = list(chat_history)
        current_messages.append(HumanMessage(content=consulta))
        
        initial_state = {
            "messages": current_messages, 
            "file_context": file_content
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
        
        config["configurable"] = {"collection_name": collection_name}
        
        if chat_history is None:
            chat_history = []
        
        current_messages = list(chat_history)
        current_messages.append(HumanMessage(content=consulta))
        
        initial_state = {
            "messages": current_messages
        }

        async for event in self.workflow.astream_events(initial_state, config=config, version="v1"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content

# Singleton instance
chat = ChatService()

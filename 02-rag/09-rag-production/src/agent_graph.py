import time
import json
from typing import TypedDict, Optional, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langfuse.langchain import CallbackHandler
from langfuse import get_client

from src.settings import settings
from src.models import AskResponse, Chunk
from src.prompts import ROUTER_PROMPT, RELEVANCE_PROMPT, ANSWER_PROMPT
from src.qdrant_io import embed_text, search_collection, normalize_results

langfuse = get_client()

langfuse_handler = CallbackHandler()
config = {"callbacks": [langfuse_handler]}

class AgentState(TypedDict):
    user_query: str
    route: Optional[str]
    retrieval: Optional[Dict[str, Any]]
    relevant: bool
    answer: str
    used_collections: List[str]
    warnings: List[str]
    
    fallback_attempts: int
    collection_hint: Optional[str]
    top_k: int
    metadata_filters: Optional[Dict[str, Any]]
    session_id: Optional[str]
    
# --- Tools / Retrievers ---
def _search_collection_tool(collection_name: str, query: str, top_k: int, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    
    vector = embed_text(query)
    
    qdrant_results = search_collection(collection_name, vector, top_k, filters)
    normalized = normalize_results(collection_name, query, qdrant_results)
    
    return normalized

def tool_search_produtos(query: str, top_k: int, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return _search_collection_tool(settings.QDRANT_COLLECTION_PRODUTOS, query, top_k, filters)

def tool_search_suporte(query: str, top_k: int, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return _search_collection_tool(settings.QDRANT_COLLECTION_SUPORTE, query, top_k, filters)

def tool_search_atendimento_especializado(query: str, top_k: int, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return _search_collection_tool(settings.QDRANT_COLLECTION_ATENDIMENTO, query, top_k, filters)

# --- Nodes ---
def router_node(state: AgentState):
    llm = ChatOpenAI(temperature=0, model=settings.OPENAI_MODEL_ROUTER).bind(response_format={"type": "json_object"})
    prompt = ROUTER_PROMPT.format(question=state["user_query"], collection_hint=state.get("collection_hint", ""))
    
    response = llm.invoke([HumanMessage(content=prompt)], config=config)
    content = response.content
    try:
        route_data = json.loads(content)
        route = route_data.get("route", "suporte") # fallback
    except Exception:
        route = "suporte"
    
    if route not in ["produtos", "suporte", "atendimento_especializado"]:
        route = "suporte"
        
    return {"route": route, "used_collections": [route]}

def retrieve_node(state: AgentState):
    route = state.get("route")
    if not route:
        route = "suporte"
        
    query = state["user_query"]
    top_k = state.get("top_k") or settings.TOP_K
    filters = state.get("metadata_filters")
    
    if route == "produtos":
        retrieval = tool_search_produtos(query, top_k, filters)
    elif route == "atendimento_especializado":
        retrieval = tool_search_atendimento_especializado(query, top_k, filters)
    else:
        retrieval = tool_search_suporte(query, top_k, filters)
        
    return {"retrieval": retrieval}

def relevance_node(state: AgentState):
    retrieval = state.get("retrieval", {})
    results = retrieval.get("results", [])
    
    if not results:
        return {"relevant": False}
    
    max_score = max([r.get("score", 0) for r in results])
    if max_score >= settings.SCORE_THRESHOLD:
        return {"relevant": True}
        
    context_text = "\n\n".join([f"Metadata: {r.get('metadata')}\nText: {r.get('text')}" for r in results])
    prompt = RELEVANCE_PROMPT.format(context=context_text, question=state["user_query"])
    llm = ChatOpenAI(temperature=0, model=settings.get_relevance_model).bind(response_format={"type": "json_object"})
    
    response = llm.invoke([HumanMessage(content=prompt)], config=config)
    content = response.content
    try:
        rel_data = json.loads(content)
        relevant = rel_data.get("relevant", False)
    except:
        relevant = False
        
    return {"relevant": relevant}

def fallback_node(state: AgentState):
    attempts = state.get("fallback_attempts", 0)
    warnings_list = state.get("warnings", [])
    used = state.get("used_collections", [])
    
    fallback_order = [c.strip() for c in settings.FALLBACK_ORDER.split(",") if c.strip()]
    
    next_route = None
    for cand in fallback_order:
        if cand not in used:
            next_route = cand
            break
            
    if not next_route or attempts >= 2:
        warnings_list.append("Max fallback attempts reached or no more collections.")
        return {"fallback_attempts": attempts + 1, "warnings": warnings_list}
        
    used.append(next_route)
    warnings_list.append(f"Fallback to collection: {next_route}")
    
    return {
        "route": next_route,
        "used_collections": used,
        "fallback_attempts": attempts + 1,
        "warnings": warnings_list
    }

def answer_node(state: AgentState):   
    retrieval = state.get("retrieval", {})
    results = retrieval.get("results", [])
    
    context_text = "\n\n".join([f"Metadata: {r.get('metadata')}\nText: {r.get('text')}" for r in results])
    prompt = ANSWER_PROMPT.format(context=context_text, question=state["user_query"])
    
    llm = ChatOpenAI(temperature=0, model=settings.OPENAI_MODEL_ANSWER)
    response = llm.invoke([HumanMessage(content=prompt)], config=config)
    
    return {"answer": response.content}

# --- Graph Wiring ---
def route_after_relevance(state: AgentState):
    if state.get("relevant"):
        return "answer"
    attempts = state.get("fallback_attempts", 0)
    if attempts >= 2:
        return "answer"
    
    used = state.get("used_collections", [])
    fallback_order = [c.strip() for c in settings.FALLBACK_ORDER.split(",") if c.strip()]
    if len(used) >= len(fallback_order):
        return "answer"
        
    return "fallback"

workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("relevance", relevance_node)
workflow.add_node("fallback", fallback_node)
workflow.add_node("answer", answer_node)

workflow.add_edge(START, "router")
workflow.add_edge("router", "retrieve")
workflow.add_edge("retrieve", "relevance")
workflow.add_conditional_edges(
    "relevance",
    route_after_relevance,
    {
        "answer": "answer",
        "fallback": "fallback"
    }
)
workflow.add_edge("fallback", "retrieve")
workflow.add_edge("answer", END)

app_graph = workflow.compile()

# --- Main Entry ---
def run_agent(
    user_query: str, 
    session_id: Optional[str] = None, 
    top_k: Optional[int] = None, 
    collection_hint: Optional[str] = None,
    metadata_filters: Optional[Dict[str, Any]] = None
) -> AskResponse:
    
    initial_state = {
        "user_query": user_query,
        "route": None,
        "retrieval": None,
        "relevant": False,
        "answer": "",
        "used_collections": [],
        "warnings": [],
        "fallback_attempts": 0,
        "collection_hint": collection_hint,
        "top_k": top_k or settings.TOP_K,
        "metadata_filters": metadata_filters,
        "session_id": session_id,
    }
    
    final_state = app_graph.invoke(initial_state, config=config)
    
    evidence_dicts = final_state.get("retrieval", {}).get("results", [])
    evidence_objs = [Chunk(**chunk_dict) for chunk_dict in evidence_dicts]
    
    confidence = 0.0
    if evidence_dicts:
        confidence = max([e.get("score", 0.0) for e in evidence_dicts])
    
    return AskResponse(
        answer=final_state.get("answer", ""),
        route=final_state.get("route", "unknown"),
        used_collections=final_state.get("used_collections", []),
        confidence=float(confidence),
        evidence=evidence_objs,
        warnings=final_state.get("warnings", [])
    )

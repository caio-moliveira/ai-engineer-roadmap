import asyncio
import os
import sys
from typing import TypedDict, Literal

from aula01_simple_tool import calculate_budget
from aula02_api_tool import get_weather, get_tourist_info

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from langchain_mcp_adapters.client import MultiServerMCPClient

class TravelState(TypedDict):
    destination: str
    origin: str
    days: int
    date_start: str
    date_end: str
    profile: str
    
    budget: str
    weather: str
    tourist: str
    policy: str
    
    draft_info: str
    final_itinerary: str
    approved: bool

async def main():
    print("Iniciando o Exemplo 07 (Final): Fluxo Completo LangGraph + MCP + HITL\n")
    
    server_script = os.path.join(os.path.dirname(__file__), "03_mcp_server.py")
    
    print("Iniciando Conexão com MCP Server...")
    # Em versões mais recentes do adaptador (0.1.0+), o cliente não deve ser usado como async context manager
    client = MultiServerMCPClient(
        {
            "Travel_MCP": {
                "transport": "stdio",   
                "command": "python",
                "args": [server_script]
            }
        }
    )
        
    # =========================================================================
    # NODE 1: Usa as tools locais (01_simple_tool e 02_api_tool)
    # =========================================================================
    async def node_gather_local(state: TravelState):
        print("-> [Nó 1] Calculando Orçamento (Tool Simples)...")
        budget = await calculate_budget.ainvoke({
            "days": state["days"], "origin": state["origin"], 
            "destination": state["destination"], 
            "date_start": state["date_start"], "date_end": state["date_end"]
        })
        
        print("-> [Nó 1] Consultando APIs de Clima e Turismo (Tool de API)...")
        weather = await get_weather.ainvoke({"city": state["destination"]})
        tourist = await get_tourist_info.ainvoke({"city": state["destination"]})
        
        return {"budget": budget, "weather": weather, "tourist": tourist}
        
    # =========================================================================
    # NODE 2: Usa o Resource MCP (05_mcp_as_resource) para trazer as diretrizes
    # =========================================================================
    async def node_mcp_resource(state: TravelState):
        print("-> [Nó 2] Lendo Política de Viagens via MCP Resource...")
        blobs = await client.get_resources("Travel_MCP", uris=["travel://info/international"])
        policy_text = blobs[0].as_string()
        return {"policy": policy_text}
        
    # =========================================================================
    # NODE 3: Usa MCP Prompt (06_mcp_as_prompt) e junta tudo com LLM
    # =========================================================================
    async def node_build_draft(state: TravelState):
        print("-> [Nó 3] Estruturando rascunho com LLM usando nosso MCP Prompt Oficial...")
        
        p_result = await client.get_prompt(
            "Travel_MCP", 
            prompt_name="itinerary_planner", 
            arguments={"destination": state["destination"], "days": str(state["days"]), "profile": state["profile"]}
        )
        
        # Aqui, p_result já é uma lista preenchida (ex: [SystemMessage]).
        contexto = f"Orçamento: {state['budget']}\nClima: {state['weather']}\nTurismo: {state['tourist']}\nPolítica/Segurança: {state['policy']}"
        p_result.append(HumanMessage(content=f"Crie um roteiro descritivo integrando os dados colhidos do contexto:\n{contexto}"))
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        res = await llm.ainvoke(p_result)
        return {"draft_info": res.content}
        
    # =========================================================================
    # NODE 4: Usa MCP Tool (04_mcp_as_tool) para bater no sistema e finalizar roteiro
    # =========================================================================
    async def node_mcp_tool(state: TravelState):
        print("-> [Nó 4] Formatando e Validando a string através da Tool oficial do MCP Server...")
        tools = await client.get_tools()
        create_itin_tool = next(t for t in tools if t.name == "create_itinerary")
        
        result_tool = await create_itin_tool.ainvoke({"raw_info": state["draft_info"]})
        return {"final_itinerary": str(result_tool)}
        
    # =========================================================================
    # NODE 5: HITL Interrupt para Aprovação Humana
    # =========================================================================
    def node_human_approval(state: TravelState):
        print("\n\n=================== ROTEIRO FINAL (PENDENTE) ==================")
        print(state["final_itinerary"].strip())
        print("=================================================================\n")
        
        # Isso suspende a execução e salva o nó na memória.
        decision = interrupt("O Humano precisa aprovar este roteiro para salvá-lo.")
        
        print(f"\n[Aprovação Final da Diretoria]: Resposta recebida -> '{decision}'")
        is_approved = str(decision).lower() in ['y', 'yes', 'sim']
        return {"approved": is_approved}
        
    def route_approval(state: TravelState) -> str:
        if state.get("approved"):
            return "node_save_file"
        print("-> [Fluxo Encerrado] O usuário optou por não salvar o arquivo Markdown.")
        return "__end__"
        
    # =========================================================================
    # NODE 6: Salva Markdown
    # =========================================================================
    def node_save_file(state: TravelState):
        file_name = "roteiro_aprovado.md"
        print(f"-> [Nó 6] Aprovado! Gravando roteiro oficial no disco local corporativo ({file_name})...")
        with open(file_name, "w", encoding="utf-8") as f:
             f.write(state["final_itinerary"])
        return {}

    # -------------------------------------------------------------------------
    # CONSTRUÇÃO DO GRAFO (PIPELINE)
    # -------------------------------------------------------------------------
    workflow = StateGraph(TravelState)
    workflow.add_node("node_gather_local", node_gather_local)
    workflow.add_node("node_mcp_resource", node_mcp_resource)
    workflow.add_node("node_build_draft", node_build_draft)
    workflow.add_node("node_mcp_tool", node_mcp_tool)
    workflow.add_node("node_human_approval", node_human_approval)
    workflow.add_node("node_save_file", node_save_file)
    
    workflow.add_edge(START, "node_gather_local")
    workflow.add_edge("node_gather_local", "node_mcp_resource")
    workflow.add_edge("node_mcp_resource", "node_build_draft")
    workflow.add_edge("node_build_draft", "node_mcp_tool")
    workflow.add_edge("node_mcp_tool", "node_human_approval")
    workflow.add_conditional_edges("node_human_approval", route_approval)
    workflow.add_edge("node_save_file", END)
    
    # Um Checkpointer é OBRIGATÓRIO para usar .interrupt()
    app = workflow.compile(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "viagem_paris_final"}}
    
    # -------------------------------------------------------------------------
    # ESTADO INICIAL
    # -------------------------------------------------------------------------
    initial_state = {
        "origin": "São Paulo",
        "destination": "Paris",
        "days": 7,
        "date_start": "10-05-2024",
        "date_end": "17-05-2024",
        "profile": "Casal jovem focado em cultura e boa gastronomia"
    }
    
    print("\nDisparando Agente e alimentando o Data Pipeline...\n")
    
    # Loop do CLI pra dar a sensação interativa e fluida de resume:
    while True:
        state_snapshot = app.get_state(config)
        
        if state_snapshot.tasks and state_snapshot.tasks[0].interrupts:
            # O LangGraph pausou. Solicitamos input real no console de quem tá usando.
            ans = input("\n>> O Gerente aprova o Roteiro para gravação em Markdown? (y/N): ")
            
            # Retomamos o node `node_human_approval` passando `ans` no lugar do interrupt()
            async for event in app.astream(Command(resume=ans), config=config):
                pass
            break
        elif not state_snapshot.values:
            # Primeira Rodada Iniciando do Zero
            async for event in app.astream(initial_state, config=config):
                pass
        else:
            # Se não estiver zerado e nem com tarefas pendentes (já resumiu e acabou)
            break
            
    print("\nPipeline Inteiro Exitosamente Concluído!")

if __name__ == "__main__":
    asyncio.run(main())

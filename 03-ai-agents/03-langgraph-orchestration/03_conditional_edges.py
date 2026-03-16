import operator
from typing import Annotated, List, Literal, TypedDict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# 1. Esquema para o Roteamento Inteligente
class RoutingAnalysis(BaseModel):
    """Análise para decidir o roteamento do feedback."""
    categoria: str = Field(description="'Bug', 'Elogio' ou 'Outro'")
    sentimento: str = Field(description="'Positivo' ou 'Negativo'")
    justificativa: str = Field(description="Breve explicação da decisão")

# 2. Definindo o Estado (State)
class State(TypedDict):
    cliente_nome: str
    feedback: str
    decisao: Optional[RoutingAnalysis]
    equipe_atendimento: Optional[str]
    resposta_final: Optional[str]
    historico: Annotated[List[str], operator.add]

# 3. LLM Config
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 4. Nós do Grafo

def node_analise_roteamento(state: State) -> dict:
    print(f"\n[ANALISE] Classificando feedback de {state['cliente_nome']}...")
    
    structured_llm = llm.with_structured_output(RoutingAnalysis)
    analise = structured_llm.invoke(f"Analise o feedback para roteamento: {state['feedback']}")
    
    print(f" -> Categoria: {analise.categoria}")
    print(f" -> Sentimento: {analise.sentimento}")
    
    return {
        "decisao": analise,
        "historico": [f"Feedback classificado como {analise.categoria} ({analise.sentimento})"]
    }

def node_especialista_tech(state: State) -> dict:
    print("\n[ROTA] Encaminhado para Especialista Técnico")
    return {
        "equipe_atendimento": "Engenharia / QA",
        "resposta_final": "Obrigado por reportar. Nossa equipe técnica já está investigando o problema.",
        "historico": ["Tratado pela equipe de Engenharia"]
    }

def node_marketing(state: State) -> dict:
    print("\n[ROTA] Encaminhado para Marketing (Sucesso do Cliente)")
    return {
        "equipe_atendimento": "Marketing / Customer Success",
        "resposta_final": "Ficamos muito felizes com seu feedback! Vamos compartilhar com todo o time.",
        "historico": ["Tratado pela equipe de Marketing"]
    }

def node_suporte_geral(state: State) -> dict:
    print("\n[ROTA] Encaminhado para Suporte Geral")
    return {
        "equipe_atendimento": "Atendimento Nível 1",
        "resposta_final": "Olá! Recebemos sua mensagem e um atendente entrará em contato em breve.",
        "historico": ["Tratado pelo Suporte Geral"]
    }

# 5. Função de Roteamento (Conditional Edge)
def router(state: State) -> Literal["especialista", "marketing", "suporte"]:
    decisao = state["decisao"]
    
    if decisao.categoria == "Bug":
        return "especialista"
    elif decisao.sentimento == "Positivo":
        return "marketing"
    else:
        return "suporte"

# 6. Montagem do Grafo
builder = StateGraph(State)

builder.add_node("analisar", node_analise_roteamento)
builder.add_node("especialista", node_especialista_tech)
builder.add_node("marketing", node_marketing)
builder.add_node("suporte", node_suporte_geral)

builder.add_edge(START, "analisar")

# Adicionando a ARESTA CONDICIONAL
# Parta de 'analisar', use a função 'router', e mapeie os retornos para os nós
builder.add_conditional_edges(
    "analisar",
    router,
    {
        "especialista": "especialista",
        "marketing": "marketing",
        "suporte": "suporte"
    }
)

builder.add_edge("especialista", END)
builder.add_edge("marketing", END)
builder.add_edge("suporte", END)

graph = builder.compile()

# 7. Execução Interativa para Testar os Caminhos
if __name__ == "__main__":
    testes = [
        {"nome": "Alice", "msg": "Encontrei um erro crítico na tela de pagamentos, o botão não clica."},
        {"nome": "Bruno", "msg": "Adorei a nova interface, ficou muito mais rápida! Parabéns."},
        {"nome": "Carla", "msg": "Como faço para trocar minha senha?"},
    ]
    
    for i, t in enumerate(testes, 1):
        print("\n" + "="*60)
        print(f"TESTE #{i}: {t['nome']}")
        print(f"Mensagem: {t['msg']}")
        print("="*60)
        
        entrada = {
            "cliente_nome": t["nome"],
            "feedback": t["msg"],
            "historico": []
        }
        
        resultado = graph.invoke(entrada)
        
        print(f"\nDESTINO: {resultado['equipe_atendimento']}")
        print(f"RESPOSTA: {resultado['resposta_final']}")
        print(f"HISTÓRICO: {' -> '.join(resultado['historico'])}")

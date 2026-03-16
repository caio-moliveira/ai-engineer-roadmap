import operator
from typing import Annotated, List, TypedDict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv

# Carregar variáveis de ambiente (API Key)
load_dotenv()

# 1. Esquemas para cada análise paralela
class SentimentAnalysis(BaseModel):
    sentimento: str = Field(description="'Positivo', 'Negativo' ou 'Neutro'")

class Categorization(BaseModel):
    categoria: str = Field(description="'Bug', 'Financeiro', 'Sugestão' ou 'Suporte'")

class UrgencyAnalysis(BaseModel):
    urgencia: str = Field(description="'Baixa', 'Média' ou 'Alta'")

# 2. Definindo o Estado (State)
class State(TypedDict):
    cliente_nome: str
    feedback: str
    
    # Resultados individuais dos nós paralelos
    res_sentimento: Optional[str]
    res_categoria: Optional[str]
    res_urgencia: Optional[str]
    
    # Campo final concatenado
    analise_final: Optional[str]
    
    # Histórico acumulado para mostrar o paralelismo em ação
    historico: Annotated[List[str], operator.add]

# 3. LLM Config
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 4. Nós do Grafo

def node_sanitizacao(state: State) -> dict:
    print(f"\n[START] Iniciando pipeline para: {state['cliente_nome']}")
    return {"historico": [f"Iniciou no nó: Sanitização"]}

def node_sentimento(state: State) -> dict:
    print(" -> [Nó Paralelo]: Analisando Sentimento...")
    structured_llm = llm.with_structured_output(SentimentAnalysis)
    res = structured_llm.invoke(f"Qual o sentimento deste feedback: {state['feedback']}")
    return {
        "res_sentimento": res.sentimento,
        "historico": [f"Finalizou nó: Sentimento ({res.sentimento})"]
    }

def node_categorizacao(state: State) -> dict:
    print(" -> [Nó Paralelo]: Categorizando Feedback...")
    structured_llm = llm.with_structured_output(Categorization)
    res = structured_llm.invoke(f"Categorize este feedback: {state['feedback']}")
    return {
        "res_categoria": res.categoria,
        "historico": [f"Finalizou nó: Categoria ({res.categoria})"]
    }

def node_urgencia(state: State) -> dict:
    print(" -> [Nó Paralelo]: Analisando Urgência...")
    structured_llm = llm.with_structured_output(UrgencyAnalysis)
    res = structured_llm.invoke(f"Qual a urgência para este caso: {state['feedback']}")
    return {
        "res_urgencia": res.urgencia,
        "historico": [f"Finalizou nó: Urgência ({res.urgencia})"]
    }

def node_agregador(state: State) -> dict:
    """Nó de Fan-in: Só executa após TODOS os anteriores terminarem."""
    print("\n[JOIN] Agregador consolidando resultados paralelos...")
    
    resumo = (
        f"Análise Consolidada:\n"
        f"- Sentimento: {state['res_sentimento']}\n"
        f"- Categoria: {state['res_categoria']}\n"
        f"- Urgência: {state['res_urgencia']}"
    )
    
    return {
        "analise_final": resumo,
        "historico": ["Finalizou no nó: Agregador"]
    }

# 5. Montagem do Grafo
builder = StateGraph(State)

builder.add_node("sanitizar", node_sanitizacao)
builder.add_node("sentimento", node_sentimento)
builder.add_node("categoria", node_categorizacao)
builder.add_node("urgencia", node_urgencia)
builder.add_node("agregador", node_agregador)

# Fluxo
builder.add_edge(START, "sanitizar")

# FAN-OUT: Sanitização abre para 3 nós em paralelo
builder.add_edge("sanitizar", "sentimento")
builder.add_edge("sanitizar", "categoria")
builder.add_edge("sanitizar", "urgencia")

# FAN-IN: Os 3 nós se encontram no agregador
builder.add_edge("sentimento", "agregador")
builder.add_edge("categoria", "agregador")
builder.add_edge("urgencia", "agregador")

builder.add_edge("agregador", END)

graph = builder.compile()

# 6. Execução
if __name__ == "__main__":
    import json
    
    entrada = {
        "cliente_nome": "João Silva",
        "feedback": "Paguei o boleto há 4 dias e ainda não liberaram meu acesso. Preciso disso agora!",
        "historico": []
    }
    
    print("="*60)
    print("EXECUÇÃO PARALELA (FAN-OUT/FAN-IN)")
    print("="*60)
    
    resultado = graph.invoke(entrada)
    
    print("\n" + "="*60)
    print("ESTADO FINAL CONSOLIDADO")
    print("="*60)
    # Exibir apenas os campos principais para facilitar a leitura
    print(f"RESUMO FINAL:\n{resultado['analise_final']}")
    
    print("\nORDEM DE CONCLUSÃO (HISTÓRICO):")
    for i, passo in enumerate(resultado['historico'], 1):
        print(f"{i}. {passo}")

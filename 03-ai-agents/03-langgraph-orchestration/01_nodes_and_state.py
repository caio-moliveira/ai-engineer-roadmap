import operator
import json
from typing import Annotated, List, TypedDict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv

load_dotenv()

# 1. Definindo o Esquema de Saída Estruturada com Pydantic
class FeedbackAnalysis(BaseModel):
    """Esquema para a análise de sentimento e urgência do feedback."""
    sentimento: str = Field(description="O sentimento do feedback: 'Positivo', 'Negativo' ou 'Neutro'")
    urgencia: str = Field(description="A urgência de resposta: 'Baixa', 'Média' ou 'Alta'")
    resumo: str = Field(description="Um resumo de uma frase sobre o problema ou elogio")

# 2. Definindo o Estado (State)
class State(TypedDict):
    cliente_nome: str
    feedback_bruto: str
    feedback_limpo: Optional[str]
    analise: Optional[FeedbackAnalysis]
    historico: Annotated[List[str], operator.add]

# 3. Configuração do LLM
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
model_with_structure = llm.with_structured_output(FeedbackAnalysis)

# 4. Criando os Nós

def node_sanitizacao(state: State) -> dict:
    """Limpa o texto do feedback."""
    print("\n[Passo 1]: Sanitização")
    texto_limpo = state["feedback_bruto"].strip()
    return {
        "feedback_limpo": texto_limpo,
        "historico": ["Texto sanitizado."]
    }

def node_analise_llm(state: State) -> dict:
    """Usa o LLM para analisar o feedback de forma inteligente."""
    print("\n[Passo 2]: Análise com LLM")
    
    prompt = f"""Analise o seguinte feedback de um cliente e extraia o sentimento, a urgência e um resumo:
    
    Cliente: {state['cliente_nome']}
    Feedback: {state['feedback_limpo']}
    """
    
    # Chamada ao LLM com output estruturado
    analise_resultado = model_with_structure.invoke(prompt)
    
    print(f" -> Sentimento: {analise_resultado.sentimento}")
    print(f" -> Urgência: {analise_resultado.urgencia}")
    print(f" -> Resumo: {analise_resultado.resumo}")
    
    return {
        "analise": analise_resultado,
        "historico": [f"Análise LLM concluída conforme o modelo Pydantic."]
    }

def node_conclusao(state: State) -> dict:
    """Apenas registra a finalização do processo."""
    print("\n[Passo 3]: Finalização")
    return {
        "historico": ["Workflow finalizado com sucesso."]
    }

# 5. Construindo o Grafo
builder = StateGraph(State)

builder.add_node("sanitizar", node_sanitizacao)
builder.add_node("analisar_llm", node_analise_llm)
builder.add_node("concluir", node_conclusao)

builder.add_edge(START, "sanitizar")
builder.add_edge("sanitizar", "analisar_llm")
builder.add_edge("analisar_llm", "concluir")
builder.add_edge("concluir", END)

graph = builder.compile()

# 6. Execução
if __name__ == "__main__":
    print("-" * 50)
    print("PIPELINE DE FEEDBACK COM LLM & LANGGRAPH")
    print("-" * 50)
    
    entrada = {
        "cliente_nome": "Maria Silva",
        "feedback_bruto": "Nossa, parabéns pelo serviço. O sistema caiu 3 vezes hoje e perdi todo meu trabalho. Simplesmente incrível.",
        "historico": []
    }
    
    resultado = graph.invoke(entrada)
    
    print("\n" + "="*50)
    print("ESTADO FINAL")
    print("="*50)
    
    resultado["analise"] = resultado["analise"].model_dump() if resultado["analise"] else None
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

import operator
from typing import Annotated, List, Literal, TypedDict, Optional
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

# 1. Definindo o Estado da Transação
class State(TypedDict):
    cliente: str
    valor: float
    status: str
    logs: Annotated[List[str], operator.add]

# 2. Nó de Verificação Inicial
def verificar_transferencia(state: State) -> Command[Literal["processar_direto", "aguardar_aprovacao"]]:
    valor = state["valor"]
    cliente = state["cliente"]
    
    print(f"\n[SISTEMA] Verificando transferência de R$ {valor:.2f} para {cliente}...")
    
    # Regra de Negócio: Acima de R$ 5.000,00 exige aprovação humana
    if valor > 5000:
        print("[ALERTA] Valor alto detectado! Encaminhando para revisão do gerente.")
        return Command(
            update={"logs": [f"Transferência de {valor} para {cliente} aguardando aprovação."]},
            goto="aguardar_aprovacao"
        )
    else:
        print("[OK] Valor dentro dos limites. Processando automaticamente.")
        return Command(
            update={"logs": [f"Transferência de {valor} para {cliente} processada automaticamente."]},
            goto="processar_direto"
        )

# 3. Nó de Aguardar Aprovação (Onde ocorre o HITL)
def aguardar_aprovacao(state: State):

    decisao = interrupt(
        f"SOLICITAÇÃO DE APROVAÇÃO: Transferência de R$ {state['valor']:.2f} para {state['cliente']}."
    )
    
    # Após o 'resume', a execução continua aqui
    if decisao.lower() == "aprovar":
        print("\n[GERENTE] Transferência APROVADA!")
        return {
            "status": "Aprovado",
            "logs": ["Gerente aprovou a transação."]
        }
    else:
        print("\n[GERENTE] Transferência REJEITADA!")
        return {
            "status": "Rejeitado",
            "logs": ["Gerente rejeitou a transação."]
        }

# 4. Nó de Processamento Direto
def processar_direto(state: State):
    return {
        "status": "Finalizado Automaticamente",
        "logs": ["Transação concluída sem necessidade de aprovação."]
    }

# 5. Construindo o Grafo
builder = StateGraph(State)
builder.add_node("verificar", verificar_transferencia)
builder.add_node("aguardar_aprovacao", aguardar_aprovacao)
builder.add_node("processar_direto", processar_direto)

builder.add_edge(START, "verificar")
builder.add_edge("processar_direto", END)
builder.add_edge("aguardar_aprovacao", END)

# Checkpointer é essencial para manter o estado durante a pausa do HITL
memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)

# 6. Execução Interativa no Terminal
if __name__ == "__main__":
    print("="*60)
    print("        SISTEMA BANCÁRIO (HUMAN-IN-THE-LOOP)")
    print("="*60)
    
    nome = input("Nome do Cliente: ")
    quantia = float(input("Valor da Transferência (R$): "))
    
    # Thread ID isola cada transação
    config = {"configurable": {"thread_id": "transfer-123"}}
    
    # Iniciando a execução
    resultado = graph.invoke(
        {"cliente": nome, "valor": quantia, "status": "pendente", "logs": []}, 
        config
    )
    
    # Loop de HITL: Verifica se há interrupções pendentes
    while "__interrupt__" in resultado:
        interrupcao = resultado["__interrupt__"][-1]
        print(f"\n>>> [PAUSA DO SISTEMA] <<<")
        print(f"Mensagem: {interrupcao.value}")
        
        # Simulação da ação do Gerente
        acao = input("\nGerente, tome uma decisão (aprovar/rejeitar): ")
        
        # Retomando o grafo de onde parou usando Command(resume)
        resultado = graph.invoke(Command(resume=acao), config)

    # Resultado Final
    print("\n" + "="*60)
    print("        STATUS FINAL DA TRANSAÇÃO")
    print("="*60)
    print(f"Cliente: {resultado['cliente']}")
    print(f"Valor: R$ {resultado['valor']:.2f}")
    print(f"Status: {resultado['status']}")
    print("\nHistórico de Logs:")
    for log in resultado["logs"]:
        print(f" - {log}")
    print("="*60)

from typing import Union, Literal
from pydantic import BaseModel, Field

# --- Cenário: O LLM pode retornar diferentes ações ---
# Usamos `Literal["nome_da_acao"]` como discriminador.

class CreateTicket(BaseModel):
    kind: Literal["create_ticket"]
    title: str = Field(..., min_length=3)
    priority: int = Field(..., ge=1, le=5)

class AskFollowup(BaseModel):
    kind: Literal["ask_followup"]
    question: str = Field(..., min_length=5)

class FinalAnswer(BaseModel):
    kind: Literal["final_answer"]
    answer: str

# Union discriminada: Pydantic decide qual classe usar baseada no campo 'kind'
# Isso é CRUCIAL para agentes que podem tomar diferentes rumos.
LLMAction = Union[CreateTicket, AskFollowup, FinalAnswer]

# --- Exemplo de Uso ---

def process_action(data: dict):
    try:
        # Pydantic verifica o campo 'kind' e valida com a classe correta
        action = LLMAction.model_validate(data)
        
        print(f"\n--- Ação Identificada: {type(action).__name__} ---")
        if isinstance(action, CreateTicket):
            print(f"Criando ticket '{action.title}' com prioridade {action.priority}")
        elif isinstance(action, AskFollowup):
            print(f"Pergunta ao usuário: {action.question}")
        elif isinstance(action, FinalAnswer):
            print(f"Resposta final: {action.answer}")
            
    except Exception as e:
        print(f"\nErro de validação:\n{e}")

if __name__ == "__main__":
    # Caso 1: Criar Ticket
    process_action({
        "kind": "create_ticket", 
        "title": "Erro no Login", 
        "priority": 5
    })

    # Caso 2: Pergunta
    process_action({
        "kind": "ask_followup", 
        "question": "Pode fornecer o ID do usuário?"
    })

    # Caso 3: Erro (falta campo obrigatório do modelo específico)
    process_action({
        "kind": "create_ticket",
        "title": "Erro sem prioridade" # Falta priority
    })

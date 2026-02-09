import json
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

# --- 1. Definindo o Schema Final (Contrato) ---

class ActionItem(BaseModel):
    description: str = Field(..., min_length=5)
    owner: Optional[str] = None

class MeetingExtract(BaseModel):
    topic: str = Field(..., min_length=3)
    participants: List[str] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)

# --- 2. Simulação de LLM (Mock) ---

def mock_llm_call(prompt: str) -> str:
    """
    Simula um LLM.
    Na primeira chamada (sem feedback de erro), retorna JSON inválido.
    Na segunda chamada (com feedback), retorna JSON corrigido.
    """
    if "CORRIJA OS SEGUINTES ERROS" in prompt:
        print(">> [LLM] Recebi feedback de erro. Corrigindo JSON...")
        return json.dumps({
            "topic": "Reunião de Daily",
            "participants": ["Alice", "Bob"],
            "action_items": [
                {"description": "Corrigir bug na API", "owner": "Bob"}
            ]
        })
    else:
        print(">> [LLM] Gerando primeira versão (com defeito)...")
        # Retorna JSON faltando campos obrigatórios e com tipo errado
        return json.dumps({
            "topic": "", # Erro: min_length=3
            "participants": "Alice, Bob", # Erro: deveria ser list, não str
            # Falta action_items (mas é default_factory list então ok? Não, se o LLM alucinar)
        })

# --- 3. Função de Validação e Retry (O Core do Pipeline) ---

def format_validation_errors(errors: list[dict]) -> str:
    return "; ".join([f"{'.'.join(str(x) for x in e['loc'])}: {e['msg']}" for e in errors])

def extract_with_retry(text_input: str, max_retries: int = 2) -> MeetingExtract:
    schema = MeetingExtract.model_json_schema()
    
    base_prompt = f"""
    Extraia informações da reunião. Retorne JSON.
    Schema: {json.dumps(schema, indent=2)}
    Texto: {text_input}
    """
    
    current_prompt = base_prompt
    last_error = None

    for attempt in range(max_retries + 1):
        print(f"\n--- Tentativa {attempt + 1} ---")
        
        # Chama LLM
        response_text = mock_llm_call(current_prompt)
        print(f"Resposta LLM: {response_text}")
        
        try:
            # Valida
            obj = MeetingExtract.model_validate_json(response_text)
            print(">> Validação: SUCESSO! ✅")
            return obj
        except ValidationError as e:
            print(f">> Validação: FALHA ❌ ({len(e.errors())} erros)")
            last_error = e
            feedback = format_validation_errors(e.errors())
            
            # Atualiza prompt com feedback
            current_prompt = f"{base_prompt}\n\nCORRIJA OS SEGUINTES ERROS:\n{feedback}\nRetorne JSON válido."

    raise last_error

# --- Exemplo de Uso ---

if __name__ == "__main__":
    text = "Alice e Bob discutiram o bug da API na daily. Bob ficou de arrumar."
    
    try:
        result = extract_with_retry(text)
        print("\n--- Resultado Final Confiável ---")
        print(result.model_dump_json(indent=2))
    except ValidationError:
        print("\n--- Falha Total após retries ---")

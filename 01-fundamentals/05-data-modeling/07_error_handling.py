from pydantic import BaseModel, Field, ValidationError

class UserProfile(BaseModel):
    name: str = Field(..., min_length=1)
    email: str # Validadores simples de string se não usar EmailStr
    age: int = Field(..., ge=0, le=120)

def format_validation_errors(errors: list[dict]) -> str:
    """
    Transforma erros do Pydantic em texto legível para re-inserir no prompt do LLM.
    Exemplo de output: "- Campo 'age': Input should be a valid integer"
    """
    lines = []
    for err in errors:
        # 'loc' é o caminho do campo (ex: ('body', 'users', 0, 'age'))
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "")
        lines.append(f"- Campo '{loc}': {msg}")
    return "\n".join(lines)

# --- Exemplo de Uso ---

if __name__ == "__main__":
    print("--- Tentativa com Dados Inválidos ---")
    
    # Dados com múltiplos problemas: email ausente, age string inválida, name vazio
    bad_data = {
        "name": "", 
        "age": "noventa"
    }

    try:
        UserProfile.model_validate(bad_data)
    except ValidationError as e:
        print("\n1. Erro Bruto (Pydantic):")
        print(e)

        print("\n2. Erros Estruturados (e.errors()):")
        # Lista de dicts com detalhes do erro
        print(e.errors())

        print("\n3. Feedback Formatado para LLM:")
        # Isso aqui é o que você mandaria de volta pro ChatGPT/Claude
        feedback = format_validation_errors(e.errors())
        print(feedback)
        
        # Exemplo de como usar no prompt de retry:
        retry_prompt = f"""
        O JSON anterior gerou erros. Corrija-os com base neste feedback:
        {feedback}
        
        Retorne o JSON corrigido.
        """
        print("\n--- Prompt de Retry ---")
        print(retry_prompt)

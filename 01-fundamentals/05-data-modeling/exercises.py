from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ValidationError

# ==========================================
# EXERCÍCIO A: Extração de Edital
# ==========================================
# Objetivo: Criar um modelo para extrair dados chave de um edital.
# 1. `orgao`: string, min 3 caracteres
# 2. `cargos`: lista de strings, min 1 item
# 3. `tem_cronograma`: bool
# 4. `paginas_referenciadas`: lista de int, números devem ser >= 1

class EditalExtract(BaseModel):
    # TODO: Implemente os campos aqui
    pass

def test_exercicio_a():
    print("--- Teste Exercício A ---")
    # Caso válido
    data = {
        "orgao": "Prefeitura XPTO",
        "cargos": ["Analista", "Técnico"],
        "tem_cronograma": True,
        "paginas_referenciadas": [10, 15]
    }
    try:
        # edital = EditalExtract.model_validate(data)
        # print(f"Sucesso: {edital}")
        print("TODO: Descomente as linhas acima após implementar")
    except ValidationError as e:
        print(e)

# ==========================================
# EXERCÍCIO B: Union Discriminada
# ==========================================
# Objetivo: Modelar uma resposta de agente que pode ser:
# - Pedir info ao usuário (`kind="ask_user"`)
# - Extrair campos (`kind="extract_fields"`)
# - Resposta final (`kind="final_answer"`)

class AskUser(BaseModel):
    kind: Literal["ask_user"]
    question: str

class ExtractFields(BaseModel):
    # TODO: kind="extract_fields" e fields: List[str]
    pass

class FinalAnswer(BaseModel):
    # TODO: kind="final_answer" e answer: str
    pass

# TODO: Crie a Union
# AgentAction = ...

def test_exercicio_b():
    print("\n--- Teste Exercício B ---")
    data_ask = {"kind": "ask_user", "question": "Qual seu nome?"}
    
    # try:
    #     action = AgentAction.model_validate(data_ask)
    #     print(f"Ação identificada: {type(action)}")
    # except Exception as e:
    #     print(e)
    print("TODO: Descomente as linhas acima após implementar")

if __name__ == "__main__":
    test_exercicio_a()
    test_exercicio_b()

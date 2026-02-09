from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    name: str
    email: str
    age: int
    role: str = "user"

# --- Dados brutos (simulando saída de um LLM ou API) ---
raw_data = {
    "name": "  alice  ",   # Espaços extras
    "email": "[email protected]",
    "age": "29",           # String numérica (Pydantic coage para int)
    "role": "admin"
}

# --- 1. model_validate: De Dict para Objeto ---
print("--- 1. model_validate (Dict -> Obj) ---")
user = UserProfile.model_validate(raw_data)
# Note que o Pydantic faz coerção de tipos (age "29" -> 29)
print(f"Objeto: {user}")
print(f"Tipo do age: {type(user.age)}") 


# --- 2. model_validate_json: De String JSON para Objeto ---
# Essencial para lidar com output de LLMs que retornam strings
print("\n--- 2. model_validate_json (JSON Str -> Obj) ---")
json_str = '{"name": "Bob", "email": "[email protected]", "age": 40}'
user_from_json = UserProfile.model_validate_json(json_str)
print(f"Objeto do JSON: {user_from_json}")


# --- 3. model_dump: De Objeto para Dict ---
print("\n--- 3. model_dump (Obj -> Dict) ---")
user_dict = user.model_dump()
print(f"Dict: {user_dict}")
# Dica: use exclude_unset=True para ignorar campos que não foram definidos explicitamente
# ou exclude_none=True para ignorar Nones.


# --- 4. model_dump_json: De Objeto para String JSON ---
print("\n--- 4. model_dump_json (Obj -> JSON Str) ---")
user_json = user.model_dump_json(indent=2)
print(f"JSON String:\n{user_json}")

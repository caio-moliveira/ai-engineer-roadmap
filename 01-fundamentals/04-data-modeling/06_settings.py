import os
from pydantic import Field
from pydantic_settings import BaseSettings

# --- Simulando variáveis de ambiente (para o exemplo rodar) ---
os.environ["OPENAI_API_KEY"] = "sk-proj-123456789"
os.environ["MODEL_NAME"] = "gpt-4-turbo"
# Note que definimos TEMPERATURE como string no env, mas Pydantic converte para float
os.environ["TEMPERATURE"] = "0.7" 

class Settings(BaseSettings):
    # Lê de OPENAI_API_KEY
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    
    # Lê de MODEL_NAME, com default
    model_name: str = Field(default="gpt-3.5-turbo", alias="MODEL_NAME")
    
    # Lê de TEMPERATURE, converte e valida
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, alias="TEMPERATURE")
    
    # Configurações extras
    class Config:
        # Define arquivo .env para carregar (se existir)
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Ignora variáveis extras no .env que não estão no modelo
        extra = "ignore" 

# --- Exemplo de Uso ---

if __name__ == "__main__":
    try:
        settings = Settings()
        
        print("--- Configurações Carregadas ---")
        # Mascarando a chave para exibição
        masked_key = f"{settings.openai_api_key[:5]}...{settings.openai_api_key[-4:]}"
        print(f"API Key: {masked_key}")
        print(f"Model: {settings.model_name}")
        print(f"Temperature: {settings.temperature}")
        
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")

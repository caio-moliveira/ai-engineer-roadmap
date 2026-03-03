import os
import shutil
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Importando do DeepAgents (pip install deepagents)
try:
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
except ImportError:
    create_deep_agent = None

load_dotenv()

# ==========================================
# 1. A Magia das Skills (Progressive Disclosure Nativo)
# ==========================================
# Lembra de termos construído uma Tool Dinâmica via "SKILLS_REGISTRY" no Módulo anterior?
# Esqueça aquele código solto. O pacote DeepAgents já possui isso no CORE da API!
# Um Agente "Deep" varre qualquer diretório no formato /skills/<nome>/SKILL.md...
# e se a LLM desconfiar que precisa do assunto, ela importa esse arquivão para o contexto de graça!

def setup_mock_skills():
    """Cria uma pasta real de skills no HD para o agente ler."""
    os.makedirs("./skills/suporte_sql", exist_ok=True)
    
    content = """---
name: Database Exists
description: Como interagir com nosso banco de dados da empresa
---
# Diretrizes do Banco de Dados Corporativo
Você agora sabe como consultar dados. 
As Tabelas são: 'funcionarios(cpf, nome, salario)'.
Regra de ouro: Jamais dê 'DROP TABLE'. As consultas devem usar o 'LIMIT 10'.
    """
    
    with open("./skills/suporte_sql/SKILL.md", "w", encoding="utf-8") as f:
        f.write(content)
        
    print("[Sistema]: Pasta de Skills Dinâmicas criada no HD (`./skills/suporte_sql/SKILL.md`).")


def test_skills_progressive_disclosure():
    print("\n" + "="*50)
    print(" INICIANDO DEEP AGENTS COM SKILLS")
    print("="*50)
    
    if create_deep_agent is None:
        print("O pacote 'deepagents' não está instalado. Pulando execução prática.")
        return
        
    setup_mock_skills()
    
    # Iniciando a IA! 
    # Ao mapear o caminho das skills no arg 'skills=', 
    # o agente ganhará a Tool "import_skill" nativamente sem você programar nada!
    agent = create_deep_agent(
        model="openai:gpt-4o-mini",
        system_prompt="Você responde duvidas técnicas. Se precisar mexer em SQL, use a Skill correta antes de bolar respostas.",
        skills=["./skills/suporte_sql"] # <-- Progressão Dinâmica Automática!
    )
    
    question = "Quais as tabelas e regras que temos pra consultar funcionarios?"
    print(f"\n[Usuário]: {question}")
    
    print("\n[A IA invocará `import_skill` nos bastidores puxando o markdown...]")
    response = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": "skills_01"}}
    )
    
    print(f"\n[Deep Agent Skill-Loader]: \n{response['messages'][-1].content}\n")
    
    # Limpeza Limpeza (TearDown)
    shutil.rmtree("./skills", ignore_errors=True)

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: Variável de ambiente OPENAI_API_KEY ausente.")
    else:
        test_skills_progressive_disclosure()

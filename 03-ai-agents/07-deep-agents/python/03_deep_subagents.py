import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# Importando do DeepAgents (pip install deepagents)
try:
    from deepagents import create_deep_agent
except ImportError:
    create_deep_agent = None

load_dotenv()

# ==========================================
# 1. Recapitulando o passado (O Módulo 6)
# ==========================================
# Na pasta anterior de "Multi-Agentes", para você invocar 2 agêntes diferentes...
# Você teve que criar Agente 1, Agente 2...
# Assinar `@tool` pra embrulhar o Agente 1, `@tool` pro Agente 2.
# E injetar "tools=[call_ag1, call_ag2]" no Supervisor. ERA MUITO CÓDIGO BOILERPLATE!

# ==========================================
# 2. Deep Agents: Dicionários de Subagentes
# ==========================================
# O novo pacote isola essa lógica em um Dicionário padronizado (SubAgent dict)
# Ele cria o Tool Wrapper, herda o RuntimeState e o Cérebro nativamente, sem código massante!

@tool
def calculate_tax(value: float) -> str:
    """Calcula imposto de 10%"""
    return f"Valor original: {value}. Com a Taxa fica: {value * 1.10}"

def test_dict_subagents():
    print("\n" + "="*50)
    print(" INICIANDO DEEP AGENTS (Subagentes via Listas Dict)")
    print("="*50)
    
    if create_deep_agent is None:
        print("O pacote 'deepagents' não está instalado. Pulando execução prática.")
        return
        
    print("[Harness]: Em vez de 3 grafos paralelos criados à mão, delegamos a Lista de SubAgents...")
    print("[Harness]: O `create_deep_agent` gerará os workers nativamente em Threads filhas isoladas!")

    # Instanciando de forma fluida (O Supervisor central já será o próprio Deep Agent)
    agent = create_deep_agent(
        model="openai:gpt-4o",
        system_prompt="Você é Presidente de Finanças. Delegue as continhas para o Subagente de imposto (tax_calculator).",
        
        # O Mágico Atributo! Uma lista de dicionários obedecendo a interface `SubAgent`
        subagents=[
            {
                "name": "tax_calculator", # Nome vira o nome da Tool invocável pela LLM
                "description": "Calcula taxas da empresa", # Descrição da Tool
                "system_prompt": "Você é especialista em cálculo de Tributos Governamentais.",
                "tools": [calculate_tax], # As tools que só ELE terá acesso (contexto limpo)
                "model": "openai:gpt-4o-mini" # Se ele é só uma régua, usa o modelo mais barato!
            }
        ]
    )

    question = "Olha presidente.. meu faturamento foi de 150 dólares no PIX hoje. Quanto é com as deudas?"
    print(f"\n[Usuário]: {question}")
    
    response = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": "sub_dict_01"}}
    )
    
    # A Magia: Se você fosse rastrear usando o LangSmith, a "Thread" principal manteve a memória limpa,
    # enquanto uma Sub-Thread na branch ao lado gerou e chamou a tool do cálculo, retornando só
    # o Summary final esporádico.
    
    print(f"\n[Deep Coordenador Financeiro]: \n{response['messages'][-1].content}\n")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: Variável de ambiente OPENAI_API_KEY ausente.")
    else:
        test_dict_subagents()

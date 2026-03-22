import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.messages import HumanMessage
from langgraph.types import Command

load_dotenv()

# ==========================================
# 1. Por que usar Skills? (Progressive Disclosure)
# ==========================================
# Se você tiver 50 ferramentas (SQL, Web, Python, Jira), injetar 
# as descrições de TODAS elas no Prompt inicial da LLM vai explodir 
# o limite de tokens e deixá-la confusa.
# Solução: A LLM recebe apenas UMA ferramenta ("load_skill").
# Ao bater nessa tool, a LLM "descobre" a habilidade nova, altera seu prompt 
# localmente, e carrega ferramentas avançadas só sob demanda.

# Simulando um Banco de Dados de Prompts/Habilidades (Poderia vir de um BD)
SKILLS_REGISTRY = {
    "write_sql": "Você é um perito em PostgreSQL. Suas consultas são exatas. A tabela é 'users(id, name, clicks)'. Retorne apenas código.",
    "review_legal_doc": "Você é um Juiz de Direito rigoroso. Avalie os contratos e ache as vírgulas erradas."
}


# ==========================================
# 2. A Tool Dinâmica ("Discoverer")
# ==========================================
@tool
def load_skill(skill_name: str, runtime: ToolRuntime) -> str:
    """Busca uma habilidade e altera o estado do Agente para torná-lo em um especialista.
    Habilidades disponíveis:
    - write_sql: Para montar consultas complexas.
    - review_legal_doc: Para ler contratos.
    """
    
    # 1. Verifica se a skill existe
    if skill_name not in SKILLS_REGISTRY:
        return f"Erro. Skill '{skill_name}' não encontrada. Escolha uma da lista."
    
    print(f"\n[🔄 Tool] -> O Agente solicitou o donwload da habilidade: {skill_name}")
    
    new_prompt = SKILLS_REGISTRY[skill_name]
    
    # IMPORTANTE: No LangChain, alterar as dinâmicas do Agente costuma ser 
    # injetar uma mensagem com 'role=system' no histórico pra mudar as regras do jogo.
    
    # 2. Modificando o Estado (A LLM passa a agir como o Novo Especialista)
    return Command(
        update={
            "messages": [
                {"role": "system", "content": new_prompt},
                {"role": "tool", "content": f"A Habilidade de {skill_name} foi carregada. Você agora é este especialista. Proceda a resolver o pedido do usuário sob esta ótica.", "tool_call_id": runtime.tool_call_id}
            ]
        }
    )

# ==========================================
# 3. Agente "Folha em Branco"
# ==========================================
# Ele é leve, barato e rápido. Não sabe nada de SQL ou Leis. Sabe apenas invocar 'load_skill'
lite_agent = create_agent(
    model="gpt-4o-mini",
    tools=[load_skill],
    system_prompt="Você é um assistente de triagem. Para resolver tarefas, invoque `load_skill` para adquirir especialidades."
)

def test_skills_pattern():
    print("\n" + "="*50)
    print(" INICIANDO PADRÃO SKILLS (Progressive Disclosure)")
    print("="*50)
    
    # 1. Desafio Legal
    task1 = "Leia isto e diga o defeito legal do texto: 'O locatário devrá pagr todo mês.'"
    print(f"\n[Usuário]: {task1}")
    
    response1 = lite_agent.invoke(
        {"messages": [HumanMessage(content=task1)]}
    )
    print(f"\n[Agente Muta-Formas]: \n{response1['messages'][-1].content}\n")
    
    
    print("-" * 50)
    # 2. Desafio SQL (Numa nova call limpa)
    task2 = "Escreva uma query pegando os maiores clickers."
    print(f"\n[Usuário]: {task2}")
    
    response2 = lite_agent.invoke(
        {"messages": [HumanMessage(content=task2)]}
    )
    print(f"\n[Agente Muta-Formas]: \n{response2['messages'][-1].content}\n")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: Variável de ambiente OPENAI_API_KEY ausente.")
    else:
        test_skills_pattern()

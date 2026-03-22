from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def consultar_base_conhecimento(pergunta: str) -> str:
    """Consulta simulada à base interna de suporte."""
    return f"Resultado da busca interna para: {pergunta}"

@tool
def abrir_ticket(descricao: str) -> str:
    """Abre um ticket de suporte no JIRA."""
    return f"Ticket aberto no sistema JIRA com sucesso."

# ===============================================
# PROMPT CUSTOMIZADO DE SUMARIZAÇÃO (PORTUGUÊS)
# ===============================================
PROMPT_DE_RESUMO_PT = """<role>
Assistente de Extração de Contexto
</role>

<primary_objective>
Seu único objetivo é extrair o resumo mais relevante da longa conversa abaixo, estritamente em Português do Brasil.
</primary_objective>

<instructions>
Substitua o histórico por um panorama focado em não repetir ações passadas.
Estruture usando os seguintes cabeçalhos (se não houver dado, escreva "Nenhum"):

## OBJETIVO DA SESSÃO
Qual o problema que o usuário quer resolver?

## RESUMO TÉCNICO
Fatos levantados, decisões tomadas, ferramentas já utilizadas (ex: usuário já reiniciou o PC, erro 412 apareceu).

## PRÓXIMOS PASSOS
O que falta fazer?

Responda APENAS com o contexto extraído em Português.

<messages>
Mensagens para resumir:
{messages}
</messages>"""

def main():
    # ===============================================
    # 1. Configuração do Middleware
    # ===============================================
    summarizer = SummarizationMiddleware(
        model="gpt-4o-mini",      
        trigger=("messages", 6),  # GATILHO: Se tivermos 6 ou mais mensagens...
        keep=("messages", 2),     # REGRA: Segure as últimas 2, e esprema o resto num Resumo!
        summary_prompt=PROMPT_DE_RESUMO_PT
    )

    agent = create_agent(
        model="gpt-4o-mini",
        tools=[consultar_base_conhecimento, abrir_ticket],
        middleware=[summarizer]
    )

    # ===============================================
    # 2. Simulando um Histórico Longo Antigo
    # ===============================================
    # O limite é 6. Aqui temos exatamente 6.
    historia_antiga = [
        HumanMessage(content="Oi, minha VPN não conecta de jeito nenhum."),
        AIMessage(content="Olá! Posso tentar ajudar. Você já reiniciou o PC?"),
        HumanMessage(content="Já sim, reiniciei duas vezes e não foi."),
        AIMessage(content="Certo. Aparece algum código de erro no Cisco AnyConnect?"),
        HumanMessage(content="Aparece o erro 412: Authentication Failed."),
        AIMessage(content="Isso indica falha de credencial. Você mudou sua senha do AD ontem?"),
    ]

    print("📜 HISTÓRICO ORIGINAL (6 mensagens compridas de troubleshooting)")
    for msg in historia_antiga:
        print(f"   ► {msg.content}")

    # ===============================================
    # 3. Disparando uma NOVA mensagem (Gatilho da compressão)
    # ===============================================
    print("\n🚀 [AÇÃO REAL] O usuário envia uma nova mensagem (a Sétima Mensagem).")
    print("O Middleware percebe que passou do limite (6) e injeta o resumo automaticamente antes da LLM ler!\n")
    
    nova_mensagem = {"role": "user", "content": "Mudei minha senha do AD sim! Acho que quebrou. Pode abrir um ticket?"}
    historia_antiga.append(nova_mensagem)
    
    resposta = agent.invoke({"messages": historia_antiga})
    final_messages = resposta["messages"]

    # ===============================================
    # 4. Inspecionando o "Depois"
    # ===============================================
    print("="*70)
    print(f"✨ HISTÓRICO RESULTANTE (Total Comprimido: {len(final_messages)} mensagens)")
    print("="*70)
    
    for i, msg in enumerate(final_messages):
        # Em LangChain, type(msg).__name__ ajuda a sabermos quem falou
        role_type = type(msg).__name__
        
        # Formataremos bonito para você ver a mágica do Resumo:
        if role_type == "HumanMessage" and "Here is a summary" in msg.content:
            texto_traduzido = msg.content.replace("Here is a summary of the conversation to date:", "AQUI ESTÁ UM RESUMO GERADO PARA ALIVIAR A MEMÓRIA:")
            print(f"\n[{i}] 🗜️ RESUMO INJETADO PELO MIDDLEWARE:")
            print(f"    {texto_traduzido.strip()}")
            
        elif role_type == "HumanMessage":
            print(f"\n[{i}] 👤 VOCÊ (USER):")
            print(f"    {msg.content}")
            
        elif role_type == "AIMessage":
            print(f"\n[{i}] 🤖 AGENTE DE SUPORTE (AI):")
            # Pode ser texto ou ToolCall
            if msg.content:
                print(f"    {msg.content}")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"    [Decidiu usar a Ferramenta: {tc['name']} -> {tc['args']}]")
                    
        elif role_type == "ToolMessage":
            print(f"\n[{i}] 🛠️ SISTEMA INTERNO (Resultado da Tool - Invisível ao User):")
            print(f"    {msg.content}")


if __name__ == "__main__":
    main()
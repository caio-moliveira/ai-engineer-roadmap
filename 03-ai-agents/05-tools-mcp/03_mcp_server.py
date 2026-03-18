import sys
from fastmcp import FastMCP

mcp = FastMCP("Travel_MCP")

# --- 1. MCP TOOLS ---
@mcp.tool()
def create_itinerary(raw_info: str) -> str:
    """
    Recebe um texto bruto contendo a preferência de viagem e compõe um roteiro oficial estruturado.
    
    Args:
        raw_info: Texto descritivo do humano, por exemplo "5 dias em Paris focados em história e culinária."
    """

    return f"""
    [ITINERÁRIO ESTRUTURADO GERADO PELO SISTEMA DA AGÊNCIA]
    Contexto Capturado: {raw_info}
    
    Dia 1: Chegada, Check-in no hotel designado, Jantar de boas vindas leve.
    Dia 2: Visita a pontos turísticos fundamentais pelas redondezas.
    Dia 3: Imersão cultural matutina, Tarde livre para compras.
    Dia 4: Experiência gastronômica típica e atividades relaxantes.
    Dia 5: Checkout e partida.
    """

# --- 2. MCP RESOURCES ---
@mcp.resource("travel://info/international")
def get_international_travel_info() -> str:
    """Retorna dicas gerais essenciais e mandatórias de segurança para destinos internacionais."""
    return """
    INFORMAÇÕES OFICIAIS DE SEGURANÇA E VIAGENS INTERNACIONAIS:
    1. Sempre ande com uma cópia colorida do passaporte (deixe o original no cofre).
    2. Tenha atenção a batedores de carteira em capitais europeias turísticas.
    3. Confirme as coberturas do seguro viagem estendido antes de realizar esportes de aventura.
    4. Tenha os contatos da embaixada local no celular.
    """

# --- 3. MCP PROMPTS ---
@mcp.prompt()
def itinerary_planner(destination: str, days: str, profile: str) -> str:
    """
    Prompt corporativo que instrui a formatação completa combinando dados do usuário e regras da agência.
    """
    policy = get_international_travel_info()
    
    return f"""Você é o Especialista Chefe de Roteiros Internacionais da Agência.
Sua missão é criar o discurso de venda perfeito baseando-se no destino: {destination}.
A viagem vai durar {days} dias, perfil de viagem: {profile}.

Lembre-se SEMPRE de incluir as informações de segurança obrigatórias no final da sua fala,
que são diretrizes da empresa:
===
{policy}
===

Aja com entusiasmo, gere um roteiro incrível e certifique-se de listar as seguranças de forma gentil.
"""

if __name__ == "__main__":
    print("Iniciando Travel_MCP Server...")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nServidor MCP encerrado.")
        sys.exit(0)

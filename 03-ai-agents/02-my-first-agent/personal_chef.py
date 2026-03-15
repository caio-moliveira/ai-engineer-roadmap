from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pprint import pprint
from langchain_tavily import TavilySearch

load_dotenv()

tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)

class Recipe(BaseModel):
    nome: str = Field(description="Nome da receita")
    ingredientes: List[str] = Field(description="Lista de ingredientes principais")
    instrucoes: str = Field(description="Modo de preparo resumido")

class RecipeList(BaseModel):
    receitas: List[Recipe]

system_prompt = """
Você é um chef pessoal.
O usuário fornecerá uma lista de ingredientes que sobraram em casa.

Sua tarefa é:
1. Usar a ferramenta de busca na web quando necessário.
2. Encontrar receitas compatíveis com os ingredientes disponíveis.
3. Sugerir receitas simples e realistas.
4. Responder sempre no formato estruturado solicitado.

Se nem todos os ingredientes forem usados, tudo bem.
Priorize receitas fáceis e comuns.
"""

agent = create_agent(
    model="openai:gpt-5",  # ajuste para o modelo/provider que você tiver disponível
    tools=[tavily_search_tool],
    system_prompt=system_prompt,
    response_format=RecipeList
)

question = HumanMessage(
    content="Tenho frango, arroz, feijão e batata. O que posso fazer?"
)


for step in agent.stream(
    {"messages": question},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

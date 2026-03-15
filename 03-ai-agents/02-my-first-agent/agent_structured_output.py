from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel
from pprint import pprint

load_dotenv()

# Example 1: Agent with structured output

class CapitalInfo(BaseModel):
    nome: str
    populacao: int
    ponto_turistico: str
    economia: str

question = HumanMessage(content="Qual é a capital da França?")
agent_structured = create_agent(
    model="gpt-5-nano",
    system_prompt="Você é um expert em turismo. Responda com as informações sobre a capital solicitada.",
    response_format=CapitalInfo
)

response_structured = agent_structured.invoke(
    {"messages": [question]}
)

print("Output do Agente:")
capital_info = response_structured["structured_response"]
pprint(capital_info.model_dump())

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel
from pprint import pprint

load_dotenv()

# ---------------------------------------------------------
# Example 1: Agent WITHOUT structured output
# ---------------------------------------------------------
print("--- Example 1: Agent WITHOUT structured output ---")
agent_simple = create_agent(
    model="gpt-5-nano",
    system_prompt="You are a science fiction writer, create a capital city at the users request."
)

question = HumanMessage(content="What is the capital of Mars?")
response_simple = agent_simple.invoke(
    {"messages": [question]}
)

print("Standard Text Response:")
print(response_simple['messages'][-1].content)
print("\n")


# ---------------------------------------------------------
# Example 2: Agent WITH structured output
# ---------------------------------------------------------
print("--- Example 2: Agent WITH structured output ---")

class CapitalInfo(BaseModel):
    name: str
    location: str
    vibe: str
    economy: str

agent_structured = create_agent(
    model="gpt-5-nano",
    system_prompt="You are a science fiction writer, create a capital city at the users request.",
    response_format=CapitalInfo
)

response_structured = agent_structured.invoke(
    {"messages": [question]}
)

print("Structured Response Object (parsed automatically):")
capital_info = response_structured["structured_response"]
pprint(capital_info.dict())
print(f"\nExtracted fields: The city of {capital_info.name} is located at {capital_info.location}.")

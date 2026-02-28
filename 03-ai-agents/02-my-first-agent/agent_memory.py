from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# ---------------------------------------------------------
# Example 1: Agent WITHOUT memory
# ---------------------------------------------------------
print("--- Example 1: Agent WITHOUT memory ---")
agent_no_memory = create_agent(
    model="gpt-5-nano"
)

msg1 = HumanMessage(content="Hello, my name is Seán and my favourite colour is green.")
agent_no_memory.invoke({"messages": [msg1]})

msg2 = HumanMessage(content="What's my favourite colour?")
response_no_mem = agent_no_memory.invoke({"messages": [msg2]})

print("Response (No Memory):")
print(response_no_mem['messages'][-1].content) # The agent won't remember the color or name
print("\n")


# ---------------------------------------------------------
# Example 2: Agent WITH memory
# ---------------------------------------------------------
print("--- Example 2: Agent WITH memory ---")
agent_with_memory = create_agent(
    model="gpt-5-nano",
    checkpointer=InMemorySaver()
)

# A thread_id helps the checkpointer separate different conversational sessions
config = {"configurable": {"thread_id": "1"}}

# First interaction (Agent saves this to memory checkpointer)
agent_with_memory.invoke(
    {"messages": [msg1]},
    config
)

# Second interaction (Agent retrieves context from checkpointer)
response_with_mem = agent_with_memory.invoke(
    {"messages": [msg2]},
    config
)

print("Response (With Memory):")
print(response_with_mem['messages'][-1].content) # The agent will remember the color and name

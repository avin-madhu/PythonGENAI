import os
from typing import TypedDict, List, Annotated

import httpx
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver  # NEW: Persistence
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


# 1. TOOL DEFINITION
@tool
def add_tool(a: int, b: int) -> int:
    """Adds two numbers a and b and returns the result."""
    return a + b


tools = [add_tool]
tool_node = ToolNode(tools)

# 2. LLM SETUP
client = httpx.Client(verify=False)
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    http_client=client,
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)


# 3. STATE & NODES
class State(TypedDict):
    # 'add_messages' ensures we append to history rather than overwriting
    messages: Annotated[List[AnyMessage], add_messages]


def llm_node(state: State):
    # Concept: System Messages (gives the AI a 'personality' or 'rules')
    sys_msg = SystemMessage(content="You are a helpful math assistant. Always use tools for calculation.")

    # Prepend system message to the existing message list
    messages = [sys_msg] + state["messages"]

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# 4. GRAPH CONSTRUCTION
graph = StateGraph(State)

graph.add_node("llm_node", llm_node)
graph.add_node("tools", tool_node)

graph.set_entry_point("llm_node")

# Concept: Conditional Edge (The Logic Gate)
graph.add_conditional_edges(
    "llm_node",
    tools_condition,  # Built-in: checks if LLM wants tools or to stop
)

# Concept: The Cycle (Returning results to the LLM)
graph.add_edge("tools", "llm_node")

# 5. PERSISTENCE (Memory)
# This allows the agent to remember conversations across different sessions
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# 6. EXECUTION WITH STREAMING
if __name__ == "__main__":
    # Config is required for memory (thread_id identifies the specific user/chat)
    config = {"configurable": {"thread_id": "user_123"}}

    user_query = "Hi, my name is Gemini. What is 15 + 25?"
    initial_state = {"messages": [HumanMessage(content=user_query)]}

    print(f"--- Processing Query 1 ---")
    # Concept: Streaming (Seeing nodes finish in real-time)
    for event in app.stream(initial_state, config, stream_mode="values"):
        last_msg = event["messages"][-1]
        print(f"Node Update: {type(last_msg).__name__}")

    print(f"Final Response: {event['messages'][-1].content}")
    print("-" * 50)

    # Concept: Memory Verification
    user_query_2 = "What is my name and what was the previous answer?"
    print(f"--- Processing Query 2 (Memory Test) ---")

    # We don't need to pass the old messages; 'thread_id' pulls them from memory
    result_2 = app.invoke({"messages": [HumanMessage(content=user_query_2)]}, config)
    print(f"Response: {result_2['messages'][-1].content}")

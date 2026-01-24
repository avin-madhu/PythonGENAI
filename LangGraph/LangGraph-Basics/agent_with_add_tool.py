import os
from typing import TypedDict, List, Annotated

import httpx
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.constants import END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


@tool
def add_tool(a: int, b: int) -> int:
    """Adds a two numbers a and b and give the result"""
    return a + b


tools = [add_tool]
tool_node = ToolNode(tools)  # wrap all these tools in the tool node

client = httpx.Client(verify=False)

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    http_client=client,
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)


# this is the structure of the message that is being passed from node to node
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


def llm_node(state: State):
    message = state["messages"]
    response = llm_with_tools.invoke(message)
    return {"messages": [response]}


graph = StateGraph(State)

# making the graph
graph.add_node("llm_node", llm_node)
graph.add_node("tool_node", tool_node)

graph.set_entry_point("llm_node")

graph.add_conditional_edges(
    "llm_node",
    tools_condition,
    {"tools": "tool_node", END: END}
)

app = graph.compile()

if __name__ == "__main__":
    # Example 1: Agent uses the tool
    user_query = "What is the sum of 5 and 10?"
    initial_state = {"messages": [HumanMessage(content=user_query)]}
    result = app.invoke(initial_state)
    print(f"Query: {user_query}")
    print(f"Response: {result['messages'][-1].content}")
    print("-" * 50)

    # Example 2: Agent responds directly
    user_query_2 = "Hello, how are you?"
    initial_state_2 = {"messages": [HumanMessage(content=user_query_2)]}
    result_2 = app.invoke(initial_state_2)
    print(f"Query: {user_query_2}")
    print(f"Response: {result_2['messages'][-1].content}")
    print("-" * 50)

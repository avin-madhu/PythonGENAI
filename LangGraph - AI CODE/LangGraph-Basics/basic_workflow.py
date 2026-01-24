import operator
from typing import Annotated, List, TypedDict

from langchain_community.tools import ArxivQueryRun
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI  # Use your preferred LLM, e.g., OpenAI, Anthropic
from langgraph.graph import StateGraph, END

# Set environment variables for API keys (e.g., OPENAI_API_KEY)

# os.environ["OPENAI_API_KEY"] = "your_api_key"

# 1. Define the ArXiv Tool
# LangChain provides a built-in Arxiv tool
arxiv_tool = ArxivQueryRun()
tools = [arxiv_tool]


# 2. Define the Graph State
# The state is the information passed between nodes in the graph
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# 3. Define the LLM (must support tool calling/function calling)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
# Bind the tools to the LLM
llm_with_tools = llm.bind_tools(tools)


# 4. Define Nodes
def call_llm(state: AgentState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def call_tool(state: AgentState):
    last_message = state['messages'][-1]
    # Execute the tool calls
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_output = arxiv_tool.invoke(tool_call.args)  # Assuming only one tool for simplicity
        tool_messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call.id))
    return {"messages": tool_messages}


# 5. Define the Conditional Edge (Router)
def route_to_tool_or_end(state: AgentState):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "call_tool"
    else:
        return "end"


# 6. Build the Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("call_llm", call_llm)
workflow.add_node("call_tool", call_tool)

# Set the entry point
workflow.set_entry_point("call_llm")

# Add edges
workflow.add_conditional_edges(
    "call_llm",
    route_to_tool_or_end,
    {"call_tool": "call_tool", "end": END}
)
workflow.add_edge('call_tool', 'call_llm')

# Compile the graph
app = workflow.compile()

# Visualize the graph (optional, requires pygraphviz)
# from IPython.display import Image
# Image(app.get_graph().draw_mermaid_png())

# 7. Run the Agent
inputs = {"messages": [
    HumanMessage(content="Find me recent papers on LangGraph and AI agents and summarize the key findings.")]}

for output in app.stream(inputs):
    for key, value in output.items():
        print(f"Output from Node '{key}': {value}")
    print("\n---\n")

import os
from typing import Literal, TypedDict

import httpx
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.constants import END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

load_dotenv()

client = httpx.Client(verify=False)

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    http_client=client
)


# this is for the LLM, normallt we know the output of an LLm can be very messy right?
# so we do this to force the LLM to generate output only in the structure that I mentioned
# in this Route class, without this we can't do "decision.step" later in the code
class Route(BaseModel):
    step: Literal["poem", "joke"] = Field(description="routes to the necessary steps")


class State(TypedDict):
    input: str
    decision: str
    output: str


# forces the LLM to generate a specific structure type output ( according to my pydantic class )
router = llm.with_structured_output(Route)


def joke_node(state: State):
    """ tell a joke """
    print("Joke node is called!")
    response = llm.invoke("write a joke based on " + state["input"])
    return {"output": response.content}


def poem_node(state: State):
    """tell a poem"""
    print("poem node is called")
    response = llm.invoke("Write a poem based on " + state["input"])
    return {"output": response.content}


def router_node(state: State):
    """routes the node to the appropriate node based on input"""
    decision = router.invoke(
        [
            SystemMessage(content="Route to the nodes poem or joke based on the user request"),
            HumanMessage(content=state["input"])
        ]
    )
    return {"decision": decision.step}


def route_condition(state: State):
    if state["decision"] == "joke":
        return "joke_node"
    if state["decision"] == "poem":
        return "poem_node"
    return END


# build the graph
graph = StateGraph(State)
graph.add_node("joke_node", joke_node)
graph.add_node("poem_node", poem_node)
graph.add_node("router_node", router_node)

graph.set_entry_point("router_node")
graph.add_conditional_edges(
    "router_node",
    route_condition,
    {
        "joke_node": "joke_node",
        "poem_node": "poem_node",
        END: END
    }
)
app = graph.compile()

if __name__ == "__main__":
    input = {"input": "tell me a joke on bananas"}
    response = app.invoke(input)
    print(response["output"])

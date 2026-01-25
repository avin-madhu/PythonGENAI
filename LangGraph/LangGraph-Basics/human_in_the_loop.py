import os
from typing import Literal, TypedDict

import httpx
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver  # Added for HITL
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


class Route(BaseModel):
    step: Literal["poem", "joke"] = Field(description="routes to the necessary steps")


class State(TypedDict):
    input: str
    decision: str
    output: str


router = llm.with_structured_output(Route)


def joke_node(state: State):
    print("--- Executing Joke Node ---")
    response = llm.invoke("write a joke based on " + state["input"])
    return {"output": response.content}


def poem_node(state: State):
    print("--- Executing Poem Node ---")
    response = llm.invoke("Write a poem based on " + state["input"])
    return {"output": response.content}


def router_node(state: State):
    print("--- Router Node: Analyzing Input ---")
    decision = router.invoke([
        SystemMessage(content="Route to the nodes poem or joke based on the user request"),
        HumanMessage(content=state["input"])
    ])
    return {"decision": decision.step}


def route_condition(state: State):
    if state["decision"] == "joke":
        return "joke_node"
    if state["decision"] == "poem":
        return "poem_node"
    return END


# Build the graph
builder = StateGraph(State)
builder.add_node("joke_node", joke_node)
builder.add_node("poem_node", poem_node)
builder.add_node("router_node", router_node)

builder.set_entry_point("router_node")
builder.add_conditional_edges(
    "router_node",
    route_condition,
    {
        "joke_node": "joke_node",
        "poem_node": "poem_node",
        END: END
    }
)

# 1. ADDING HITL: Use MemorySaver and interrupt_before
memory = MemorySaver()
app = builder.compile(
    checkpointer=memory,
    interrupt_before=["joke_node", "poem_node"]  # we get a pause here lmao!
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    initial_input = {"input": "tell me a joke on bananas"}

    # 2. RUNNING THE AGENT
    # so when we call app.streams langgraph calls the nodes one by one
    print("Starting Agent...")
    for event in app.stream(initial_input, config, stream_mode="values"):
        print(f"Current Decision: {event.get('decision', 'None')}")

    # The graph is now PAUSED. It ran 'router_node' but hasn't entered 'joke_node'.
    snapshot = app.get_state(config)
    print(f"\n ⏸ PAUSED. The agent wants to go to: {snapshot.next}")

    # 3. HUMAN INTERVENTION
    feedback = input("Would you like to change the decision? (Type 'poem' to override, or press Enter to continue): ")

    if feedback.strip().lower() == "poem":
        # We manually update the state to steer the agent
        app.update_state(config, {"decision": "poem"})
        print("Decision manually overridden to 'poem'.")

    # 4. RESUME THE AGENT (PART 2)
    print("\nResuming Agent...")
    # Passing None resumes from where it left off
    for event in app.stream(None, config, stream_mode="values"):
        if "output" in event:
            print(f"\nFINAL OUTPUT: {event['output']}")

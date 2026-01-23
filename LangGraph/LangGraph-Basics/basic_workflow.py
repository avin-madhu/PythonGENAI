import random
from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    input: str
    result: str


def tour(state: State):
    print(state["input"] + " is going for a tour folks!")
    return state


# one node
def japan(state: State):
    return {"result": "I go to japan"}


# another node
def paris(state: State):
    return {"result": "I got to paris"}


# condition
def decide(state: State) -> Literal["japan", "paris"]:
    if random.random() > 0.5:
        return "japan"  # same as the name of the function/node
    else:
        return "paris"


# building the graph
workflow = StateGraph(State)
workflow.add_node("tour", tour)
workflow.add_node("japan", japan)
workflow.add_node("paris", paris)
workflow.add_edge(START, "tour")
workflow.add_conditional_edges("tour", decide)
workflow.add_edge("japan", END)
workflow.add_edge("paris", END)
app = workflow.compile()

inputs = {"input": "Avin"}
res = app.invoke(inputs)

print(res)

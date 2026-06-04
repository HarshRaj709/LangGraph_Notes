from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

# step 1: define the state
class QuadraticState(TypedDict):
    a: float
    b: float
    c: float
    equation: str
    discriminant: float
    result: str
    

#step 2: define the graph
graph = StateGraph(QuadraticState)

#step 4: define the noodes functions
def show_equation(state: QuadraticState):
    return {"equation": f"{state['a']}x^2 +{state['b']}x + {state['c']} = 0"}

def calculate_discriminant(state: QuadraticState):
    a = state["a"]
    b = state["b"]
    c = state["c"]
    discriminant = b**2 - 4*a*c
    return {"discriminant": discriminant}


#conditional node 1
def real_roots(state: QuadraticState):
    root1 = (-state["b"] + state["discriminant"]**0.5)/(2*state["a"])
    root2 = (-state["b"] - state["discriminant"]**0.5)/(2*state["a"])
    result = f'The roots are {root1} and {root2}'
    return {'result': result}

#conditional node 2
def repeated_roots(state: QuadraticState):
    root = (-state["b"])/(2*state["a"])
    result = f'Only repeating root is {root}'
    return {'result': result}

#conditional node 3
def no_real_roots(state: QuadraticState):
    result = f'No real roots'
    return {'result': result}


#main conditional node
def determine_roots(state: QuadraticState) -> Literal["real_roots", "repeated_roots", "no_real_roots"]:
    if state["discriminant"] > 0:
        return "real_roots"
    elif state["discriminant"] == 0:
        return "repeated_roots"
    else:
        return "no_real_roots"

#step 3: define the nodes
graph.add_node("show_equation", show_equation)
graph.add_node("calculate_discriminant", calculate_discriminant)
graph.add_node("determine_roots", determine_roots)
graph.add_node('real_roots', real_roots)
graph.add_node('repeated_roots', repeated_roots)
graph.add_node('no_real_roots', no_real_roots)

#step 5: Add Edges
graph.add_edge(START, "show_equation")
graph.add_edge("show_equation", "calculate_discriminant")

#conditional edges
graph.add_conditional_edges("calculate_discriminant", determine_roots)

graph.add_edge("real_roots", END)
graph.add_edge("repeated_roots", END)   
graph.add_edge("no_real_roots", END)
#step 6: compile graph
workflow = graph.compile()

#step 7: execute workflow
initial_state = { "a": 15, "b": 20, "c": 2}
result = workflow.invoke(initial_state)
print(result["equation"])
print(result["discriminant"])
print(result["result"])

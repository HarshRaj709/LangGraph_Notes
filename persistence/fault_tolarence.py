from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import time
from langgraph.checkpoint.memory import InMemorySaver


class CrashState(TypedDict):
    input:str
    step1:str
    step2:str
    step3:str


def step1(state: CrashState) -> dict:
    print("Step 1 done")
    return {"step1":"done", "input":state["input"]}

def step2(state: CrashState) -> dict:
    print("Step 2 hanging as long running task, you can manually interupt th flow")
    time.sleep(30)
    return {"step2":"done"}

def step3(state: CrashState) -> dict:
    print("step3 execute")
    return {"step3":"done"}

graph = StateGraph(CrashState)

graph.add_node("step1", step1)
graph.add_node("step2", step2)
graph.add_node("step3", step3)

graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)

memory = InMemorySaver()
workflow=graph.compile(checkpointer=memory)

config = {"configurable":{"thread_id":1}}

try:
  print("Running graph: please manually intrupt")
  result = workflow.invoke({"input":"start"}, config=config)
except KeyboardInterrupt:
  print("kernel manually interrupted")

print(workflow.get_state(config))

print(list(workflow.get_state_history(config)))

final_state = workflow.invoke(None, config=config)
print("\n final state", final_state)

print(workflow.get_state(config))

print(list(workflow.get_state_history(config)))
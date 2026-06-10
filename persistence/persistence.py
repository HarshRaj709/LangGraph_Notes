from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=3200,
)

class JokeState(TypedDict):
    topic: str
    joke : str
    explanation: str

graph = StateGraph(JokeState)

def generate_joke(state: JokeState) -> dict:
    topic = state["topic"]
    prompt = f"You are a comedian who can generate joke on any topic and now you need to create a joke on this topic {topic}"
    result = model.invoke(prompt).content
    return {"joke":result}

def explain(state: JokeState) -> dict:
    joke = state["joke"]
    prompt = f"You need to explain this joke {joke}, make sure it make completely sense"
    result=model.invoke(prompt).content
    return {"explanation": result}

graph.add_node("generate_joke", generate_joke)
graph.add_node("explain_node", explain)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "explain_node")
graph.add_edge("explain_node", END)

memory = InMemorySaver()

workflow = graph.compile(checkpointer=memory)  #added persistance

config = {"configurable": {"thread_id":1}}

initial_state = {"topic":"human race"}

result = workflow.invoke(initial_state, config=config)

print("topic: ",result["topic"])
print("joke: ",result["joke"])
print("explaination: ",result["explanation"])
print(end="\n")
print(workflow.get_state(config))
print("\n")
# print(list(workflow.get_state_history(config)))
for state in workflow.get_state_history(config):
    print(state.values)
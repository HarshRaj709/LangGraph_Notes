from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")


model = ChatOpenAI(
            model="deepseek/deepseek-chat-v3.1",
            openai_api_key=OPENROUTER_API_KEY,
            base_url=BASE_URL,
            streaming=True,
            temperature=0.5,
            max_tokens=550,
        )

# create a state
class LLMState(TypedDict):
    question: str
    answer: str

def llm_qa(state: LLMState) -> LLMState:
    # extract the question from state
    question = state['question']
    # form a prompt
    prompt = f'Answer the following question {question}'
    # ask that question to the LLM
    answer = model.invoke(prompt).content
    # update the answer in the state
    state['answer'] = answer
    return state

# create our graph
graph = StateGraph(LLMState)

# add nodes
graph.add_node('llm_qa', llm_qa)

# add edges
graph.add_edge(START, 'llm_qa')
graph.add_edge('llm_qa', END)

# compile
workflow = graph.compile()
# execute

intial_state = {'question': 'How far is moon from the earth?'}

final_state = workflow.invoke(intial_state)

print(final_state['answer'])


# model.invoke('How far is moon from the earth?').content

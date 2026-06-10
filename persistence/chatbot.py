from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")


#1. define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] #use add_messages as its recommeded to use for list of messages, it will automatically add the system and human messages together when we pass the list of messages to the model


# define checkpointer
checkpointer = MemorySaver()

#2. define graph
graph = StateGraph(ChatState)

#5. define model
chat_model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=800,
)

#4. define node function
def chat_node(state: ChatState) -> dict:
    #take user query
    query = state["messages"]

    #pass to llm
    response = chat_model.invoke(query)
    #response store state
    return {"messages": [response]} #append the response to the existing messages in the state

#3. define node
graph.add_node("chat_node", chat_node)

#6. define edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

#7. compile and run
workflow = graph.compile(checkpointer=checkpointer)     #added checkpointer Because you compiled with: LangGraph stores the state under: thread 1

#8. define initial state
# initial_state = {"messages": [HumanMessage(content="What is the capital of France?")]}
# result = workflow.invoke(initial_state)
# print(result["messages"][-1].content) 


thread_id = '1'
while True:
    user_message = input("type here: ")
    if user_message.strip().lower() == "exit":
        break
    
    config = {'configurable': {'thread_id': thread_id}}   #this is responsible to pas the old messages history
    response = workflow.invoke({"messages": [HumanMessage(content=user_message)]}, config=config) # The key thing to understand is that the LLM is not explicitly told "this is the last message". Instead, LangGraph and LangChain pass the entire conversation history to the model in the correct order, and chat models are trained to generate the next assistant response based on the latest message in that sequence.
    print("AI:", response["messages"][-1].content)

    # 11. How Does Model Know Which Message To Reply To?
    # Because chat models are trained on sequences:

    # Human
    # Assistant
    # Human
    # Assistant
    # Human
    # ???

    # The next expected token is always the next Assistant message.
    # The model naturally generates a reply to the last message in the sequence.
    # It doesn't search for "latest message" explicitly.
    # It simply continues the conversation.

    # print(workflow.get_state(config=config))   #to see the state of thread 1 at that time.
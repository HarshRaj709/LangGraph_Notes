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

#5. define model
chat_model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=800,
)


#1. define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] #use add_messages as its recommeded to use for list of messages, it will automatically add the system and human messages together when we pass the list of messages to the model


# define checkpointer
checkpointer = MemorySaver()

#2. define graph
graph = StateGraph(ChatState)

#4. define node function
def chat_node(state: ChatState) -> dict:
    query = state["messages"]
    response = chat_model.invoke(query)
    return {"messages": [response]} #append the response to the existing messages in the state

#3. define node
graph.add_node("chat_node", chat_node)
#6. define edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

#7. compile and run
chatbot = graph.compile(checkpointer=checkpointer)
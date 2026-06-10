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

chat_model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=800,
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] #use add_messages as its recommeded to use for list of messages, it will automatically add the system and human messages together when we pass the list of messages to the model

checkpointer = MemorySaver()

graph = StateGraph(ChatState)

def chat_node(state: ChatState) -> dict:
    query = state["messages"]
    response = chat_model.invoke(query)
    return {"messages": [response]}

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


chatbot = graph.compile(checkpointer=checkpointer)

for message_chunk, metadata in chatbot.stream(
    {"messages": [HumanMessage(content="What is the capital of uttar pradesh and bangal")]},
    config= {'configurable': {'thread_id': "thread_1"}},
    stream_mode = 'messages'
):

    # print(message_chunk) #content='The' additional_kwargs={} response_metadata={'model_provider': 'openai'} id='lc_run--019eafb8-c267-76f1-8596-01c6f4bbf332' tool_calls=[] invalid_tool_calls=[] tool_call_chunks=[]
    print(message_chunk.content, end=' ',flush=True )
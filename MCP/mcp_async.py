from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
import asyncio
import requests
import os
from dotenv import load_dotenv
import sqlite3

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

                                            #tools

@tool
def wheather_info(city:str) -> float:
    """Returns te temperature of city in celcius"""
    data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=9c6f1d7188a34532b8f134818261306&q={city}")
    wheather_data = data.json()
    return wheather_data["current"]["temp_c"]

llm_with_tools = chat_model.bind_tools([wheather_info])

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_graph():

    async def chat_node(state: ChatState):
        query = state["messages"]
        response = await llm_with_tools.ainvoke(query)
        return {"messages": [response]} #append the response to the existing messages in the state

    # tool Node
    tool_node = ToolNode([wheather_info])

    #2. define graph
    graph = StateGraph(ChatState)
    
    #3. define node
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)              # define node of tool

    #6. define edges
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)        #if tool then go to tool then chatbots otherwise END
    graph.add_edge("tools", "chat_node")
    # graph.add_edge("chat_node", END)

    #7. compile and run
    chatbot = graph.compile()

    return chatbot

async def main():
    chatbot = build_graph()

    response = await chatbot.ainvoke(
        {"messages":[HumanMessage(content="what is my name ?")]})
    print(response["messages"][-1].content)

if __name__=="__main__":
    asyncio.run(main())
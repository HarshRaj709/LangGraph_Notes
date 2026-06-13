from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
import requests
import os
from dotenv import load_dotenv

#mowifi9123@afterdo.com

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")


                                        # Tool call by langgraph


model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=800,
)


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]           # as this is able to store different type of messages like HumanMessage, AIMessage and ToolMessage

graph = StateGraph(State)


@tool
def wheather_info(city:str) -> float:
    """Returns te temperature of city in celcius"""
    data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=9c6f1d7188a34532b8f134818261306&q={city}")
    wheather_data = data.json()
    return wheather_data["current"]["temp_c"]

llm_with_tools = model.bind_tools([wheather_info])

def model_node(state: State) -> dict:
    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }

tool_node = ToolNode([wheather_info])

graph.add_node("chatbots", model_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatbots")
graph.add_conditional_edges("chatbots", tools_condition)

# def tools_condition(state):
#     last_message = state["messages"][-1]

#     if last_message.tool_calls:
#         return "tools"

#     return END

graph.add_edge("tools", "chatbots")

chatbot = graph.compile()

result = chatbot.invoke(
    {
        "messages": [
            HumanMessage(
                content="What is the current temperature of kanpur?"
            )
        ]
    }
)

print(result["messages"][-1].content)



########################################################################################################

                                # manual tool call 


# model = ChatOpenAI(
#     model="openai/gpt-4o-mini",
#     openai_api_key=OPENROUTER_API_KEY,
#     base_url=BASE_URL,
#     streaming=True,
#     temperature=0.5,
#     max_tokens=800,
# )

# class NormalState(TypedDict):
#     query: str
#     answer: str

# graph = StateGraph(NormalState)


# @tool
# def wheather_info(city:str) -> float:
#     """Returns te temperature of city in celcius"""
#     data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=9c6f1d7188a34532b8f134818261306&q={city}")
#     wheather_data = data.json()
#     return wheather_data["current"]["temp_c"]


# tool_node = ToolNode([wheather_info])

# llm_with_tool = model.bind_tools([wheather_info])

# def model_node(state: NormalState) -> dict:
#     query = state["query"]

#     # LLM generates tool call
#     ai_response = llm_with_tool.invoke(query)

#     # ToolNode executes the tool call
#     tool_result = tool_node.invoke(             #ye dekhti h AI message and agar usme tool cll h to krti h tool ko run
#         {"messages": [ai_response]}
#     )

#     state["answer"] = tool_result["messages"][0].content

#     return state


# # def model_node(state: NormalState)-> dict:
# #     query = state["query"]
# #     answer = llm_with_tool.invoke(query)
# #     state["answer"] = answer
# #     return state

# # wheather_info("lucknow")

# graph.add_node("model_node", model_node)

# graph.add_edge(START, "model_node")
# graph.add_edge("model_node", END)

# chatbot = graph.compile()

# result = chatbot.invoke(
#     {
#         "query": "what is the current temperature of lucknow"
#     }
# )

# print(result)




##########################################################################################################
                                        # Direct api call


# model = ChatOpenAI(
#     model="openai/gpt-4o-mini",
#     openai_api_key=OPENROUTER_API_KEY,
#     base_url=BASE_URL,
#     streaming=True,
#     temperature=0.5,
#     max_tokens=800,
# )

# class NormalState(TypedDict):
#     query: str
#     answer: str

# graph = StateGraph(NormalState)

# def wheather_info(city:str) -> float:
#     data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=9c6f1d7188a34532b8f134818261306&q={city}")
#     wheather_data = data.json()
#     return wheather_data["current"]["temp_c"]


# def wheather_node(state: NormalState)-> dict:
#     query = state["query"]
#     temperature = wheather_info(query)
#     state["answer"] = temperature
#     return state

# # wheather_info("lucknow")

# graph.add_node("wheather_info", wheather_node)

# graph.add_edge(START, "wheather_info")
# graph.add_edge("wheather_info", END)

# chatbot = graph.compile()

# result = chatbot.invoke(
#     {
#         "query": "lucknow"
#     }
# )

# print(result)
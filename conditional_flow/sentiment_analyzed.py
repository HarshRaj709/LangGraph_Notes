from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Literal
from langchain_openai import ChatOpenAI
import operator
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")

class SentimentSchema(BaseModel):
    sentiment: Literal["positive", "negative"] = Field(description="The sentiment of the review, either positive or negative.")

class DiagnosisSchema(BaseModel):
    issue_type: Literal["UX", "Performance", "Bug", "Support", "Other"] = Field(description='The category of issue mentioned in the review')
    tone: Literal["angry", "frustrated", "disappointed", "calm"] = Field(description='The emotional tone expressed by the user')
    urgency: Literal["low", "medium", "high"] = Field(description='How urgent or critical the issue appears to be')

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=3200,
)

structured_model = model.with_structured_output(SentimentSchema)
structured_diagnosis_model = model.with_structured_output(DiagnosisSchema)

class ReviewState(TypedDict):
    review: str
    sentiment: Literal["positive", "negative"]
    diagnosis: dict
    response: str

graph = StateGraph(ReviewState)


def analyze_sentiment(state: ReviewState) -> dict:
    prompt = f'For the following review find out the sentiment \n {state["review"]}'
    sentiment_result = structured_model.invoke(prompt)
    return {"sentiment": sentiment_result.sentiment}

def positive_response(state: ReviewState):

    prompt = f"""Write a warm thank-you message in response to this review:
            \n\n\"{state['review']}\"\n
            Also, kindly ask the user to leave feedback on our website.
        """
    
    response = model.invoke(prompt).content

    return {'response': response}

def diagnose_issue(state: ReviewState) -> dict:
    prompt = f"""Diagnose this negative review:\n\n{state['review']}\n"
        "Return issue_type, tone, and urgency.
        """
    diagnosis_result = structured_diagnosis_model.invoke(prompt)
    print(diagnosis_result)
    return {"diagnosis": diagnosis_result.model_dump()}

def negative_response(state: ReviewState):

    diagnosis = state['diagnosis']

    prompt = f"""You are a support assistant.
        The user had a '{diagnosis['issue_type']}' issue, sounded '{diagnosis['tone']}', and marked urgency as '{diagnosis['urgency']}'.
        Write an empathetic, helpful resolution message.
    """
    response = model.invoke(prompt).content

    return {'response': response}

def check_sentiment(state: ReviewState) -> Literal["diagnose_issue", "positive_response"]:
    if state["sentiment"] == "negative":
        return "diagnose_issue"
    else:
        return "positive_response"

#define nodes
graph.add_node("analyze_sentiment", analyze_sentiment)
graph.add_node("diagnose_issue", diagnose_issue)
graph.add_node("negative_response", negative_response)
graph.add_node("positive_response", positive_response)


#connect the nodes
graph.add_edge(START, "analyze_sentiment")

graph.add_conditional_edges("analyze_sentiment", check_sentiment)

graph.add_edge("diagnose_issue", "negative_response")
graph.add_edge("negative_response", END)
graph.add_edge("positive_response", END)


workflow = graph.compile()
initial_state = {"review": "The app is amazing and the customer support is excellent."}
result=workflow.invoke(initial_state)
print(result["sentiment"])
print(result["response"])
print(result.get("diagnosis"))
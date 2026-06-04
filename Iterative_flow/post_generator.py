from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")

generator_model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=800,
)

evaluator_model = ChatOpenAI(
    model="deepseek/deepseek-chat-v3.1",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0,
    max_tokens=800,
)

optimizer_llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    streaming=True,
    temperature=0.5,
    max_tokens=800,
)

#1
class PostGeneratorInput(TypedDict):
    topic: str
    tweet: str
    evaluation: Literal["approved", "needs_improvement"]
    feedback: str
    iteration: int
    max_iteration: int

    tweet_history: Annotated[list[str], operator.add]
    feedback_history: Annotated[list[str], operator.add]


class Evaluatorschema(BaseModel):
    evaluation: Literal["approved", "needs_improvement"] = Field(description="Whether the generated tweet is approved or needs improvement.")
    feedback: str = Field(description="Constructive feedback for improving the tweet if it needs improvement.") 

structured_evaluator_model = evaluator_model.with_structured_output(Evaluatorschema)

#2
graph = StateGraph(PostGeneratorInput)

#4
def generate_tweet(state:PostGeneratorInput) -> dict:
    messages = [
        SystemMessage(content="You are a funny and clever Twitter/X influencer."),
        HumanMessage(content=f"""
            Write a short, original, and hilarious tweet on the topic: "{state['topic']}".

            Rules:
            - Do NOT use question-answer format.
            - Max 280 characters.
            - Use observational humor, irony, sarcasm, or cultural references.
            - Think in meme logic, punchlines, or relatable takes.
            - Use simple, day to day english
            """)
        ]
    response = generator_model.invoke(messages).content
    return {"tweet": response, 'tweet_history': [response]}

def evaluate_tweet(state: PostGeneratorInput) -> dict:
    messages = [
        SystemMessage(content="You are a strict and discerning Twitter/X content moderator."),
        HumanMessage(content=f"""
            Evaluate the following tweet for humor, originality, and relevance to the topic "{state['topic']}":

            Tweet: "{state['tweet']}"

            Evaluation Criteria:
            - Humor: Is the tweet genuinely funny or clever?
            - Originality: Does it offer a unique take or perspective?
            - Relevance: Is it clearly related to the given topic?

            Auto-reject if:
            - It's written in question-answer format (e.g., "Why did..." or "What happens when...")
            - It exceeds 280 characters
            - It reads like a traditional setup-punchline joke
            - Dont end with generic, throwaway, or deflating lines that weaken the humor (e.g., “Masterpieces of the auntie-uncle universe” or vague summaries)
            
            ### Respond ONLY in structured format:
            - evaluation: "approved" or "needs_improvement"  
            - feedback: One paragraph explaining the strengths and weaknesses 
        """)
    ]
    evaluation_result = structured_evaluator_model.invoke(messages)
    return {"evaluation": evaluation_result.evaluation, "feedback": evaluation_result.feedback, 'feedback_history': [evaluation_result.feedback]}


def optimize_tweet(state: PostGeneratorInput) -> dict:

    messages = [
        SystemMessage(content="You punch up tweets for virality and humor based on given feedback."),
        HumanMessage(content=f"""
            Improve the tweet based on this feedback:
            "{state['feedback']}"

            Topic: "{state['topic']}"
            Original Tweet:
            {state['tweet']}

            Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 280 characters.
            """)
    ]

    response = optimizer_llm.invoke(messages).content
    iteration = state['iteration'] + 1

    return {'tweet': response, 'iteration': iteration, 'tweet_history': [response]}

def route_evaluation(state: PostGeneratorInput) -> Literal["approved", "needs_improvement"]:
    # if state['evaluation'] == 'approved' or state['iteration'] >= state['max_iteration']:
    #     return "approved"
    if state["iteration"] >= 3:
        return "approved"
    else:
        return "needs_improvement"

#3
graph.add_node("generate_tweet", generate_tweet)
graph.add_node("evaluate_tweet", evaluate_tweet)
graph.add_node("optimize_tweet", optimize_tweet)

#5
graph.add_edge(START, "generate_tweet")
graph.add_edge("generate_tweet", "evaluate_tweet")

graph.add_conditional_edges("evaluate_tweet", route_evaluation, {"approved": END, "needs_improvement": "optimize_tweet"})

graph.add_edge("optimize_tweet", "evaluate_tweet")

#6
workflow = graph.compile()

initial_state = {"topic": "giberish","iteration": 1,"max_iteration": 5}

#7
result = workflow.invoke(initial_state)

print("Topic:", result["topic"])
print("Generated Tweet:", result["tweet"])
print("Evaluation:", result["evaluation"])
print("Feedback:", result["feedback"])
print("Tweet History:", result["tweet_history"])
print("Feedback History:", result["feedback_history"])
print("Total Iterations:", result["iteration"])
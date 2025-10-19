from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)


class ChatState(TypedDict):
    chat_history: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state["chat_history"]
    response = llm.invoke(messages)
    return {"chat_history": [response]}


# Checkpoint saver
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)

# nodes
graph.add_node("chat", chat_node)

# edges
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)

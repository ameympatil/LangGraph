from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

# Tools

search_tool = DuckDuckGoSearchRun(region="us")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    A simple calculator tool that can perform basic arithmetic operations like addition,
    subtraction, multiplication, and division.
    """
    if operation == "addition" or operation == "add":
        return {"result": first_num + second_num}
    elif operation == "subtraction" or operation == "subtract":
        return {"result": first_num - second_num}
    elif operation == "multiplication" or operation == "multiply":
        return {"result": first_num * second_num}
    elif operation == "division" or operation == "divide":
        if second_num == 0:
            return {"error": "Division by zero is not allowed."}
        return {"result": first_num / second_num}
    else:
        return {
            "error": "Invalid operation. Please use add, subtract, multiply, or divide."
        }


@tool
def get_stock_price(ticker: str) -> dict:
    """
    A tool to get the current stock price of a given ticker symbol.
    eg: AAPL, GOOGL, MSFT, AMZN
    """
    # For demonstration purposes, we'll return a mock price.
    # In a real implementation, you would fetch the price from a financial API.
    mock_prices = {"AAPL": 150.25, "GOOGL": 2750.50, "MSFT": 299.00, "AMZN": 3400.75}
    price = mock_prices.get(ticker.upper(), None)
    if price is not None:
        return {"ticker": ticker.upper(), "price": price}
    else:
        return {"error": "Ticker symbol not found."}


tools = [search_tool, calculator, get_stock_price]
tool_node = ToolNode(tools=tools)
llm_with_tools = llm.bind_tools(tools)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Checkpoint saver
sqlite3_conn = sqlite3.connect("chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=sqlite3_conn)

graph = StateGraph(ChatState)

# nodes
graph.add_node("chat", chat_node)
graph.add_node("tools", tool_node)

# edges
graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)

CONFIG = {"configurable": {"thread_id": "test_thread1"}}


def retrive_all_thread_ids():
    all_threads = set()
    for i in checkpointer.list(None):
        all_threads.add(i.config["configurable"]["thread_id"])

    return list(all_threads)

import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

# Utility functions


def generate_thread_id():
    return uuid.uuid4()


def reset_chat():
    st.session_state["thread_id"] = generate_thread_id()
    add_thread_id(st.session_state["thread_id"])
    st.session_state["message_history"] = []


def add_thread_id(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    # Check if messages key exists in state values, return empty list if not
    messages = state.values.get("chat_history", [])
    return messages

def chat_thread_summarizer(messages):
    pass

# Initialize message history in session state if not present
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

add_thread_id(st.session_state["thread_id"])

# Adding Sidebar UI
st.sidebar.title("LangGraph ChatBot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("Conversation Histories")

for thread_id in st.session_state["chat_threads"][::-1]:
    
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role": role, "content": message.content})

        st.session_state["message_history"] = temp_messages

# Display previous conversation messages
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

# Get user input from chat box
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to history and display it
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

    # Stream assistant response using chatbot backend
    stream = chatbot.stream(
        {"chat_history": [HumanMessage(content=user_input)]},
        config=CONFIG,
        stream_mode="messages",
    )

    # Display assistant response in chat and collect the output
    with st.chat_message("assistant"):
        chatbot_response = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {"chat_history": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            )
        )
    # Add assistant response to message history
    st.session_state["message_history"].append(
        {"role": "assistant", "content": chatbot_response}
    )

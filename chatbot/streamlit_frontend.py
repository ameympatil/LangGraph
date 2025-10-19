import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

if "message_history" not in st.session_state:
    st.session_state['message_history'] = []


# Loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    chatbot_response = chatbot.invoke(
        {"chat_history": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": "default"}}
    )
        
        
    st.session_state['message_history'].append({"role": "assistant", "content": chatbot_response["chat_history"][-1].content})
    with st.chat_message("assistant"):
        st.markdown(chatbot_response["chat_history"][-1].content)
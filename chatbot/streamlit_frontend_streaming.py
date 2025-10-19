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
    
    stream = chatbot.stream(
        {"chat_history": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": "default"}},
        stream_mode="messages"
    )
        
    with st.chat_message('assistant'):
        chatbot_response = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
        {"chat_history": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": "default"}},
        stream_mode="messages"
    )
        )
    st.session_state['message_history'].append({"role": "assistant", "content": chatbot_response})
    
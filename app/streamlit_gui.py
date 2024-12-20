import streamlit as st
import random
import time
from llama_engine import llama_chat_gen_streamed

st.title("llm chat demo")

# Initialize chat histories in session state
if "all_chat_histories" not in st.session_state:
    st.session_state.all_chat_histories = {
        "Default Chat": [
            {"role": "system", "content": "You are a helpful chatbot who will assist the end user as best as possible."},
            {"role": "assistant", "content": "Hi there, how can I help you today?"}
        ]
    }

# Initialize current chat selection
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Default Chat"

# Sidebar for chat management
with st.sidebar:
    st.title("Chat Management")
    
    # Create new chat button
    if st.button("Create New Chat"):
        # Generate a unique name for the new chat
        new_chat_name = f"Chat {len(st.session_state.all_chat_histories) + 1}"
        st.session_state.all_chat_histories[new_chat_name] = [
            {"role": "system", "content": "You are a helpful chatbot who will assist the end user as best as possible."},
            {"role": "assistant", "content": "Hi there, how can I help you today?"}
        ]
        st.session_state.current_chat = new_chat_name

    # Dropdown to select current chat
    selected_chat = st.selectbox(
        "Select Chat",
        options=list(st.session_state.all_chat_histories.keys()),
        index=list(st.session_state.all_chat_histories.keys()).index(st.session_state.current_chat)
    )
    
    # Update current chat when selection changes
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    # Delete current chat button (prevent deleting the last chat)
    if len(st.session_state.all_chat_histories) > 1:
        if st.button("Delete Current Chat"):
            del st.session_state.all_chat_histories[st.session_state.current_chat]
            st.session_state.current_chat = list(st.session_state.all_chat_histories.keys())[0]
            st.rerun()

# Get current chat history
current_messages = st.session_state.all_chat_histories[st.session_state.current_chat]

# Display chat messages from history on app rerun
for message in current_messages:
    if message["role"] != "system":  # don't display system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    current_messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner('Responding...'):
            generated_response = llama_chat_gen_streamed(current_messages)
            response = st.write_stream(generated_response)
    
    # Add assistant response to chat history
    current_messages.append({"role": "assistant", "content": response})
    
    # Update the chat history in session state
    st.session_state.all_chat_histories[st.session_state.current_chat] = current_messages
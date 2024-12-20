import streamlit as st
import random
import time
from llama_engine import llama_chat_gen_streamed

st.title("llm chat demo")

# Initialize session state variables
if "all_chat_histories" not in st.session_state:
    st.session_state.all_chat_histories = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "new_chat_name" not in st.session_state:
    st.session_state.new_chat_name = ""

@st.dialog("Create a new chat history")
def create_new_chat_hist():
    name = st.text_input("Put your chat name here!")
    if st.button("Create"):
        if name:
            st.session_state.all_chat_histories[name] = [
                {"role": "system", "content": "You are a helpful chatbot who will assist the end user as best as possible."},
                {"role": "assistant", "content": "Hi there, how can I help you today?"} # make this more flexible??? allow for each new chat history to have a different input context?
            ]
            st.session_state.current_chat = name
            st.rerun()
        else:
            st.error("Please enter a name for your chat.")


# Initial chat creation dialog
if len(st.session_state.all_chat_histories) == 0:
    create_new_chat_hist()
# Sidebar with chat management in expander
with st.sidebar:
    with st.expander("Chat Management", expanded=True):
        if st.button("Create New Chat"):
            create_new_chat_hist()
        # Chat selection dropdown (only show if there are chats)
        if st.session_state.all_chat_histories:
            selected_chat = st.selectbox(
                "Select Chat",
                options=list(st.session_state.all_chat_histories.keys()),
                index=list(st.session_state.all_chat_histories.keys()).index(st.session_state.current_chat) if st.session_state.current_chat else 0
            )
            
            # Update current chat when selection changes
            if selected_chat != st.session_state.current_chat:
                st.session_state.current_chat = selected_chat
                st.rerun()

            # Delete current chat button (prevent deleting the last chat)
            if len(st.session_state.all_chat_histories) > 1:
                if st.button("Delete Current Chat"):
                    del st.session_state.all_chat_histories[st.session_state.current_chat]
                    st.session_state.current_chat = list(st.session_state.all_chat_histories.keys())[0] #defaults to earliest chat available
                    st.rerun()

# Main chat interface
if st.session_state.current_chat:
    current_messages = st.session_state.all_chat_histories[st.session_state.current_chat]

    # Display chat messages from history on app rerun
    for message in current_messages:
        if message["role"] != "system":  # don't display system messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Accept user input only if not currently generating a response
    if not st.session_state.is_generating:
        prompt = st.chat_input("What is up?")
        if prompt:
            # Add user message to chat history
            current_messages.append({"role": "user", "content": prompt}) #modify this to allow for RAG
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Set generating flag to True
            st.session_state.is_generating = True
            st.rerun()
    
    # Handle response generation
    if st.session_state.is_generating:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner('Responding...'):
                generated_response = llama_chat_gen_streamed(current_messages)
                response = st.write_stream(generated_response)
        
        # Add assistant response to chat history
        current_messages.append({"role": "assistant", "content": response})
        
        # Update the chat history in session state
        st.session_state.all_chat_histories[st.session_state.current_chat] = current_messages
        
        # Reset generating flag
        st.session_state.is_generating = False
        st.rerun()
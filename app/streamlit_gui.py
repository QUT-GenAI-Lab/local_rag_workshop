import streamlit as st
import random
import time
from llama_engine import llama_chat_gen_streamed
from RAG_backend import create_injection_prompt

st.title("llm chat demo")

#TEMPORARY DEV VAR
inject_template = """ 
Respond to the following message:

{USER_MESSAGE}.

Use the following example messages to base your response off of. Try to copy both the style and the substance of these examples:

{INJECT_TEXT}

"""

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
            init_messages = [
                {"role": "system", "content": "You are a helpful chatbot who will assist the end user as best as possible."},
                {"role": "assistant", "content": "Hi there, how can I help you today?"}
            ]
            st.session_state.all_chat_histories[name] = {
                'normal_hist': init_messages.copy(),
                'RAG_hist': init_messages.copy(),
            }
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
        
        if st.session_state.all_chat_histories:
            selected_chat = st.selectbox(
                "Select Chat",
                options=list(st.session_state.all_chat_histories.keys()),
                index=list(st.session_state.all_chat_histories.keys()).index(st.session_state.current_chat) if st.session_state.current_chat else 0
            )
            
            if selected_chat != st.session_state.current_chat:
                st.session_state.current_chat = selected_chat
                st.rerun()

            if len(st.session_state.all_chat_histories) > 1:
                if st.button("Delete Current Chat"):
                    del st.session_state.all_chat_histories[st.session_state.current_chat]
                    st.session_state.current_chat = list(st.session_state.all_chat_histories.keys())[0]
                    st.rerun()

# Display function for chat histories
def display_chat_hist(mode='normal_hist'):
    if st.session_state.current_chat:
        current_messages = st.session_state.all_chat_histories[st.session_state.current_chat][mode]
        for message in current_messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

# Main chat interface with tabs
normal_tab, rag_tab = st.tabs(["Default", "RAG history"])
with normal_tab:
    display_chat_hist('normal_hist')

with rag_tab:
    display_chat_hist('RAG_hist')

# Single chat input and response handling
if st.session_state.current_chat and not st.session_state.is_generating:
    prompt = st.chat_input("What is up?")
    if prompt:
        # Get both histories
        chat_histories = st.session_state.all_chat_histories[st.session_state.current_chat]
        
        # Create normal and RAG versions of the message
        normal_message = {"role": "user", "content": prompt}
        injection_prompt = create_injection_prompt( #### HAVE THIS DICTATED BY STUFF IN THE SIDEBAR!
            'wint_db', 
            prompt, 
            3, 
            max_dist=None, 
            inject_col=None, 
            inject_template=inject_template
        )
        rag_message = {"role": "user", "content": injection_prompt}
        
        # Add messages to respective histories
        chat_histories['normal_hist'].append(normal_message)
        chat_histories['RAG_hist'].append(rag_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.is_generating = True
        st.rerun()

if st.session_state.current_chat and st.session_state.is_generating:
    chat_histories = st.session_state.all_chat_histories[st.session_state.current_chat]
    
    # Generate response using RAG-enhanced prompt
    with st.chat_message("assistant"):
        with st.spinner('Responding...'):
            # Use RAG history for generation
            #NOTE - this could blow out memory quite quickly??? Be sure to change context length et cetera.
            generated_response = llama_chat_gen_streamed(chat_histories['RAG_hist']) 
            response = st.write_stream(generated_response)
    
    # Add response to both histories
    assistant_message = {"role": "assistant", "content": response}
    chat_histories['normal_hist'].append(assistant_message)
    chat_histories['RAG_hist'].append(assistant_message)
    
    st.session_state.is_generating = False
    st.rerun()
import streamlit as st
import random
import time
from llama_engine import llama_chat_gen_streamed

st.title("llm chat demo")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful chatbot who will assist the end user as best as possible."}, 
                                 {"role": "assistant", "content": "Hi there, how can I help you today?"}
                                ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system": # don't display system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        generated_response = llama_chat_gen_streamed(st.session_state.messages)
        response = st.write_stream(generated_response)
        # making this a stream with write_stream isn't that simple weirdly
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})